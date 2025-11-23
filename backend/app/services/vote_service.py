import json
import hashlib
from typing import Optional, List
from redis.asyncio import Redis

from app.models.poll import PollOption


class VoteService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def vote(
        self,
        poll_id: str,
        option_id: int,
        client_ip: str
    ) -> tuple[bool, Optional[str], List[PollOption], int]:
        """
        投票

        Returns:
            (success, error_message, updated_options, total_votes)
        """
        # 检查投票是否存在
        poll_exists = await self.redis.exists(f"poll:{poll_id}")
        if not poll_exists:
            return False, "投票不存在或已过期", [], 0

        # 检查选项是否存在
        options_key = f"poll:{poll_id}:options"
        option_exists = await self.redis.hexists(options_key, str(option_id))
        if not option_exists:
            return False, "无效的选项", [], 0

        # 检查IP是否已投票
        ip_hash = self._hash_ip(client_ip)
        vote_key = f"poll:{poll_id}:vote:{ip_hash}"
        already_voted = await self.redis.exists(vote_key)

        if already_voted:
            return False, "您已经投过票了", [], 0

        # 获取TTL用于设置IP记录的过期时间
        poll_ttl = await self.redis.ttl(f"poll:{poll_id}")
        if poll_ttl <= 0:
            return False, "投票已过期", [], 0

        # 使用Lua脚本执行原子操作
        lua_script = """
        local options_key = KEYS[1]
        local stats_key = KEYS[2]
        local vote_key = KEYS[3]
        local option_id = ARGV[1]
        local ttl = tonumber(ARGV[2])

        -- 增加选项投票数
        local option_json = redis.call('HGET', options_key, option_id)
        if not option_json then
            return {err = 'Invalid option'}
        end

        local option_data = cjson.decode(option_json)
        option_data.votes = option_data.votes + 1
        redis.call('HSET', options_key, option_id, cjson.encode(option_data))

        -- 增加总投票数
        redis.call('HINCRBY', stats_key, 'total_votes', 1)
        redis.call('HINCRBY', stats_key, 'unique_voters', 1)

        -- 记录IP投票
        redis.call('SETEX', vote_key, ttl, option_id)

        return {ok = true}
        """

        try:
            await self.redis.eval(
                lua_script,
                3,
                options_key,
                f"poll:{poll_id}:stats",
                vote_key,
                str(option_id),
                str(poll_ttl)
            )
        except Exception as e:
            return False, f"投票失败: {str(e)}", [], 0

        # 获取更新后的数据
        options_data = await self.redis.hgetall(options_key)
        stats_data = await self.redis.hgetall(f"poll:{poll_id}:stats")

        # 构造选项列表
        options = []
        for opt_id, option_json in sorted(
            options_data.items(),
            key=lambda x: int(x[0])
        ):
            option_dict = json.loads(option_json)
            options.append(PollOption(
                id=int(opt_id),
                text=option_dict["text"],
                votes=int(option_dict["votes"])
            ))

        total_votes = int(stats_data.get("total_votes", 0))

        return True, None, options, total_votes

    @staticmethod
    def _hash_ip(ip: str) -> str:
        """哈希IP地址（隐私保护）"""
        return hashlib.sha256(ip.encode()).hexdigest()[:16]
