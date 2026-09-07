from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from executor.models.vehicles import Vehicle
from executor.schemas.vehicle import VehicleCreate


class VehicleRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_executor_id(self, executor_id: int) -> list[Vehicle]:
        result = await self.db.scalars(
            select(Vehicle).where(Vehicle.executor_id == executor_id)
        )
        return list(result.all())

    async def create_many(self, executor_id: int, cars: list["VehicleCreate"]) -> list[Vehicle]:
        vehicles = [Vehicle(executor_id=executor_id, **car.model_dump()) for car in cars]
        self.db.add_all(vehicles)
        return vehicles