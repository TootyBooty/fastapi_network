from pydantic import BaseSettings

import pytz
from datetime import tzinfo


class Settings(BaseSettings):
    # secret
    SECRET_KEY: str = 'secret_key'

    # database
    POSTGRES_URL: str = "postgresql+asyncpg://postgres:postgres@172.18.0.11:5432/fastapi_network"

    # jwt_auth
    TOKEN_URL: str = "api/v1/login/token"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = 'HS256'

    # time
    TIMEZONE: tzinfo = pytz.timezone('Europe/Moscow')

    # cache
    MEMCACHE_HOST: str = 'memcached'
    MEMCACHE_PORT: int = 11211
    DEFAULT_EXPTIME: int = 60

    class Config:
        env_file = ".env"


Config = Settings()
