from pathlib import Path
from typing import TypedDict

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.repositories.subscription_repository import SubscriptionRepository
from core.schemas.membership_read import SubscriptionRead

from executor.models.executor import Executor
from executor.models.service import Service
from executor.models.supplier import Supplier
from executor.models.enums.executor_types import ExecutorTypes

from executor.schemas.executor_read import ExecutorRead, TowTruckExecutorRead, ServiceExecutorRead, SupplierExecutorRead, CarrierRead
from executor.schemas.service import ServiceRead
from executor.schemas.supplier import SupplierRead
from executor.schemas.vehicle import VehicleRead

from executor.repositories.executor import ExecutorRepository
from executor.repositories.vehicle import VehicleRepository

class _ExecutorBaseFields(TypedDict):
    id: int
    name: str
    email: str
    phone_number: str
    image_url: str | None
    is_notifications_enabled: bool
    is_active: bool
    subscription: SubscriptionRead | None

# директория для загруженного контента
UPLOAD_DIR = Path("uploads/executors/")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def get_executor(session: AsyncSession, executor_id: int) -> Executor:
    executor = await ExecutorRepository(session).get_by_id(executor_id)
    if not executor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Executor not found")
    return executor

async def build_executor_read(executor: Executor, db: AsyncSession) -> ExecutorRead:
    subscription_repo = SubscriptionRepository(db)
    active_subscription = await subscription_repo.get_active_for_executor(executor.id)

    base: _ExecutorBaseFields = {
        "id": executor.id,
        "name": executor.name,
        "email": executor.email,
        "phone_number": executor.phone_number,
        "image_url": executor.image_url,
        "is_notifications_enabled": executor.is_notifications_enabled,
        "is_active": executor.is_active,
        "subscription": SubscriptionRead.model_validate(active_subscription) if active_subscription else None,
    }

    match executor.type:
        case ExecutorTypes.carrier:
            vehicle_repo = VehicleRepository(db)
            cars = await vehicle_repo.get_by_executor_id(executor.id)
            return CarrierRead(**base, type=executor.type, cars=[VehicleRead.model_validate(c) for c in cars])

        case ExecutorTypes.service:
            service = await db.scalar(
                select(Service).where(Service.executor_id == executor.id).options(selectinload(Service.brands))
            )
            return ServiceExecutorRead(**base, type=executor.type, service=ServiceRead.model_validate(service))

        case ExecutorTypes.supplier:
            supplier = await db.scalar(
                select(Supplier).where(Supplier.executor_id == executor.id).options(selectinload(Supplier.brands))
            )
            return SupplierExecutorRead(**base, type=executor.type, supplier=SupplierRead.model_validate(supplier))

        case ExecutorTypes.towtruck:
            return TowTruckExecutorRead(**base, type=executor.type)