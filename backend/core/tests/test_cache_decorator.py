"""Тесты декоратора @cached — реальный Redis не нужен (фейк)."""

import json

import pytest
from pydantic import BaseModel

from core.config import settings
from core.redis import cache as cache_module
from core.redis.cache import cache_key, cached

TTL = 60
KEY = "test:items"


class Item(BaseModel):
    id: int
    name: str


def make_loader():
    """Возвращает закешированный загрузчик и счётчик его вызовов."""
    calls: list[int] = []

    @cached(ttl=TTL, key=KEY)
    async def load_items() -> list[Item]:
        calls.append(1)
        return [Item(id=1, name="Первый"), Item(id=2, name="Второй")]

    return load_items, calls


async def test_first_call_fills_cache_and_second_uses_it(cache_client, fake_redis):
    load_items, calls = make_loader()

    first = await load_items()
    second = await load_items()

    assert len(calls) == 1, "второй вызов должен идти из кеша, без обращения к источнику"
    assert first == second
    assert fake_redis.ttl_of(cache_key(KEY)) == TTL
    assert json.loads(await fake_redis.get(cache_key(KEY))) == [
        {"id": 1, "name": "Первый"},
        {"id": 2, "name": "Второй"},
    ]


async def test_cache_returns_pydantic_models(cache_client):
    load_items, _ = make_loader()

    await load_items()
    from_cache = await load_items()

    assert isinstance(from_cache, list)
    assert all(isinstance(item, Item) for item in from_cache)
    assert [item.name for item in from_cache] == ["Первый", "Второй"]


async def test_cache_disabled_calls_source_every_time(cache_client, fake_redis, monkeypatch):
    monkeypatch.setattr(settings, "cache_enabled", False)
    load_items, calls = make_loader()

    await load_items()
    await load_items()

    assert len(calls) == 2
    assert fake_redis.store == {}


async def test_redis_error_falls_back_to_source(broken_redis_client, monkeypatch):
    monkeypatch.setattr(cache_module, "redis_client", broken_redis_client)
    load_items, calls = make_loader()

    result = await load_items()
    await load_items()

    assert len(calls) == 2, "без Redis каждый вызов идёт в источник"
    assert result == [Item(id=1, name="Первый"), Item(id=2, name="Второй")]


async def test_broken_cache_payload_is_ignored_and_rewritten(cache_client, fake_redis):
    fake_redis.store[cache_key(KEY)] = "not-a-json"
    load_items, calls = make_loader()

    result = await load_items()

    assert len(calls) == 1
    assert [item.name for item in result] == ["Первый", "Второй"]
    assert json.loads(await fake_redis.get(cache_key(KEY)))[0]["id"] == 1


async def test_outdated_cache_schema_is_ignored(cache_client, fake_redis):
    """Кеш со старой схемой ответа не должен ронять запрос."""
    fake_redis.store[cache_key(KEY)] = json.dumps({"items": [{"id": 1}]})
    load_items, calls = make_loader()

    result = await load_items()

    assert len(calls) == 1
    assert result == [Item(id=1, name="Первый"), Item(id=2, name="Второй")]


async def test_key_builder_makes_separate_entries(cache_client, fake_redis):
    calls: list[int] = []

    @cached(ttl=TTL, key=lambda user_id: f"user:{user_id}")
    async def load_user(user_id: int) -> Item:
        calls.append(user_id)
        return Item(id=user_id, name=f"user-{user_id}")

    first = await load_user(1)
    second = await load_user(2)
    cached_first = await load_user(1)

    assert calls == [1, 2]
    assert first == cached_first == Item(id=1, name="user-1")
    assert second == Item(id=2, name="user-2")
    assert await fake_redis.exists(cache_key("user:1"), cache_key("user:2")) == 2


async def test_invalidation_by_key_reloads_source(cache_client, fake_redis):
    load_items, calls = make_loader()
    await load_items()

    await cache_client.delete_cached_keys(cache_key(KEY))
    await load_items()

    assert len(calls) == 2


async def test_invalidation_by_prefix_reloads_source(cache_client):
    load_items, calls = make_loader()
    await load_items()

    assert await cache_client.delete_cached_by_prefix(settings.cache_prefix) == 1
    await load_items()

    assert len(calls) == 2


def test_cache_key_uses_configured_prefix(monkeypatch):
    monkeypatch.setattr(settings, "cache_prefix", "cr:")

    assert cache_key("main:faq") == "cr:main:faq"


def _sync_loader() -> list[Item]:
    """Синхронный загрузчик — декоратор такие не поддерживает (тест ниже)."""
    return []


async def _loader_without_annotation():
    """Загрузчик без аннотации возврата — декоратор такие не поддерживает."""
    return []


def test_sync_function_is_rejected():
    with pytest.raises(TypeError):
        cached(ttl=TTL, key=KEY)(_sync_loader)  # type: ignore[arg-type]


def test_function_without_return_annotation_is_rejected():
    with pytest.raises(TypeError):
        cached(ttl=TTL, key=KEY)(_loader_without_annotation)
