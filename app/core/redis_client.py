from functools import lru_cache

import redis

from app.config import settings


@lru_cache
def get_redis_client():
    if settings.app_env == "test":
        import fakeredis

        return fakeredis.FakeStrictRedis(decode_responses=True)
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)
