from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union


class Settings(BaseSettings):
    # Redis配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # CORS配置
    # 开发环境：允许Vite开发服务器
    # 生产环境：通过nginx统一暴露，无需CORS（前后端同源）
    cors_origins: Union[str, List[str]] = "http://localhost:5173"

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            # 支持逗号分隔的字符串
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v

    # 业务配置
    max_poll_options: int = 20
    max_poll_title_length: int = 100
    max_option_text_length: int = 50

    # 持续时长配置（秒）
    duration_map: dict[str, int] = {
        "3m": 180,
        "30m": 1800,
        "1h": 3600,
        "6h": 21600,
        "1d": 86400,
        "3d": 259200,
        "7d": 604800,
        "10d": 864000
    }

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
