from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import AsyncGenerator

from core.database import AsyncSessionLocal
from core.security import decode_token
from backend.user.models.client import Client
from backend.user.repositories.client import ClientRepository

# извлекает Bearer-токен из заголовка Authorization.
# auto_error=False — не даём FastAPI вернуть 403, обрабатываем отсутствие токена сами (401).
bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency: открывает сессию на запрос и закрывает после.
    yield делает это context manager'ом — аналог django's atomic()."""

    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(
    db: DbSession,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Client:
    """
    Dependency: декодирует JWT, достаёт юзера из БД.
    Если что-то не так — бросает 401.
    Используется в защищённых эндпоинтах через Depends().
    """
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise unauthorized

    payload = decode_token(credentials.credentials, is_refresh=False)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    subject = payload.get("sub")

    if not isinstance(subject, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(subject)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    repo = ClientRepository(db)
    user = await repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    return user


# вставляем в сигнатуру роутера одной строкой
CurrentUser = Annotated[Client, Depends(get_current_user)]

# инжектор в роутеры
DbSession = Annotated[AsyncSession, Depends(get_db)]