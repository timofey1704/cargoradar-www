from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from client.models.client import Client
from client.repositories.client import ClientRepository

# директория для загруженного контента
UPLOAD_DIR = Path("uploads/clients/")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def get_client(session: AsyncSession, client_id: int) -> Client:
    client = await ClientRepository(session).get_by_id(client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client

async def update_account_data(
    session: AsyncSession,
    client_id: int,
    *,
    name: str | None = None,
    email: str | None = None,
    phone_number: str | None = None,
    is_notifications_enabled: bool | None = None,
    is_active: bool | None = None,
    image_url: str | None = None
) -> Client:
    """Обновляет переданные поля профиля исполнителя.
    None пропускается (поле не передали).
    """
    repo = ClientRepository(session)
    client = await repo.get_by_id(client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data: dict = {}

    if name is not None:
        update_data["name"] = name
    if email is not None:
        update_data["email"] = email
    if phone_number is not None:
        update_data["phone_number"] = phone_number
    if is_notifications_enabled is not None:
        update_data["is_notifications_enabled"] = is_notifications_enabled
    if is_active is not None:
        update_data["is_active"] = is_active
    if image_url is not None:
        update_data["image_url"] = image_url

    for key, value in update_data.items():
        setattr(client, key, value)

    await session.commit()
    await session.refresh(client)
    return client