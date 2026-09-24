"""Роуты заявок клиента на перевозку (CargoRequest) — «мои заказы» в кабинете.

Префикс `/orders` выбран под фронт: lib/api/client/orders.ts ходит в
`/client/orders/` (список и создание), операции над одной заявкой — по её id.
"""

from fastapi import APIRouter, HTTPException, status

from core.dependencies import CurrentClient, DbSession
from core.services.search.common import DEFAULT_PAGE_LIMIT

from client.exceptions import (
    CargoRequestNotDeletableError,
    CargoRequestNotEditableError,
    CargoRequestNotFoundError,
    ClientError,
)
from client.schemas.request import (
    CargoRequestCreate,
    CargoRequestDeleted,
    CargoRequestRead,
    CargoRequestUpdate,
)
from client.services.request_service import CargoRequestService

router = APIRouter(prefix="/orders", tags=["client orders"])


def _http_error(exc: ClientError) -> HTTPException:
    """Доменные ошибки сервиса — в HTTP-ответы (как в роуте профиля)."""
    if isinstance(exc, CargoRequestNotFoundError):
        # чужая/удалённая заявка неотличима от несуществующей — не подсказываем
        return HTTPException(status.HTTP_404_NOT_FOUND, "Заявка не найдена")
    if isinstance(exc, CargoRequestNotEditableError):
        return HTTPException(
            status.HTTP_409_CONFLICT,
            f"Заявку в статусе '{exc.status}' нельзя изменить",
        )
    if isinstance(exc, CargoRequestNotDeletableError):
        return HTTPException(
            status.HTTP_409_CONFLICT,
            f"Заявку в статусе '{exc.status}' нельзя удалить",
        )
    return HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))


@router.get("", response_model=list[CargoRequestRead], status_code=status.HTTP_200_OK)
async def get_client_orders(
    current: CurrentClient,
    db: DbSession,
    skip: int = 0,
    limit: int = DEFAULT_PAGE_LIMIT,
) -> list[CargoRequestRead]:
    """Заявки текущего клиента, свежие сверху (чужие и удалённые не попадают).

    Фронт ждёт простой массив (lib/api/client/orders.ts → `CargoRequest[]`),
    поэтому страницу сервиса разворачиваем в список.
    """
    service = CargoRequestService(db)
    page = await service.list_by_client(current.id, skip=skip, limit=limit)
    return page.items


@router.get(
    "/{request_id}",
    response_model=CargoRequestRead,
    status_code=status.HTTP_200_OK,
)
async def get_client_order(
    request_id: int,
    current: CurrentClient,
    db: DbSession,
) -> CargoRequestRead:
    """Одна заявка клиента (404 — если её нет, она чужая или удалена)."""
    service = CargoRequestService(db)
    try:
        return await service.get(current.id, request_id)
    except ClientError as exc:
        raise _http_error(exc) from exc


@router.post("", response_model=CargoRequestRead, status_code=status.HTTP_201_CREATED)
async def create_client_order(
    data: CargoRequestCreate,
    current: CurrentClient,
    db: DbSession,
) -> CargoRequestRead:
    """Создать заявку на перевозку от имени текущего клиента (статус `new`)."""
    service = CargoRequestService(db)
    return await service.create(current.id, data)


@router.patch(
    "/{request_id}",
    response_model=CargoRequestRead,
    status_code=status.HTTP_200_OK,
)
async def update_client_order(
    request_id: int,
    data: CargoRequestUpdate,
    current: CurrentClient,
    db: DbSession,
) -> CargoRequestRead:
    """Изменить свою заявку: применяются только переданные поля.

    404 — заявки нет или она чужая; 409 — заявка уже взята в работу.
    """
    service = CargoRequestService(db)
    try:
        return await service.update(current.id, request_id, data)
    except ClientError as exc:
        raise _http_error(exc) from exc


@router.delete(
    "/{request_id}",
    response_model=CargoRequestDeleted,
    status_code=status.HTTP_200_OK,
)
async def delete_client_order(
    request_id: int,
    current: CurrentClient,
    db: DbSession,
) -> CargoRequestDeleted:
    """Мягко удалить свою заявку: строка остаётся в БД с `is_deleted=true`.

    404 — заявки нет или она чужая; 409 — заявка в работе или уже выполнена.
    """
    service = CargoRequestService(db)
    try:
        return await service.delete(current.id, request_id)
    except ClientError as exc:
        raise _http_error(exc) from exc

