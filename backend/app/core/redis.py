import redis.asyncio as redis
from typing import Optional
from .config import settings

# Redis连接池
redis_pool: Optional[redis.ConnectionPool] = None
redis_client: Optional[redis.Redis] = None


async def init_redis() -> None:
    """初始化Redis连接池"""
    global redis_pool, redis_client

    redis_pool = redis.ConnectionPool(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password if settings.redis_password else None,
        max_connections=50,
        decode_responses=True,
        socket_keepalive=True,
        health_check_interval=30
    )

    redis_client = redis.Redis(connection_pool=redis_pool)

    # 测试连接
    await redis_client.ping()
    print(f"✓ Redis connected: {settings.redis_host}:{settings.redis_port}")


async def close_redis() -> None:
    """关闭Redis连接"""
    global redis_pool, redis_client

    if redis_client:
        await redis_client.aclose()

    if redis_pool:
        await redis_pool.aclose()

    print("✓ Redis connection closed")


def get_redis() -> redis.Redis:
    """获取Redis客户端"""
    if redis_client is None:
        raise RuntimeError("Redis not initialized")
    return redis_client
