from __future__ import annotations

from datetime import date
from typing import Sequence

from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_SetSRID
from sqlalchemy import func, select

from core.repositories.search.base import BaseRepository
from client.models.request import CargoRequest
from client.models.enums.request_statuses import CargoRequestStatus


class CargoRequestRepository(BaseRepository[CargoRequest]):
    """
    Репозиторий заявок (CargoRequest).
    Основной метод — get_feed: лента всех активных заявок с фильтрами
    (тип груза, транспорт, даты, радиус от точки).
    """

    model = CargoRequest

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
        limit: int = 20,
    ) -> Sequence[CargoRequest]:
        stmt = select(CargoRequest).where(CargoRequest.is_deleted.is_(False))

        if status is not None:
            stmt = stmt.where(CargoRequest.status == status)
        if cargo_type is not None:
            stmt = stmt.where(CargoRequest.cargo_type == cargo_type)
        if vehicle_type is not None:
            stmt = stmt.where(CargoRequest.vehicle_type == vehicle_type)
        if loading_date_from is not None:
            stmt = stmt.where(CargoRequest.loading_date >= loading_date_from)
        if loading_date_to is not None:
            stmt = stmt.where(CargoRequest.loading_date <= loading_date_to)

        if origin_lat is not None and origin_lon is not None and radius_km is not None:
            point = ST_SetSRID(ST_MakePoint(origin_lon, origin_lat), 4326)
            stmt = stmt.where(
                ST_DWithin(
                    CargoRequest.origin_location,
                    point,
                    radius_km * 1000,  # ST_DWithin с geography — метры
                    True,
                )
            )

        stmt = (
            stmt.order_by(CargoRequest.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_feed(
        self,
        *,
        status: CargoRequestStatus | None = CargoRequestStatus.NEW,
        cargo_type: str | None = None,
        vehicle_type: str | None = None,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(CargoRequest)
            .where(CargoRequest.is_deleted.is_(False))
        )
        if status is not None:
            stmt = stmt.where(CargoRequest.status == status)
        if cargo_type is not None:
            stmt = stmt.where(CargoRequest.cargo_type == cargo_type)
        if vehicle_type is not None:
            stmt = stmt.where(CargoRequest.vehicle_type == vehicle_type)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_by_client(
        self, client_id: int, *, skip: int = 0, limit: int = 20
    ) -> Sequence[CargoRequest]:
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

    async def update_status(
        self, request_id: int, status: CargoRequestStatus
    ) -> CargoRequest | None:
        obj = await self.get_by_id(request_id)
        if obj is None:
            return None
        obj.status = status
        await self.session.flush()
        return obj