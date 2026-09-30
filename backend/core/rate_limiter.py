from __future__ import annotations

import hashlib
import math
from collections.abc import Awaitable, Callable

from fastapi import HTTPException, Request
from redis.asyncio import Redis
from redis.exceptions import RedisError

from core.security import decode_token
from core.redis.redis_client import redis_client


_RATE_LIMIT_SCRIPT = """
local key = KEYS[1]

local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local requested = tonumber(ARGV[3])
local redis_time = redis.call("TIME")
local now = tonumber(redis_time[1]) + tonumber(redis_time[2]) / 1000000

local data = redis.call("HMGET", key, "tokens", "timestamp")

local tokens = tonumber(data[1])
local timestamp = tonumber(data[2])

if tokens == nil then
    tokens = capacity
end

if timestamp == nil then
    timestamp = now
end

local elapsed = math.max(0, now - timestamp)

tokens = math.min(
    capacity,
    tokens + elapsed * refill_rate
)

local allowed = 0
local retry_after = 0

if tokens >= requested then
    tokens = tokens - requested
    allowed = 1
else
    retry_after = (requested - tokens) / refill_rate
end

redis.call(
    "HSET",
    key,
    "tokens",
    tokens,
    "timestamp",
    now
)

redis.call(
    "EXPIRE",
    key,
    math.ceil(capacity / refill_rate * 2)
)

return {
    allowed,
    tokens,
    retry_after
}
"""


class RateLimiter:
    def __init__(
        self,
        redis_client: Redis,
        *,
        prefix: str = "rate_limit",
    ) -> None:
        self.redis = redis_client
        self.prefix = prefix

    async def is_allowed(
        self,
        *,
        key: str,
        requests_per_second: float,
        burst: int,
    ) -> tuple[bool, float]:
        if requests_per_second <= 0:
            raise ValueError("requests_per_second must be greater than 0")
        if burst < 1:
            raise ValueError("burst must be greater than 0")

        result = await self.redis.eval(
            _RATE_LIMIT_SCRIPT,
            1,
            key,
            burst,
            requests_per_second,
            1,
        )

        allowed = bool(result[0])
        retry_after = float(result[2])

        return allowed, retry_after

    def build_key(
        self,
        *,
        scope: str,
        identifier: str,
    ) -> str:
        identifier_hash = hashlib.sha256(
            identifier.encode(),
        ).hexdigest()

        return f"{self.prefix}:{scope}:{identifier_hash}"

    @staticmethod
    def _get_identifier(request: Request) -> tuple[str, str]:
        authorization = request.headers.get("authorization", "")
        authorization_parts = authorization.split()
        if len(authorization_parts) == 2 and authorization_parts[0].lower() == "bearer":
            tokens = (authorization_parts[1],)
        else:
            tokens = tuple(
                token
                for cookie_name in ("client_access_token", "executor_access_token")
                if (token := request.cookies.get(cookie_name))
            )

        for token in tokens:
            payload = decode_token(token, is_refresh=False)
            if payload and payload.get("type") == "access":
                role = payload.get("role")
                subject = payload.get("sub")
                if role in {"client", "executor"} and isinstance(subject, str) and subject:
                    return subject, role

        client = request.client
        return (client.host if client else "unknown"), "ip"

    def limit(
        self,
        *,
        requests_per_second: float,
        burst: int,
        scope: str,
        fail_open: bool,
    ) -> Callable[[Request], Awaitable[None]]:
        if requests_per_second <= 0:
            raise ValueError("requests_per_second must be greater than 0")
        if burst < 1:
            raise ValueError("burst must be greater than 0")
        if not scope:
            raise ValueError("scope must not be empty")

        async def dependency(request: Request) -> None:
            identifier, identity_type = self._get_identifier(request)
            key = self.build_key(
                scope=scope,
                identifier=f"{identity_type}:{identifier}",
            )

            try:
                allowed, retry_after = await self.is_allowed(
                    key=key,
                    requests_per_second=requests_per_second,
                    burst=burst,
                )
            except RedisError as error:
                if fail_open:
                    return
                raise HTTPException(
                    status_code=503,
                    detail="Rate limiter unavailable",
                    headers={"Retry-After": "1"},
                ) from error

            if not allowed:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests",
                    headers={"Retry-After": str(max(1, math.ceil(retry_after)))},
                )

        return dependency


rate_limiter = RateLimiter(redis_client.redis)