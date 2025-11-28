from fastapi import APIRouter, HTTPException, Request

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

    poll = await poll_service.get_poll(poll_id)

    if not poll:
        raise HTTPException(status_code=404, detail={"code": "POLL_NOT_FOUND"})

    return poll


@router.post("/{poll_id}/vote", response_model=VoteResponse)
async def vote(poll_id: str, data: VoteRequest, request: Request):
    """投票（支持单选和多选）

    注意：不进行服务端IP检测，投票限制由客户端本地存储实现
    """
    redis = get_redis()
    vote_service = VoteService(redis)

    success, error_msg, options, total_votes = await vote_service.vote(
        poll_id=poll_id,
        option_id=data.option_id,
        option_ids=data.option_ids
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
