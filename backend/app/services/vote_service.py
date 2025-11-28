import json
from typing import Optional, List, Union, Dict, Any
from redis.asyncio import Redis
from redis.exceptions import ResponseError

from app.models.poll import PollOption


class VoteService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def vote(
        self,
        poll_id: str,
        option_id: Optional[int] = None,
        option_ids: Optional[List[int]] = None
    ) -> tuple[bool, Optional[Union[str, Dict[str, Any]]], List[PollOption], int]:
        """
        投票（支持单选和多选）

        注意：不进行服务端IP检测，投票限制由客户端本地存储实现

        Returns:
            (success, error_message, updated_options, total_votes)
        """
        # 确定投票的选项列表
        voting_options = []
        if option_ids is not None and len(option_ids) > 0:
            voting_options = option_ids
        elif option_id is not None:
            voting_options = [option_id]
        else:
            return False, {"code": "MISSING_OPTION"}, [], 0

        # 检查投票是否存在
        poll_key = f"poll:{poll_id}"
        poll_exists = await self.redis.exists(poll_key)
        if not poll_exists:
            return False, {"code": "POLL_NOT_FOUND"}, [], 0

        # 获取投票配置
        poll_data = await self.redis.hgetall(poll_key)
        allow_multiple = poll_data.get("allow_multiple", "False") == "True"
        min_selection = int(poll_data.get("min_selection", 1)) if "min_selection" in poll_data else None
        max_selection = int(poll_data.get("max_selection", 1)) if "max_selection" in poll_data else None

        # 验证多选配置
        if not allow_multiple and len(voting_options) > 1:
            return False, {"code": "MULTIPLE_NOT_ALLOWED"}, [], 0

        if allow_multiple:
            if min_selection is not None and len(voting_options) < min_selection:
                return False, {"code": "MIN_SELECTION", "count": min_selection}, [], 0
            if max_selection is not None and len(voting_options) > max_selection:
                return False, {"code": "MAX_SELECTION", "count": max_selection}, [], 0

        # 检查所有选项是否存在
        options_key = f"poll:{poll_id}:options"
        for opt_id in voting_options:
            option_exists = await self.redis.hexists(options_key, str(opt_id))
            if not option_exists:
                return False, {"code": "INVALID_OPTION", "option_id": opt_id}, [], 0

        # 获取TTL检查投票是否过期
        poll_ttl = await self.redis.ttl(f"poll:{poll_id}")
        if poll_ttl <= 0:
            return False, {"code": "POLL_EXPIRED"}, [], 0

        # 使用Lua脚本执行原子操作（支持多选）
        lua_script = """
        local options_key = KEYS[1]
        local stats_key = KEYS[2]
        local option_ids_json = ARGV[1]

        -- 解析选项ID列表
        local option_ids = cjson.decode(option_ids_json)

        -- 增加每个选项的投票数
        for _, option_id in ipairs(option_ids) do
            local option_json = redis.call('HGET', options_key, tostring(option_id))
            if not option_json then
                return redis.error_reply('INVALID_OPTION:' .. tostring(option_id))
            end

            local option_data = cjson.decode(option_json)
            option_data.votes = option_data.votes + 1
            redis.call('HSET', options_key, tostring(option_id), cjson.encode(option_data))
        end

        -- 增加总投票数（按选项数量）
        redis.call('HINCRBY', stats_key, 'total_votes', #option_ids)
        redis.call('HINCRBY', stats_key, 'unique_voters', 1)

        return 'OK'
        """

        try:
            await self.redis.eval(
                lua_script,
                2,
                options_key,
                f"poll:{poll_id}:stats",
                json.dumps(voting_options)
            )
        except ResponseError as e:
            message = str(e)

            if message.startswith("INVALID_OPTION:"):
                try:
                    invalid_id = int(message.split(":", 1)[1])
                except (ValueError, IndexError):
                    invalid_id = None
                return False, {"code": "INVALID_OPTION", "option_id": invalid_id}, [], 0

            return False, {"code": "VOTE_FAILED", "message": message}, [], 0
        except Exception as e:
            return False, {"code": "VOTE_FAILED", "message": str(e)}, [], 0

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
