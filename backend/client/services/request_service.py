"""Сервис заявок клиента на перевозку (CargoRequest): CRUD в рамках владельца.

Репозиторий (client.repositories.request.CargoRequestRepository) готовит
изменения и делает flush — транзакцию закрывает сервис, как и в ClientService.
Правила по статусам живут здесь, проверка владельца — в запросе репозитория.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from core.services.search.common import DEFAULT_PAGE_LIMIT, build_page

from client.exceptions import (
    CargoRequestNotDeletableError,
    CargoRequestNotEditableError,
    CargoRequestNotFoundError,
)
from client.models.enums.request_statuses import CargoRequestStatus
from client.models.request import CargoRequest
from client.repositories.request import CargoRequestRepository
from client.schemas.request import (
    CargoRequestCreate,
    CargoRequestDeleted,
    CargoRequestPageRead,
    CargoRequestRead,
    CargoRequestUpdate,
)

# править заявку можно, пока её не взял перевозчик
EDITABLE_STATUSES = frozenset({CargoRequestStatus.NEW})
# мягко удалять — новые и уже отменённые: заявку в работе удалять нельзя
DELETABLE_STATUSES = frozenset({CargoRequestStatus.NEW, CargoRequestStatus.CANCELLED})


class CargoRequestService:
    """Заявки на перевозку одного клиента: создание, чтение, правка, удаление."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = CargoRequestRepository(db)

    async def create(self, client_id: int, data: CargoRequestCreate) -> CargoRequestRead:
        """Создать заявку от имени клиента; статус `new` ставит сама модель."""
        request = await self.repository.create(client_id, data)

        await self.db.commit()
        await self.db.refresh(request)  # server_default: id/status/created_at/updated_at
        return CargoRequestRead.model_validate(request)

    async def get(self, client_id: int, request_id: int) -> CargoRequestRead:
        """Одна заявка клиента (404, в т.ч. если заявка чужая)."""
        request = await self._get_owned(client_id, request_id)
        return CargoRequestRead.model_validate(request)

    async def list_by_client(
        self,
        client_id: int,
        *,
        skip: int = 0,
        limit: int = DEFAULT_PAGE_LIMIT,
    ) -> CargoRequestPageRead:
        """Страница заявок клиента, свежие сверху."""
        requests = await self.repository.get_by_client(client_id, skip=skip, limit=limit)
        return build_page(
            [CargoRequestRead.model_validate(request) for request in requests],
            skip=skip,
            limit=limit,
        )

    async def update(
        self,
        client_id: int,
        request_id: int,
        data: CargoRequestUpdate,
    ) -> CargoRequestRead:
        """Изменить заявку: только переданные поля и только пока она `new`."""
        request = await self._get_owned(client_id, request_id)
        if request.status not in EDITABLE_STATUSES:
            raise CargoRequestNotEditableError(request_id, request.status.value)

        updated = await self.repository.update(request, data)

        await self.db.commit()
        await self.db.refresh(updated)
        return CargoRequestRead.model_validate(updated)

    async def delete(self, client_id: int, request_id: int) -> CargoRequestDeleted:
        """Мягко удалить заявку: помечаем `is_deleted`, строка остаётся в БД."""
        request = await self._get_owned(client_id, request_id)
        if request.status not in DELETABLE_STATUSES:
            raise CargoRequestNotDeletableError(request_id, request.status.value)

        await self.repository.soft_delete(request)

        await self.db.commit()
        await self.db.refresh(request)
        return CargoRequestDeleted.model_validate(request)

    async def _get_owned(self, client_id: int, request_id: int) -> CargoRequest:
        """Заявка клиента или CargoRequestNotFoundError.

        Отсутствующую и чужую заявку не различаем — не подсказываем, что она есть.
        """
        request = await self.repository.get_owned(client_id, request_id)
        if request is None:
            raise CargoRequestNotFoundError(request_id)
        return request

