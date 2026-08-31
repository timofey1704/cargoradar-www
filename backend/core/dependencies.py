from typing import Annotated

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import AsyncGenerator

from core.database import AsyncSessionLocal
from core.security import decode_token

from client.models.client import Client
from client.repositories.client import ClientRepository

from executor.models.executor import Executor
from executor.repositories.executor import ExecutorRepository

# извлекает Bearer-токен из заголовка Authorization.
# auto_error=False — не даём FastAPI вернуть 403, обрабатываем отсутствие токена сами (401).
bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency: открывает сессию на запрос и закрывает после используя context manager."""

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


async def get_current_executor(
    db: DbSession,
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Executor:
    """
    Dependency для роутеров исполнителей. Принимает access-токен либо из header
    Authorization: Bearer, либо из httpOnly-куки executor_access_token (основной путь
    для аккаунта исполнителя). В payload JWT обязан быть claim role == "executor".
    """
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token: str | None = None
    if credentials:
        token = credentials.credentials
    else:
        token = request.cookies.get("executor_access_token")

    if not token:
        raise unauthorized

    payload = decode_token(token, is_refresh=False)

    if not payload or payload.get("type") != "access" or payload.get("role") != "executor":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    subject = payload.get("sub")
    if not isinstance(subject, str):
        raise unauthorized

    try:
        executor_id = int(subject)
    except ValueError:
        raise unauthorized

    executor = await ExecutorRepository(db).get_by_id(executor_id)

    if not executor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Executor not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not executor.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    return executor


# инжектор в роутеры исполнителей
CurrentExecutor = Annotated[Executor, Depends(get_current_executor)]

# вставляем в сигнатуру роутера одной строкой
CurrentClient = Annotated[Client, Depends(get_current_user)]

# инжектор в роутеры
DbSession = Annotated[AsyncSession, Depends(get_db)]