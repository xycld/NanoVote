import ipaddress
from fastapi import APIRouter, HTTPException, Request
from typing import Annotated

from app.core.redis import get_redis
from app.models.poll import (
    CreatePollRequest,
    CreatePollResponse,
    PollResponse,
    VoteRequest,
    VoteResponse
)
from app.services import PollService, VoteService
from app.api.websocket import broadcast_vote_update

router = APIRouter(prefix="/api/polls", tags=["polls"])


def _pick_ip(ips):
    """在一组IP中优先选择IPv6，其次IPv4"""
    ipv6_list = []
    ipv4_list = []

    for raw_ip in ips:
        ip_str = raw_ip.strip()
        if not ip_str:
            continue

        # 处理形如 1.2.3.4:port 和 [2001:db8::1]:port 的情况
        if ip_str.startswith("[") and "]" in ip_str:
            ip_str = ip_str[1:ip_str.find("]")]
        elif ip_str.count(":") == 1 and "." in ip_str:
            ip_str = ip_str.rsplit(":", 1)[0]

        try:
            parsed = ipaddress.ip_address(ip_str)
        except ValueError:
            continue

        if parsed.version == 6:
            ipv6_list.append(str(parsed))
        else:
            ipv4_list.append(str(parsed))

    if ipv6_list:
        return ipv6_list[0]
    if ipv4_list:
        return ipv4_list[0]
    return ""


def get_client_ip(request: Request) -> str:
    """获取客户端真实IP，优先使用IPv6避免NAT导致的共享限制"""
    # X-Forwarded-For 可能包含多个IP，选IPv6优先
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = _pick_ip(forwarded.split(","))
        if ip:
            return ip

    # X-Real-IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        ip = _pick_ip([real_ip])
        if ip:
            return ip

    # 回退到 request.client.host
    fallback_ip = request.client.host if request.client else ""
    ip = _pick_ip([fallback_ip]) if fallback_ip else ""
    return ip or "unknown"


@router.post("", response_model=CreatePollResponse)
async def create_poll(data: CreatePollRequest, request: Request):
    """创建投票"""
    redis = get_redis()
    poll_service = PollService(redis)

    try:
        poll_id, expires_at = await poll_service.create_poll(
            title=data.title,
            options=data.options,
            duration=data.duration,
            allow_multiple=data.allow_multiple,
            min_selection=data.min_selection,
            max_selection=data.max_selection
        )

        return CreatePollResponse(
            poll_id=poll_id,
            url=f"/p/{poll_id}",
            expires_at=expires_at
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "CREATE_FAILED", "message": str(e)}
        )


@router.get("/{poll_id}", response_model=PollResponse)
async def get_poll(poll_id: str, request: Request):
    """获取投票详情"""
    redis = get_redis()
    poll_service = PollService(redis)
    client_ip = get_client_ip(request)

    poll = await poll_service.get_poll(poll_id, client_ip)

    if not poll:
        raise HTTPException(status_code=404, detail={"code": "POLL_NOT_FOUND"})

    return poll


@router.post("/{poll_id}/vote", response_model=VoteResponse)
async def vote(poll_id: str, data: VoteRequest, request: Request):
    """投票（支持单选和多选）"""
    redis = get_redis()
    vote_service = VoteService(redis)
    client_ip = get_client_ip(request)

    success, error_msg, options, total_votes = await vote_service.vote(
        poll_id=poll_id,
        option_id=data.option_id,
        option_ids=data.option_ids,
        client_ip=client_ip
    )

    if not success:
        raise HTTPException(status_code=400, detail=error_msg)

    # 广播实时更新（WebSocket）- 支持多选
    voted_option_ids = data.option_ids if data.option_ids else ([data.option_id] if data.option_id else [])
    for opt_id in voted_option_ids:
        voted_option = next((opt for opt in options if opt.id == opt_id), None)
        if voted_option:
            await broadcast_vote_update(
                poll_id=poll_id,
                option_id=opt_id,
                votes=voted_option.votes,
                total_votes=total_votes
            )

    return VoteResponse(
        success=True,
        options=options,
        total_votes=total_votes
    )
