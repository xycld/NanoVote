import uuid
import time
import json
from typing import Optional, List
from redis.asyncio import Redis

from app.core.config import settings
from app.models.poll import PollOption, PollResponse


class PollService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def create_poll(
        self,
        title: str,
        options: List[str],
        duration: str,
        allow_multiple: bool = False,
        min_selection: Optional[int] = None,
        max_selection: Optional[int] = None
    ) -> tuple[str, int]:
        """
        创建投票

        Returns:
            (poll_id, expires_at)
        """
        # 生成投票ID
        poll_id = str(uuid.uuid4())[:8]

        # 计算过期时间
        ttl = settings.duration_map.get(duration, 86400)
        created_at = int(time.time())
        expires_at = created_at + ttl

        # 使用Pipeline批量操作
        pipe = self.redis.pipeline()

        # 1. 存储投票主体
        poll_key = f"poll:{poll_id}"
        poll_data = {
            "title": title,
            "created_at": created_at,
            "expires_at": expires_at,
            "duration": duration,
            "allow_multiple": str(allow_multiple)
        }

        # 添加多选配置（如果启用）
        if allow_multiple:
            if min_selection is not None:
                poll_data["min_selection"] = str(min_selection)
            if max_selection is not None:
                poll_data["max_selection"] = str(max_selection)

        pipe.hset(poll_key, mapping=poll_data)
        pipe.expire(poll_key, ttl)

        # 2. 存储选项
        options_key = f"poll:{poll_id}:options"
        for idx, option_text in enumerate(options, start=1):
            option_data = {
                "text": option_text,
                "votes": 0
            }
            pipe.hset(options_key, str(idx), json.dumps(option_data))
        pipe.expire(options_key, ttl)

        # 3. 初始化统计
        stats_key = f"poll:{poll_id}:stats"
        pipe.hset(stats_key, mapping={
            "total_votes": 0,
            "unique_voters": 0
        })
        pipe.expire(stats_key, ttl)

        await pipe.execute()

        return poll_id, expires_at

    async def get_poll(
        self,
        poll_id: str
    ) -> Optional[PollResponse]:
        """获取投票详情

        注意：不进行服务端IP检测，has_voted和voted_for由客户端本地存储管理
        """
        poll_key = f"poll:{poll_id}"

        # 检查投票是否存在
        exists = await self.redis.exists(poll_key)
        if not exists:
            return None

        # 获取投票数据
        poll_data = await self.redis.hgetall(poll_key)
        options_data = await self.redis.hgetall(f"poll:{poll_id}:options")
        stats_data = await self.redis.hgetall(f"poll:{poll_id}:stats")

        # 构造选项列表
        options = []
        for option_id, option_json in sorted(
            options_data.items(),
            key=lambda x: int(x[0])
        ):
            option_dict = json.loads(option_json)
            options.append(PollOption(
                id=int(option_id),
                text=option_dict["text"],
                votes=int(option_dict["votes"])
            ))

        # 解析多选配置
        allow_multiple = poll_data.get("allow_multiple", "False") == "True"
        min_selection = int(poll_data["min_selection"]) if "min_selection" in poll_data else None
        max_selection = int(poll_data["max_selection"]) if "max_selection" in poll_data else None

        return PollResponse(
            poll_id=poll_id,
            title=poll_data["title"],
            options=options,
            total_votes=int(stats_data.get("total_votes", 0)),
            expires_at=int(poll_data["expires_at"]),
            has_voted=False,  # 由客户端本地存储管理
            voted_for=None,  # 由客户端本地存储管理
            allow_multiple=allow_multiple,
            min_selection=min_selection,
            max_selection=max_selection
        )

    async def check_poll_exists(self, poll_id: str) -> bool:
        """检查投票是否存在"""
        return bool(await self.redis.exists(f"poll:{poll_id}"))
