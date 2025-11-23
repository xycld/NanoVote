import socketio
from typing import Dict, Set

# 创建Socket.IO服务器
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=False
)

# 存储房间（poll_id -> set of sids）
rooms: Dict[str, Set[str]] = {}


@sio.event
async def connect(sid: str, environ: dict, auth: dict):
    """客户端连接"""
    print(f"WebSocket connected: {sid}")
    await sio.emit('connected', {'sid': sid}, to=sid)


@sio.event
async def disconnect(sid: str):
    """客户端断开连接"""
    print(f"WebSocket disconnected: {sid}")

    # 从所有房间移除
    for poll_id, members in rooms.items():
        if sid in members:
            members.discard(sid)
            await sio.leave_room(sid, poll_id)


@sio.event
async def join_poll(sid: str, data: dict):
    """加入投票房间"""
    poll_id = data.get('poll_id')
    if not poll_id:
        return

    # 加入房间
    await sio.enter_room(sid, poll_id)

    if poll_id not in rooms:
        rooms[poll_id] = set()
    rooms[poll_id].add(sid)

    print(f"Client {sid} joined poll {poll_id}")
    print(f"Room {poll_id} members: {len(rooms[poll_id])}")


@sio.event
async def leave_poll(sid: str, data: dict):
    """离开投票房间"""
    poll_id = data.get('poll_id')
    if not poll_id:
        return

    # 离开房间
    await sio.leave_room(sid, poll_id)

    if poll_id in rooms:
        rooms[poll_id].discard(sid)

    print(f"Client {sid} left poll {poll_id}")


async def broadcast_vote_update(poll_id: str, option_id: int, votes: int, total_votes: int):
    """
    广播投票更新

    Args:
        poll_id: 投票ID
        option_id: 选项ID
        votes: 该选项的投票数
        total_votes: 总投票数
    """
    if poll_id in rooms and rooms[poll_id]:
        await sio.emit(
            'vote_update',
            {
                'option_id': option_id,
                'votes': votes,
                'total_votes': total_votes
            },
            room=poll_id
        )
        print(f"Broadcast to poll {poll_id}: option_{option_id} = {votes} votes")


async def broadcast_poll_expired(poll_id: str):
    """广播投票过期"""
    if poll_id in rooms and rooms[poll_id]:
        await sio.emit('poll_expired', room=poll_id)
        print(f"Poll {poll_id} expired notification sent")
