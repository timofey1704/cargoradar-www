from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models.post import Post
from core.redis.cache import cached
from core.repositories.search.feed import FeedItem, FeedRepository
from core.schemas.search.feed import (
    FeedItemRead,
    FeedPageRead,
    FeedPostRead,
    FeedRouteRead,
)
from executor.models.route import Route

DEFAULT_FEED_LIMIT = 20


def _feed_cache_key(
    _self: Any, *, skip: int = 0, limit: int = DEFAULT_FEED_LIMIT
) -> str:
    """У каждой страницы ленты (skip/limit) свой ключ кеша."""
    return f"search:feed:{skip}:{limit}"


class FeedService:
    """
    Сервис общей ленты поиска: маршруты водителей и посты СТО/поставщиков: 
    Route (создают водители) + Post (создают СТО и поставщики)."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = FeedRepository(db)

    @cached(ttl=settings.cache_ttl_search_feed, key=_feed_cache_key)
    async def get_feed(
        self, *, skip: int = 0, limit: int = DEFAULT_FEED_LIMIT
    ) -> FeedPageRead:
        """Страница ленты: элементы + total/has_more для пагинации (кешируем в Redis)."""
        items = await self.repository.get_feed(skip=skip, limit=limit)
        total = await self.repository.count_feed()
        return FeedPageRead(
            items=[self._to_read(item) for item in items],
            total=total,
            skip=skip,
            limit=limit,
            has_more=skip + len(items) < total,
        )

    @staticmethod
    def _to_read(item: FeedItem) -> FeedItemRead:
        """ORM-объект из репозитория превращаем в плоскую read-схему."""
        # isinstance вместо item.kind: так тип объекта сужается и не разъедется с kind
        route = (
            FeedRouteRead.model_validate(item.object)
            if isinstance(item.object, Route)
            else None
        )
        post = (
            FeedPostRead.model_validate(item.object)
            if isinstance(item.object, Post)
            else None
        )
        return FeedItemRead(
            kind=item.kind,
            id=item.id,
            created_at=item.created_at,
            route=route,
            post=post,
        )
