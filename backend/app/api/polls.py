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


def get_client_ip(request: Request) -> str:
    """获取客户端真实IP"""
    # 尝试从X-Forwarded-For头获取（如果使用代理）
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    # 尝试从X-Real-IP头获取
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # 默认使用request.client.host
    return request.client.host if request.client else "unknown"


@router.post("", response_model=CreatePollResponse)
async def create_poll(data: CreatePollRequest, request: Request):
    """创建投票"""
    redis = get_redis()
    poll_service = PollService(redis)

    try:
        poll_id, expires_at = await poll_service.create_poll(
            title=data.title,
            options=data.options,
            duration=data.duration
        )

        return CreatePollResponse(
            poll_id=poll_id,
            url=f"/p/{poll_id}",
            expires_at=expires_at
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.get("/{poll_id}", response_model=PollResponse)
async def get_poll(poll_id: str, request: Request):
    """获取投票详情"""
    redis = get_redis()
    poll_service = PollService(redis)
    client_ip = get_client_ip(request)

    poll = await poll_service.get_poll(poll_id, client_ip)

    if not poll:
        raise HTTPException(status_code=404, detail="投票不存在或已过期")

    return poll


@router.post("/{poll_id}/vote", response_model=VoteResponse)
async def vote(poll_id: str, data: VoteRequest, request: Request):
    """投票"""
    redis = get_redis()
    vote_service = VoteService(redis)
    client_ip = get_client_ip(request)

    success, error_msg, options, total_votes = await vote_service.vote(
        poll_id=poll_id,
        option_id=data.option_id,
        client_ip=client_ip
    )

    if not success:
        raise HTTPException(status_code=400, detail=error_msg)

    # 广播实时更新（WebSocket）
    voted_option = next((opt for opt in options if opt.id == data.option_id), None)
    if voted_option:
        await broadcast_vote_update(
            poll_id=poll_id,
            option_id=data.option_id,
            votes=voted_option.votes,
            total_votes=total_votes
        )

    return VoteResponse(
        success=True,
        options=options,
        total_votes=total_votes
    )
