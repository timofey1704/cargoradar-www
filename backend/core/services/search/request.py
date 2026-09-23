from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from client.models.enums.request_statuses import CargoRequestStatus
from core.repositories.search.request import CargoRequestRepository
from core.schemas.search.request import CargoRequestPageRead, CargoRequestRead
from core.services.search.common import DEFAULT_PAGE_LIMIT, build_page, search_cached


class CargoRequestService:
    """Заявки клиентов: лента с фильтрами и заявки конкретного клиента."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = CargoRequestRepository(db)

    @search_cached("search:request:feed")
    async def get_feed(
        self,
        *,
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

        `total` не заполняем: COUNT в репозитории не учитывает фильтры по датам
        и радиусу, поэтому про следующую страницу говорит `has_more`.
        Кешируем по набору фильтров — разные фильтры дают разные ключи.
        """
        requests = await self.repository.get_feed(
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
        return build_page(
            [CargoRequestRead.model_validate(request) for request in requests],
            skip=skip,
            limit=limit,
        )

    @search_cached("search:request")
    async def get_by_client(
        self, client_id: int, *, skip: int = 0, limit: int = DEFAULT_PAGE_LIMIT
    ) -> CargoRequestPageRead:
        """Заявки конкретного клиента (кешируем в Redis)."""
        requests = await self.repository.get_by_client(
            client_id, skip=skip, limit=limit
        )
        return build_page(
            [CargoRequestRead.model_validate(request) for request in requests],
            skip=skip,
            limit=limit,
        )

