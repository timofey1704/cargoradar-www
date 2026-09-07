# client/services/support_requests.py
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from core.models.enums.support_statuses import SupportRequestTypes
from core.models.support_request import SupportRequest
from client.repositories.support_requests import ClientSupportRequestRepository


async def create_request(
    session: AsyncSession,
    client_id: int,
    *,
    request_type: SupportRequestTypes,
    title: str,
    description: str,
) -> SupportRequest:
    """Создать заявку в службу поддержки от клиента."""
    repo = ClientSupportRequestRepository(session)
    return await repo.create(
        owner_id=client_id,
        request_type=request_type,
        title=title,
        description=description,
    )


async def get_requests(
    session: AsyncSession,
    client_id: int,
) -> list[SupportRequest]:
    """Получить все заявки клиента."""
    repo = ClientSupportRequestRepository(session)
    return await repo.get_all_requests_by_id(owner_id=client_id)