import json
from typing import Any, Optional
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.exceptions import CommerceException
from fastapi import status

class RedisManager:
    def __init__(self):
        self.client: Optional[aioredis.Redis] = None

    async def connect(self):
        """Initialize the async Redis connection."""
        self.client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    async def disconnect(self):
        """Close the Redis connection."""
        if self.client:
            await self.client.close()

redis_manager = RedisManager()

class CacheService:
    @staticmethod
    async def set(key: str, value: Any, expire: int = 3600):
        """Store a value in the cache with an expiration time."""
        if redis_manager.client:
            await redis_manager.client.set(key, json.dumps(value), ex=expire)

    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Retrieve a value from the cache."""
        if redis_manager.client:
            data = await redis_manager.client.get(key)
            return json.loads(data) if data else None
        return None

class RateLimiter:
    @staticmethod
    async def check_limit(key: str, limit: int, window: int):
        """
        Basic sliding window rate limiter.
        Raises an exception if the limit is exceeded.
        """
        if not redis_manager.client:
            return

        current_count = await redis_manager.client.incr(key)
        if current_count == 1:
            await redis_manager.client.expire(key, window)
            
        if current_count > limit:
            raise CommerceException(
                message="Rate limit exceeded. Please try again later.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )