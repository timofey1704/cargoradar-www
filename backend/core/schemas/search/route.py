"""Read-схемы маршрутов водителей (Route)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from core.schemas.search.page import PageRead


class RouteRead(BaseModel):
    """Маршрут водителя. Геометрию (PostGIS) наружу не отдаём — она не нужна карточке."""

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


RoutePageRead = PageRead[RouteRead]

