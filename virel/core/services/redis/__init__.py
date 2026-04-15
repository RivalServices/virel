import logging
import redis.asyncio as aioredis

from ....core.config import Configuration

logger = logging.getLogger("virel.core.services.redis")


class RedisClient:
    """
    A client for interacting with a Redis database using redis-py's asyncio support.
    This class manages a Redis connection and provides convenience methods for
    common Redis operations such as get, set, delete, and exists.
    """

    def __init__(self):
        """
        Initializes the RedisClient instance by setting the client attribute
        to None. The actual Redis connection will be created when connect()
        is called.
        """

        self.client: aioredis.Redis | None = None

    async def connect(self):
        """
        Creates a connection to the Redis server using the URL specified in the
        configuration and verifies the connection by sending a PING command.
        """

        self.client = aioredis.from_url(
            Configuration.Core.redis_url,
            decode_responses=True,
        )
        await self.client.ping()
        logger.info("Connected to Redis")

    async def close(self):
        """
        Closes the connection to the Redis server if it exists and logs the closure.
        """

        if self.client:
            await self.client.close()
            logger.info("Closed Redis connection")

    async def get(self, key: str):
        """
        Retrieves the value associated with the given key from the Redis server.
        """

        if not self.client:
            raise RuntimeError("Redis client is not connected")

        return await self.client.get(key)

    async def set(self, key: str, value: str, *, ex: int | None = None):
        """
        Sets the value for the given key in the Redis server, optionally with an
        expiration time specified in seconds via the ex parameter.
        """
        if not self.client:
            raise RuntimeError("Redis client is not connected")

        return await self.client.set(key, value, ex=ex)

    async def delete(self, *keys: str):
        """
        Deletes the specified keys from the Redis server.
        """
        if not self.client:
            raise RuntimeError("Redis client is not connected")

        return await self.client.delete(*keys)

    async def exists(self, *keys: str):
        """
        Checks if the specified keys exist in the Redis server.
        """
        if not self.client:
            raise RuntimeError("Redis client is not connected")

        return await self.client.exists(*keys)
