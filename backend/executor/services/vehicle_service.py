from sqlalchemy.ext.asyncio import AsyncSession

from executor.models.vehicles import Vehicle
from executor.repositories.vehicle import VehicleRepository
from executor.schemas.vehicle import VehicleCreate


class VehicleService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = VehicleRepository(db)

    async def create_many(self, executor_id: int, cars: list[VehicleCreate]) -> list[Vehicle]:
        return await self.repository.create_many(executor_id, cars)