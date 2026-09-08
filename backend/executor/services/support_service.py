from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from core.models.enums.support_statuses import SupportRequestTypes
from core.models.support_request import SupportRequest
from executor.repositories.support_requests import ExecutorSupportRequestRepository


async def create_request(
    session: AsyncSession,
    executor_id: int,
    *,
    request_type: SupportRequestTypes,
    title: str,
    description: str,
) -> SupportRequest:
    """Создать заявку в службу поддержки от исполнителя."""
    repo = ExecutorSupportRequestRepository(session)
    request = await repo.create(
        owner_id=executor_id,
        request_type=request_type,
        title=title,
        description=description,
    )

    # репозиторий только добавляет объект в сессию (flush), фиксируем транзакцию
    # в сервисе — как в client_service.update_account_data, иначе при закрытии
    # сессии всё откатится и заявка не сохранится
    await session.commit()
    await session.refresh(request)
    return request


async def get_requests(
    session: AsyncSession,
    executor_id: int,
) -> list[SupportRequest]:
    """Получить все заявки исполнителя."""
    repo = ExecutorSupportRequestRepository(session)
    return await repo.get_all_requests_by_id(owner_id=executor_id)