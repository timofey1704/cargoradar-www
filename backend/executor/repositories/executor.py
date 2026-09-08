from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from executor.models.executor import Executor
from executor.models.service import Service, ServiceBrand
from executor.models.supplier import Supplier, SupplierBrand
from executor.models.enums.executor_types import ExecutorTypes
from executor.models.enums.car_brands import CarBrands
from executor.schemas.executor_update import ExecutorUpdate, SupplierUpdate, ServiceUpdate


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
        hashed_password: str | None,
        privacy_accepted: bool = True,
    ) -> Executor:
        executor = Executor(
            email=email,
            hashed_password=hashed_password,
            type=type,
            name=name,
            phone_number=phone_number,
            privacy_accepted=privacy_accepted,
        )
        self.db.add(executor)
        await self.db.flush()
        return executor

    async def change_account_data(
        self,
        executor_id: int,
        data: ExecutorUpdate,
    ) -> Executor:
        executor = await self.db.get(Executor, executor_id)
        if executor is None:
            raise ValueError(f"Executor {executor_id} not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(executor, field, value)

        await self.db.flush()
        return executor

    async def change_supplier_data(
        self,
        executor_id: int,
        data: SupplierUpdate,
    ) -> Supplier:
        supplier = await self.db.scalar(
            select(Supplier).where(Supplier.executor_id == executor_id).options(selectinload(Supplier.brands))
        )
        if supplier is None:
            raise ValueError(
                f"У исполнителя {executor_id} нет профиля поставщика для обновления"
            )

        update_data = data.model_dump(exclude_unset=True)
        brand_values = update_data.pop("brands", None)

        for field, value in update_data.items():
            setattr(supplier, field, value)

        if brand_values is not None:
            supplier.brands = [
                SupplierBrand(supplier_id=executor_id, brand=CarBrands(value)) for value in brand_values
            ]

        await self.db.flush()
        return supplier

    async def change_service_data(
        self,
        executor_id: int,
        data: ServiceUpdate,
    ) -> Service:
        service = await self.db.scalar(
            select(Service).where(Service.executor_id == executor_id).options(selectinload(Service.brands))
        )
        if service is None:
            raise ValueError(
                f"У исполнителя {executor_id} нет профиля СТО для обновления"
            )

        update_data = data.model_dump(exclude_unset=True)
        brand_values = update_data.pop("brands", None)

        for field, value in update_data.items():
            setattr(service, field, value)

        if brand_values is not None:
            service.brands = [
                ServiceBrand(service_id=executor_id, brand=CarBrands(value)) for value in brand_values
            ]

        await self.db.flush()
        return service