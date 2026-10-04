from sqlalchemy.ext.asyncio import AsyncSession

from client.models.request import CargoRequest
from core.models.post import Post
from core.repositories.search.feed import FeedItem, FeedRepository
from core.schemas.search.feed import FeedItemRead, FeedMapPointRead, FeedPageRead
from core.schemas.search.post import PostRead
from core.schemas.search.request import CargoRequestRead
from core.schemas.search.route import RouteRead
from core.services.search.common import DEFAULT_PAGE_LIMIT, search_cached
from executor.models.route import Route


class FeedService:
    """
    Сервис общей ленты поиска: маршруты водителей и посты СТО/поставщиков:
    Route (создают водители) + Post (создают СТО и поставщики)."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = FeedRepository(db)

    @search_cached("search:feed:v2")
    async def get_feed(
        self, *, skip: int = 0, limit: int = DEFAULT_PAGE_LIMIT
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
            RouteRead.model_validate(item.object)
            if isinstance(item.object, Route)
            else None
        )
        post = (
            PostRead.model_validate(item.object)
            if isinstance(item.object, Post)
            else None
        )
        request = (
            CargoRequestRead.model_validate(item.object)
            if isinstance(item.object, CargoRequest)
            else None
        )
        return FeedItemRead(
            kind=item.kind,
            id=item.id,
            created_at=item.created_at,
            route=route,
            post=post,
            request=request,
            map_points=[
                FeedMapPointRead(
                    label=point.label,
                    latitude=point.latitude,
                    longitude=point.longitude,
                )
                for point in item.map_points
            ],
        )
