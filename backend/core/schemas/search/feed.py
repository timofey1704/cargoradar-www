"""Read-схемы общей ленты поиска: Route (водители) + Post (СТО/поставщики)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from core.models.enums.post_creator_type import PostCreatorType
from core.repositories.search.feed import FeedKind


class FeedRouteRead(BaseModel):
    """Маршрут водителя в ленте. Геометрию не отдаём — карточке нужны только точки и цена."""

    id: int
    executor_id: int
    point_a: str
    point_b: str
    distance_km: float | None = None
    duration_min: int | None = None
    comment: str | None = None
    price: float | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedPostRead(BaseModel):
    """Пост СТО, поставщика или водителя в ленте."""

    id: int
    creator_type: PostCreatorType
    client_id: int | None = None
    executor_id: int | None = None
    title: str
    request_text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedItemRead(BaseModel):
    """Элемент ленты: маршрут или пост — заполнено ровно одно из полей `route`/`post`."""

    kind: FeedKind
    id: int
    created_at: datetime

    route: FeedRouteRead | None = None
    post: FeedPostRead | None = None


class FeedPageRead(BaseModel):
    """Страница ленты: сами элементы и данные для пагинации на фронте."""

    items: list[FeedItemRead] = Field(default_factory=list)
    total: int
    skip: int
    limit: int
    has_more: bool
