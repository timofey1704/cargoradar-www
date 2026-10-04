"""Read-схемы заявок на перевозку (CargoRequest)."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from client.models.enums.request_statuses import CargoRequestStatus
from core.schemas.search.page import PageRead
from utils.address_formatter import FormattedAddress


class CargoRequestRead(BaseModel):
    """Заявка клиента на перевозку. Геометрия (PostGIS) наружу не отдаётся."""

    id: int
    client_id: int
    status: CargoRequestStatus

    origin_address: FormattedAddress
    destination_address: FormattedAddress

    cargo_type: str
    weight_kg: float
    volume_m3: float | None = None
    vehicle_type: str | None = None

    loading_date: date
    budget: float | None = None
    comment: str | None = None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


CargoRequestPageRead = PageRead[CargoRequestRead]

