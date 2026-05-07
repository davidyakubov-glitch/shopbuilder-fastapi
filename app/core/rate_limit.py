from fastapi import HTTPException, Request, status

from app.config import settings
from app.core.redis_client import get_redis_client


def _rate_limit_key(scope: str, identifier: str) -> str:
    return f"rate_limit:{scope}:{identifier}"


def enforce_rate_limit(scope: str, identifier: str, limit: int, window_seconds: int) -> None:
    redis_client = get_redis_client()
    key = _rate_limit_key(scope, identifier)
    attempts = redis_client.incr(key)
    if attempts == 1:
        redis_client.expire(key, window_seconds)
    if attempts > limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests. Try again later.")


def rate_limit_login(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    enforce_rate_limit("login", client_ip, settings.login_rate_limit_attempts, settings.login_rate_limit_window_seconds)


def rate_limit_register(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    enforce_rate_limit(
        "register",
        client_ip,
        settings.register_rate_limit_attempts,
        settings.register_rate_limit_window_seconds,
    )
