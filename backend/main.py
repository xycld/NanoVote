import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core import settings, init_redis, close_redis
from app.api import polls_router
from app.api.websocket import sio


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("=" * 50)
    print("🚀 NanoVote Backend Starting...")
    print("=" * 50)

    # 初始化Redis
    await init_redis()

    yield

    # 关闭时
    print("=" * 50)
    print("👋 NanoVote Backend Shutting Down...")
    print("=" * 50)

    # 关闭Redis
    await close_redis()


# 创建FastAPI应用
app = FastAPI(
    title="NanoVote API",
    description="极简、快速、实时的投票系统",
    version="2.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(polls_router)

# 集成Socket.IO
socket_app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=app,
    socketio_path='/socket.io'
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "NanoVote API",
        "version": "2.0.0",
        "description": "极简、快速、实时的投票系统",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    from app.core.redis import get_redis

    try:
        redis = get_redis()
        await redis.ping()
        redis_status = "healthy"
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"

    return {
        "status": "ok",
        "redis": redis_status
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:socket_app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
