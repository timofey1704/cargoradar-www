from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.executor import Executor
from executor.models.enums.executor_types import ExecutorTypes

class ExecutorRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, executor_id: int) -> Executor | None:
        result = await self.db.execute(select(Executor).where(Executor.id == executor_id))
        return result.scalar_one_or_none()

    async def get_by_phone_number(self, phone_number: str) -> Executor | None:
        result = await self.db.execute(select(Executor).where(Executor.phone_number == phone_number))
        return result.scalar_one_or_none()

    async def create(
        self,
        type: ExecutorTypes,
        name: str,
        email: str,
        phone_number: str,
        price_per_km: int | None,
        hashed_password: str,
       
    ) -> Executor:
        executor = Executor(
            email=email,
            hashed_password=hashed_password,
            type=type,
            name=name,
            phone_number=phone_number,
            price_per_km=price_per_km
        )
        self.db.add(executor)
        await self.db.commit()
        await self.db.refresh(executor)
        return executor