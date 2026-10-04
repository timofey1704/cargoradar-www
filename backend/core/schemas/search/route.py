"""Read-схемы маршрутов водителей (Route)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from core.schemas.search.page import PageRead
from utils.address_formatter import FormattedAddress


class RouteRead(BaseModel):
    """Маршрут водителя. Геометрию (PostGIS) наружу не отдаём — она не нужна карточке."""

    id: int
    executor_id: int
    point_a: FormattedAddress
    point_b: FormattedAddress
    distance_km: float | None = None
    duration_min: int | None = None
    comment: str | None = None
    price: float | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


RoutePageRead = PageRead[RouteRead]

