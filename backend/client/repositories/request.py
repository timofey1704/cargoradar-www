from collections.abc import Sequence

from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2 import Geography
from geoalchemy2.elements import WKTElement

from client.models.request import CargoRequest, CargoRequestStatus
from client.schemas.request import (
    CargoRequestCreate,
    CargoRequestLocation,
    CargoRequestUpdate,
)
from executor.models.route import Route


def _to_point(location: CargoRequestLocation) -> WKTElement:
    """Точка для PostGIS: WKT в порядке (lng lat), SRID 4326 — как в колонках модели."""
    return WKTElement(f"POINT({location.longitude} {location.latitude})", srid=4326)


async def find_requests_near_route(
    session: AsyncSession,
    route_id: int,
    radius_meters: float,
) -> list[CargoRequest]:
    route = await session.get(Route, route_id)
    if route is None or route.path is None:
        return []

    # route.path — уже загруженный Python-объект (WKBElement), в SQL его не подставить,
    # поэтому берём геометрию пути скалярным подзапросом по колонке routes.path: так
    # не появляется cartesian product между routes и cargo_requests.
    route_path = (
        select(sa_func.cast(Route.path, Geography))
        .where(Route.id == route_id)
        .scalar_subquery()
    )

    stmt = select(CargoRequest).where(
        sa_func.ST_DWithin(
            sa_func.cast(CargoRequest.origin_location, Geography),
            route_path,
            radius_meters,
        ),
        CargoRequest.status == CargoRequestStatus.NEW,
        CargoRequest.is_deleted.is_(False),
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


class CargoRequestRepository:
    """Данные заявок клиента: создание, чтение, правка и мягкое удаление.

    Только готовит изменения и делает flush — транзакцию закрывает сервис
    (client.services.request_service.CargoRequestService).
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_owned(self, client_id: int, request_id: int) -> CargoRequest | None:
        """Заявка клиента; чужая или мягко удалённая — None.

        Владельца проверяем условием в SQL: не подсказываем существование
        чужих заявок и не тащим их объект в сессию.
        """
        stmt = select(CargoRequest).where(
            CargoRequest.id == request_id,
            CargoRequest.client_id == client_id,
            CargoRequest.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_client(
        self, client_id: int, *, skip: int = 0, limit: int = 20
    ) -> Sequence[CargoRequest]:
        """Заявки клиента, свежие сверху."""
        stmt = (
            select(CargoRequest)
            .where(
                CargoRequest.client_id == client_id,
                CargoRequest.is_deleted.is_(False),
            )
            .order_by(CargoRequest.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, client_id: int, data: CargoRequestCreate) -> CargoRequest:
        """Создать заявку клиента.

        Геометрию собираем из координат схемы: в колонки `Geometry` попадает
        WKT-точка (SRID 4326), а не WKBElement из запроса.
        """
        request = CargoRequest(
            client_id=client_id,
            origin_address=data.origin_address,
            origin_location=_to_point(data.origin_location),
            destination_address=data.destination_address,
            destination_location=_to_point(data.destination_location),
            cargo_type=data.cargo_type,
            weight_kg=data.weight_kg,
            volume_m3=data.volume_m3,
            vehicle_type=data.vehicle_type,
            loading_date=data.loading_date,
            budget=data.budget,
            comment=data.comment,
        )
        self.session.add(request)
        await self.session.flush()  # получаем id/status из server_default, коммитит сервис
        return request

    async def update(
        self, request: CargoRequest, data: CargoRequestUpdate
    ) -> CargoRequest:
        """Применить только переданные поля (exclude_unset), координаты → геометрия."""
        payload = data.model_dump(
            exclude_unset=True, exclude={"origin_location", "destination_location"}
        )
        if data.origin_location is not None:
            payload["origin_location"] = _to_point(data.origin_location)
        if data.destination_location is not None:
            payload["destination_location"] = _to_point(data.destination_location)

        # extra="forbid" в схеме гарантирует, что ключи — только колонки модели
        for field, value in payload.items():
            setattr(request, field, value)

        await self.session.flush()
        return request

    async def soft_delete(self, request: CargoRequest) -> CargoRequest:
        """Мягко удалить заявку: строка остаётся в БД, помечаем `is_deleted`."""
        request.is_deleted = True
        await self.session.flush()
        return request