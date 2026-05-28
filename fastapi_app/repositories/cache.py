import os
import redis
from typing import Protocol, Optional

class CacheProtocol(Protocol):
    def get_data(self, key: str) -> Optional[str]: ...
    def set_data(self, key: str, value: str, ttl: int) -> None: ...

class RedisCache:
    def __init__(self):
        self.client = redis.Redis(
            host=os.environ.get("REDIS_HOST", "redis"),
            port=int(os.environ.get("REDIS_PORT", 6379)),
            decode_responses=True
        )

    def get_data(self, key: str) -> Optional[str]:
        try:
            return self.client.get(key)
        except redis.ConnectionError:
            return None

    def set_data(self, key: str, value: str, ttl: int = 60) -> None:
        try:
            self.client.setex(key, ttl, value)
        except redis.ConnectionError:
            pass