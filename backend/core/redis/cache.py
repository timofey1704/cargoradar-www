"""Кеширование результатов async-функций в Redis (JSON)."""

from collections.abc import Awaitable, Callable
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, TypeVar, get_type_hints

from pydantic import TypeAdapter, ValidationError

from core.config import settings
from core.redis.redis_client import redis_client

T = TypeVar("T")

KeyBuilder = Callable[..., str]


def cache_key(key: str) -> str:
    """Полный ключ кеша с общим префиксом: "main:faq" -> "cache:main:faq"."""
    return f"{settings.cache_prefix}{key}"


def cached(
    ttl: int,
    key: str | KeyBuilder,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Кеширует результат async-функции в Redis на ttl секунд.

    Тип ответа берётся из аннотации возврата, поэтому из кеша возвращаются
    те же объекты, что и без него (модели Pydantic, их списки и т.п.).

    Args:
        ttl: время жизни кеша в секундах
        key: статичный ключ ("main:faq") либо билдер, получающий те же аргументы,
            что и функция: lambda executor_id: f"executor:{executor_id}"

    Redis здесь ускоритель, а не источник правды:
    - любые ошибки Redis и битый/устаревший кеш молча игнорируются,
      функция просто выполняется как обычно;
    - отключить кеш целиком можно настройкой CACHE_ENABLED=false;
    - функции, вернувшие None, не кешируются.

    Инвалидация:
        await redis_client.delete_cached_keys(cache_key("main:faq"))
        await redis_client.delete_cached_by_prefix(settings.cache_prefix)
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        if not iscoroutinefunction(func):
            raise TypeError(f"@cached поддерживает только async-функции: {func.__qualname__}")

        return_type = get_type_hints(func).get("return")
        if return_type is None:
            raise TypeError(f"@cached нужна аннотация возврата: {func.__qualname__}")

        adapter = TypeAdapter(return_type)

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            if not settings.cache_enabled:
                return await func(*args, **kwargs)

            entry_key = cache_key(key(*args, **kwargs) if callable(key) else key)

            cached_value = await redis_client.get_cached_json(entry_key)
            if cached_value is not None:
                try:
                    return adapter.validate_python(cached_value)
                except ValidationError:
                    pass  # схема ответа поменялась — считаем кеш промахом

            result = await func(*args, **kwargs)
            await redis_client.set_cached_json(
                entry_key,
                adapter.dump_python(result, mode="json"),
                ttl,
            )
            return result

        return wrapper

    return decorator
