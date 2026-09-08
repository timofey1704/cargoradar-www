from pathlib import Path
from typing import TypedDict

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from core.repositories.subscription_repository import SubscriptionRepository
from core.schemas.membership_read import SubscriptionRead

from executor.models.executor import Executor
from executor.models.service import Service
from executor.models.supplier import Supplier
from executor.models.enums.executor_types import ExecutorTypes

from executor.schemas.executor_read import (
    ExecutorRead,
    TowTruckExecutorRead,
    ServiceExecutorRead,
    SupplierExecutorRead,
    CarrierRead,
)
from executor.schemas.executor_update import ExecutorUpdate, SupplierUpdate, ServiceUpdate
from executor.schemas.service import ServiceRead
from executor.schemas.supplier import SupplierRead
from executor.schemas.vehicle import VehicleRead

from executor.repositories.executor import ExecutorRepository
from executor.repositories.vehicle import VehicleRepository

from executor.exceptions import (
    ExecutorError,
    ExecutorNotFoundError,
    ExecutorTypeMismatchError,
    DuplicateFieldError,
)


class _ExecutorBaseFields(TypedDict):
    id: int
    name: str
    email: str
    phone_number: str
    image_url: str | None
    is_notifications_enabled: bool
    is_active: bool
    subscription: SubscriptionRead | None


UPLOAD_DIR = Path("uploads/executors/")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


_UNIQUE_CONSTRAINT_FIELD_MAP = {
    "executors_email_key": "email",
    "executors_phone_number_key": "phone_number",
    "suppliers_unp_key": "unp",
    "services_unp_key": "unp",
}


class ExecutorService:
    def __init__(self, db: AsyncSession, executor_repo: ExecutorRepository) -> None:
        self.db = db
        self.executor_repo = executor_repo

    async def get_executor(self, executor_id: int) -> Executor:
        executor = await self.executor_repo.get_by_id(executor_id)
        if executor is None:
            raise ExecutorNotFoundError(executor_id)
        return executor

    async def update_profile(
        self,
        executor: Executor,
        executor_data: ExecutorUpdate | None = None,
        type_data: SupplierUpdate | ServiceUpdate | None = None,
    ) -> Executor:
        wants_executor_update = executor_data is not None and executor_data.model_fields_set
        wants_type_update = type_data is not None and type_data.model_fields_set

        if wants_type_update:
            if isinstance(type_data, SupplierUpdate) and executor.type != ExecutorTypes.supplier:
                raise ExecutorTypeMismatchError(executor.id, expected=ExecutorTypes.supplier)
            if isinstance(type_data, ServiceUpdate) and executor.type != ExecutorTypes.service:
                raise ExecutorTypeMismatchError(executor.id, expected=ExecutorTypes.service)

        try:
            if wants_executor_update:
                assert executor_data is not None
                await self.executor_repo.change_account_data(executor.id, executor_data)

            if wants_type_update:
                assert type_data is not None
                if isinstance(type_data, SupplierUpdate):
                    await self.executor_repo.change_supplier_data(executor.id, type_data)
                else:
                    await self.executor_repo.change_service_data(executor.id, type_data)

            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise self._translate_integrity_error(exc) from exc

        await self.db.refresh(executor)
        return executor

    @staticmethod
    def _translate_integrity_error(exc: IntegrityError) -> ExecutorError:
        constraint = getattr(exc.orig, "constraint_name", None) or str(exc.orig)
        for name, field in _UNIQUE_CONSTRAINT_FIELD_MAP.items():
            if name in str(constraint):
                return DuplicateFieldError(field)
        return ExecutorError("Не удалось сохранить изменения")


async def build_executor_read(executor: Executor, db: AsyncSession) -> ExecutorRead:
    """Собирает ExecutorRead из объекта исполнителя, включая type-specific данные.

    Используется и в GET /auth/me, и в PATCH /profile/update-data, чтобы оба
    эндпоинта возвращали профиль одинакового вида (с подпиской и типовыми данными).
    """
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