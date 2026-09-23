"""Общее для сервисов поиска: размер страницы, кеширование и сборка ответа."""

from collections.abc import Awaitable, Callable, Sequence
from enum import Enum
from inspect import signature
from typing import Any, TypeVar

from core.config import settings
from core.redis.cache import cached
from core.schemas.search.page import PageRead

ItemT = TypeVar("ItemT")
ReturnT = TypeVar("ReturnT")

# размер страницы по умолчанию — как у репозиториев поиска
DEFAULT_PAGE_LIMIT = 20


def _format_param(value: Any) -> str:
    """Значение параметра для ключа кеша: у enum берём value («new», а не CargoRequestStatus.NEW)."""
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


def search_cached(
    prefix: str, ttl: int | None = None
) -> Callable[[Callable[..., Awaitable[ReturnT]]], Callable[..., Awaitable[ReturnT]]]:
    """`@cached` с ключом из фактических аргументов метода (позиционные — по имени).

    Своя обёртка нужна потому, что `@cached` получает аргументы как `*args, **kwargs`:
    без разбора сигнатуры позиционный `executor_id=7` не попал бы в ключ и разные
    исполнители делили бы одну страницу кеша.

    Параметры, которые не передали или оставили `None`, ключ не раздувают:
    `search_cached("search:route")` над `get_by_executor(7, limit=2)`
    -> "search:route:executor_id=7:limit=2".
    """

    def decorator(
        func: Callable[..., Awaitable[ReturnT]],
    ) -> Callable[..., Awaitable[ReturnT]]:
        func_signature = signature(func)

        def build_key(*args: Any, **kwargs: Any) -> str:
            bound = func_signature.bind_partial(*args, **kwargs)
            bound.apply_defaults()
            parts = [
                f"{name}={_format_param(value)}"
                for name, value in sorted(bound.arguments.items())
                if name != "self" and value is not None
            ]
            return ":".join([prefix, *parts])

        ttl_seconds = settings.cache_ttl_search if ttl is None else ttl
        return cached(ttl=ttl_seconds, key=build_key)(func)

    return decorator


def build_page(
    items: Sequence[ItemT], *, skip: int, limit: int, total: int | None = None
) -> PageRead[ItemT]:
    """Собирает страницу: `has_more` — «страница вернулась заполненной целиком»."""
    page: PageRead[ItemT] = PageRead(
        items=list(items),
        total=total,
        skip=skip,
        limit=limit,
        has_more=len(items) == limit,
    )
    return page

