from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from executor.models.executor import Executor

from executor.repositories.executor import ExecutorRepository

# директория для загруженного контента
UPLOAD_DIR = Path("uploads/executors/")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def get_executor(session: AsyncSession, executor_id: int) -> Executor:
    executor = await ExecutorRepository(session).get_by_id(executor_id)
    if not executor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Executor not found")
    return executor

async def update_account_data(
    session: AsyncSession,
    executor_id: int,
    *,
    name: str | None = None,
    email: str | None = None,
    phone_number: str | None = None,
    image_url: str | None,
    is_notifications_enabled: bool | None = None,
) -> Executor:
    """Обновляет переданные поля профиля исполнителя.

    None пропускается (поле не передали).
    """
    repo = ExecutorRepository(session)
    executor = await repo.get_by_id(executor_id)
    if not executor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data: dict = {}

    if name is not None:
        update_data["name"] = name
    if email is not None:
        update_data["email"] = email
    if phone_number is not None:
        update_data["phone_number"] = phone_number
    if image_url is not None:
        update_data["image_url"] = phone_number
    if is_notifications_enabled is not None:
        update_data["is_notifications_enabled"] = is_notifications_enabled

    for key, value in update_data.items():
        setattr(executor, key, value)

    await session.commit()
    await session.refresh(executor)
    return executor