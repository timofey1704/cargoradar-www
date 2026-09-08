from fastapi import APIRouter, HTTPException, status

from core.dependencies import CurrentExecutor, DbSession

from executor.exceptions import (
    DuplicateFieldError,
    ExecutorError,
    ExecutorTypeMismatchError,
)
from executor.models.enums.executor_types import ExecutorTypes
from executor.repositories.executor import ExecutorRepository
from executor.schemas.executor_read import ExecutorRead
from executor.schemas.executor_update import (
    ExecutorUpdate,
    ProfileUpdateRequest,
    ServiceUpdate,
    SupplierUpdate,
)
from executor.services.executor_service import ExecutorService, build_executor_read

router = APIRouter(prefix="/profile", tags=["executor profile"])

_LEGAL_FIELDS = {"legal_name", "unp", "address", "brands"}


@router.patch("/update-data", response_model=ExecutorRead, status_code=status.HTTP_200_OK)
async def update_profile_data(
    data: ProfileUpdateRequest,
    current: CurrentExecutor,
    db: DbSession,
) -> ExecutorRead:
    """Обновляет профиль текущего исполнителя.

    Принимает плоское тело; обновляются только переданные поля. Приходят как
    обычные аккаунт-поля (name, email, ...), так и юридические (legal_name, unp,
    address) и brands — для type=supplier они уходят в таблицу suppliers,
    для type=service — в services.
    """
    raw = data.model_dump(exclude_none=True)

    executor_fields = {key: value for key, value in raw.items() if key not in _LEGAL_FIELDS}
    type_fields = {
        key: value
        for key, value in raw.items()
        if key in _LEGAL_FIELDS and value not in ("", None)
    }

    if not executor_fields and not type_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нужно передать хотя бы одно поле для обновления",
        )

    executor_data = ExecutorUpdate(**executor_fields) if executor_fields else None

    type_data = None
    if type_fields:
        match current.type:
            case ExecutorTypes.supplier:
                type_data = SupplierUpdate(**type_fields)
            case ExecutorTypes.service:
                type_data = ServiceUpdate(**type_fields)
            case _:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Данный тип аккаунта не поддерживает юридические поля",
                )

    service = ExecutorService(db=db, executor_repo=ExecutorRepository(db))

    try:
        executor = await service.update_profile(
            executor=current,
            executor_data=executor_data,
            type_data=type_data,
        )
    except ExecutorTypeMismatchError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Данный тип аккаунта не поддерживает юридические поля",
        ) from None
    except DuplicateFieldError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Поле '{exc.field}' уже занято",
        ) from exc
    except ExecutorError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return await build_executor_read(executor, db)

