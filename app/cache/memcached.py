from typing import Optional
from aiomcache import Client
from core.config import Config


class MemcachedState:
    """Memcached state."""
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __del__(self):
        MemcachedState.__instance = None

    def __init__(self, connection: Optional[Client] = None) -> None:
        self._connection = connection

    @property
    def connection(self) -> Client | None:
        """Using current connection or creating new."""
        if not self._connection:
            self._connection = self._create_connection()
        return self._connection

    def _create_connection(self) -> Client:
        """Creating new connection."""
        return Client(Config.MEMCACHE_HOST, Config.MEMCACHE_PORT)

    async def set(self, key: str, value: Optional[str], exptime: int = Config.DEFAULT_EXPTIME) -> None:
        """Creating key-value."""
        await self.connection.set(f"{key}".encode(), f"{value}".encode(), exptime)

    async def get(self, key: str, default: Optional[str] = None):
        """Getting value by key."""
        data = await self.connection.get(f"{key}".encode())
        if data:
            return data.decode()
        return default


memcached_state = MemcachedState()
