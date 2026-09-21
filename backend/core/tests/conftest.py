"""Общие фикстуры для тестов core.

Тесты смс-логики (core/redis) не требуют запущенного Redis:
подключение подменяется на in-memory фейк (FakeAsyncRedis).
"""

from collections.abc import Callable, Coroutine
from typing import Any

import pytest

from core.redis.redis_client import RedisClient


class FakeAsyncRedis:
    """In-memory реализация команд Redis, которые использует смс-логика."""

    def __init__(self) -> None:
        self.store: dict[str, str] = {}
        self.expires: dict[str, int | None] = {}

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        self.store[key] = str(value)
        self.expires[key] = ex
        return True

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def exists(self, *keys: str) -> int:
        return sum(1 for key in keys if key in self.store)

    async def ttl(self, key: str) -> int:
        if key not in self.store:
            return -2
        return self.expires.get(key) or -1

    async def incr(self, key: str) -> int:
        self.store[key] = str(int(self.store.get(key, "0")) + 1)
        return int(self.store[key])

    async def delete(self, *keys: str) -> int:
        deleted = 0
        for key in keys:
            if self.store.pop(key, None) is not None:
                self.expires.pop(key, None)
                deleted += 1
        return deleted

    # helpers для ассертов в тестах
    def ttl_of(self, key: str) -> int | None:
        return self.expires.get(key)

    def contains(self, *keys: str) -> bool:
        return all(key in self.store for key in keys)


class BrokenAsyncRedis:
    """Redis, который всегда падает — проверяем graceful degradation."""

    def __getattr__(self, name: str) -> Callable[..., Coroutine[Any, Any, Any]]:
        async def _fail(*args: Any, **kwargs: Any) -> Any:
            raise ConnectionError("redis is down")

        return _fail


@pytest.fixture
def fake_redis() -> FakeAsyncRedis:
    """Чистый in-memory Redis на каждый тест."""
    return FakeAsyncRedis()


@pytest.fixture
def redis_client(fake_redis: FakeAsyncRedis) -> RedisClient:
    """RedisClient с подменённым подключением (реальный Redis не нужен)."""
    client = RedisClient()
    client.redis = fake_redis  # type: ignore[assignment]
    return client


@pytest.fixture
def broken_redis_client() -> RedisClient:
    """RedisClient с недоступным Redis — все команды падают."""
    client = RedisClient()
    client.redis = BrokenAsyncRedis()  # type: ignore[assignment]
    return client
