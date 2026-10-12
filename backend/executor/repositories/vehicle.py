from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from executor.models.vehicles import Vehicle
from executor.schemas.vehicle import VehicleCreate


class VehicleRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_executor_id(self, executor_id: int) -> list[Vehicle]:
        result = await self.db.scalars(
            select(Vehicle)
            .where(
                Vehicle.executor_id == executor_id,
                Vehicle.is_deleted.is_(False),
            )
            .order_by(Vehicle.id)
        )
        return list(result.all())

    async def get_active_by_id(self, executor_id: int, vehicle_id: int) -> Vehicle | None:
        return await self.db.scalar(
            select(Vehicle).where(
                Vehicle.id == vehicle_id,
                Vehicle.executor_id == executor_id,
                Vehicle.is_deleted.is_(False),
            )
        )

    async def update(self, vehicle: Vehicle, data: dict[str, object]) -> Vehicle:
        for field, value in data.items():
            setattr(vehicle, field, value)
        await self.db.flush()
        return vehicle

    async def soft_delete(self, vehicle: Vehicle) -> None:
        vehicle.is_deleted = True
        await self.db.flush()

    async def create_many(self, executor_id: int, cars: list["VehicleCreate"]) -> list[Vehicle]:
        vehicles = [Vehicle(executor_id=executor_id, **car.model_dump()) for car in cars]
        self.db.add_all(vehicles)
        return vehicles