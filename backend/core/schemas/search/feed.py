"""Read-схемы общей ленты поиска: Route (водители) + Post (СТО/поставщики)."""

from datetime import datetime

from pydantic import BaseModel, Field

from core.repositories.search.feed import FeedKind
from core.schemas.search.post import PostRead
from core.schemas.search.route import RouteRead


class FeedItemRead(BaseModel):
    """Элемент ленты: маршрут или пост — заполнено ровно одно из полей `route`/`post`."""

    kind: FeedKind
    id: int
    created_at: datetime

    route: RouteRead | None = None
    post: PostRead | None = None


class FeedPageRead(BaseModel):
    """Страница ленты: те же поля, что у PageRead, но `total` всегда известен (в ленте есть COUNT)."""

    items: list[FeedItemRead] = Field(default_factory=list)
    total: int
    skip: int
    limit: int
    has_more: bool

