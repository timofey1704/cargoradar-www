"""Тесты кеш-примитивов RedisClient — реальный Redis не нужен (фейк)."""

import json
from decimal import Decimal


async def test_set_and_get_cached_json(redis_client, fake_redis):
    assert await redis_client.set_cached_json("cache:test:key", {"a": 1}, ttl=60) is True

    assert await redis_client.get_cached_json("cache:test:key") == {"a": 1}
    assert fake_redis.ttl_of("cache:test:key") == 60


async def test_get_cached_json_returns_none_for_missing_key(redis_client):
    assert await redis_client.get_cached_json("cache:test:missing") is None


async def test_cached_json_keeps_nested_lists(redis_client):
    payload = [{"id": 1, "features": [{"id": 7, "name": "Геолокация"}]}]

    await redis_client.set_cached_json("cache:test:list", payload, ttl=30)

    assert await redis_client.get_cached_json("cache:test:list") == payload


async def test_set_cached_json_stores_non_json_values_as_strings(redis_client, fake_redis):
    """Decimal из тарифов и datetime не роняют запись в кеш."""
    await redis_client.set_cached_json("cache:test:decimal", {"price": Decimal("10.50")}, ttl=30)

    raw = await fake_redis.get("cache:test:decimal")

    assert json.loads(raw) == {"price": "10.50"}


async def test_get_cached_json_ignores_broken_payload(redis_client, fake_redis):
    fake_redis.store["cache:test:broken"] = "not-a-json"

    assert await redis_client.get_cached_json("cache:test:broken") is None


async def test_delete_cached_keys_invalidates_entry(redis_client):
    await redis_client.set_cached_json("cache:test:a", {"a": 1}, ttl=30)

    assert await redis_client.delete_cached_keys("cache:test:a") is True
    assert await redis_client.get_cached_json("cache:test:a") is None


async def test_delete_cached_keys_without_keys_is_ok(redis_client):
    assert await redis_client.delete_cached_keys() is True


async def test_delete_cached_by_prefix_deletes_only_matching(redis_client, fake_redis):
    await redis_client.set_cached_json("cache:main:faq", [1], ttl=30)
    await redis_client.set_cached_json("cache:main:other", [2], ttl=30)
    await redis_client.set_cached_json("cache:membership:plans", [3], ttl=30)

    deleted = await redis_client.delete_cached_by_prefix("cache:main:")

    assert deleted == 2
    assert await fake_redis.exists("cache:main:faq", "cache:main:other") == 0
    assert await fake_redis.exists("cache:membership:plans") == 1


async def test_delete_cached_by_prefix_returns_zero_when_nothing_matches(redis_client):
    assert await redis_client.delete_cached_by_prefix("cache:nothing:") == 0


async def test_cache_commands_are_safe_when_redis_is_down(broken_redis_client):
    """Кеш не должен ломать запрос: при недоступном Redis — безопасные дефолты."""
    assert await broken_redis_client.get_cached_json("cache:test:key") is None
    assert await broken_redis_client.set_cached_json("cache:test:key", {"a": 1}, ttl=30) is False
    assert await broken_redis_client.delete_cached_keys("cache:test:key") is False
    assert await broken_redis_client.delete_cached_by_prefix("cache:") == 0
