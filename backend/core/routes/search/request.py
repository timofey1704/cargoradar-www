"""Роуты поиска заявок на перевозку (CargoRequest)."""

from datetime import date

from fastapi import APIRouter, status

from client.models.enums.request_statuses import CargoRequestStatus
from core.dependencies import DbSession
from core.schemas.search.request import CargoRequestPageRead
from core.services.search.common import DEFAULT_PAGE_LIMIT
from core.services.search.request import CargoRequestService

router = APIRouter(prefix="/requests", tags=["search"])


@router.get("", response_model=CargoRequestPageRead, status_code=status.HTTP_200_OK)
async def get_requests_feed(
    db: DbSession,
    status: CargoRequestStatus | None = CargoRequestStatus.NEW,
    cargo_type: str | None = None,
    vehicle_type: str | None = None,
    loading_date_from: date | None = None,
    loading_date_to: date | None = None,
    origin_lat: float | None = None,
    origin_lon: float | None = None,
    radius_km: float | None = None,
    skip: int = 0,
    limit: int = DEFAULT_PAGE_LIMIT,
) -> CargoRequestPageRead:
    """Лента заявок: фильтры по грузу, датам погрузки и радиусу от точки.

    По умолчанию отдаём только новые заявки (`status=new`, как в репозитории).
    Радиус задаётся только вместе с точкой: `origin_lat` + `origin_lon` + `radius_km`,
    иначе 400.
    """
    service = CargoRequestService(db)
    return await service.get_feed(
        status=status,
        cargo_type=cargo_type,
        vehicle_type=vehicle_type,
        loading_date_from=loading_date_from,
        loading_date_to=loading_date_to,
        origin_lat=origin_lat,
        origin_lon=origin_lon,
        radius_km=radius_km,
        skip=skip,
        limit=limit,
    )

