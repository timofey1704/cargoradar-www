from sqlalchemy.ext.asyncio import AsyncSession

from executor.models.vehicles import Vehicle
from executor.repositories.vehicle import VehicleRepository
from executor.schemas.vehicle import VehicleCreate, VehicleUpdate


class VehicleService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = VehicleRepository(db)

    async def create_many(self, executor_id: int, cars: list[VehicleCreate]) -> list[Vehicle]:
        return await self.repository.create_many(executor_id, cars)

    async def get_active(self, executor_id: int, vehicle_id: int) -> Vehicle | None:
        return await self.repository.get_active_by_id(executor_id, vehicle_id)

    async def update(
        self,
        executor_id: int,
        vehicle_id: int,
        data: VehicleUpdate,
    ) -> Vehicle | None:
        vehicle = await self.repository.get_active_by_id(executor_id, vehicle_id)
        if vehicle is None:
            return None
        return await self.repository.update(vehicle, data.model_dump(exclude_unset=True))

    async def soft_delete(self, executor_id: int, vehicle_id: int) -> bool:
        vehicle = await self.repository.get_active_by_id(executor_id, vehicle_id)
        if vehicle is None:
            return False
        await self.repository.soft_delete(vehicle)
        return True