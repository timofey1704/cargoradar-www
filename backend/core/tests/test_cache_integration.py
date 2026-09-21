"""Интеграционные тесты кеша на реальном Redis.

Нужен запущенный Redis (например `docker compose up -d redis`).
Если Redis недоступен — тесты автоматически пропускаются.
"""

import pytest
from pydantic import BaseModel

from core.redis import cache as cache_module
from core.redis.cache import cache_key, cached

pytestmark = pytest.mark.integration

TTL = 60
KEY = "test:integration:items"
KEYS_PREFIX = "cache:test:integration"


class Item(BaseModel):
    id: int
    name: str


calls: list[int] = []


@cached(ttl=TTL, key=KEY)
async def load_items() -> list[Item]:
    calls.append(1)
    return [Item(id=1, name="Первый"), Item(id=2, name="Второй")]


@pytest.fixture
async def real_cache_client(real_redis_client, monkeypatch):
    """Реальный клиент, подключённый внутрь модуля кеша, с очисткой тестовых ключей."""
    monkeypatch.setattr(cache_module, "redis_client", real_redis_client)
    calls.clear()

    await real_redis_client.delete_cached_by_prefix(KEYS_PREFIX)
    yield real_redis_client
    await real_redis_client.delete_cached_by_prefix(KEYS_PREFIX)


async def test_cache_roundtrip_in_real_redis(real_cache_client):
    assert await real_cache_client.set_cached_json(cache_key(KEY), {"a": 1}, ttl=TTL) is True

    assert await real_cache_client.get_cached_json(cache_key(KEY)) == {"a": 1}
    assert 0 < await real_cache_client.redis.ttl(cache_key(KEY)) <= TTL

    assert await real_cache_client.delete_cached_keys(cache_key(KEY)) is True
    assert await real_cache_client.get_cached_json(cache_key(KEY)) is None


async def test_delete_by_prefix_in_real_redis(real_cache_client):
    await real_cache_client.set_cached_json(cache_key(f"{KEY}:1"), [1], ttl=TTL)
    await real_cache_client.set_cached_json(cache_key(f"{KEY}:2"), [2], ttl=TTL)
    await real_cache_client.set_cached_json(cache_key("test:integration:other"), [3], ttl=TTL)

    deleted = await real_cache_client.delete_cached_by_prefix(cache_key(KEY))

    assert deleted == 2
    assert await real_cache_client.get_cached_json(cache_key(f"{KEY}:1")) is None
    assert await real_cache_client.get_cached_json(cache_key("test:integration:other")) == [3]


async def test_decorator_uses_real_redis(real_cache_client):
    first = await load_items()
    second = await load_items()

    assert len(calls) == 1, "второй вызов идёт из реального Redis"
    assert first == second == [Item(id=1, name="Первый"), Item(id=2, name="Второй")]
    assert isinstance(second[0], Item)


async def test_decorator_reloads_after_invalidation_in_real_redis(real_cache_client):
    await load_items()

    await real_cache_client.delete_cached_keys(cache_key(KEY))
    await load_items()

    assert len(calls) == 2
