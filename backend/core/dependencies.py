from typing import Annotated, Iterable
from collections.abc import AsyncGenerator
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal
from core.models.enums.actor_types import ActorType
from core.security import decode_token

from client.models.client import Client
from client.repositories.client import ClientRepository

from executor.models.executor import Executor
from executor.repositories.executor import ExecutorRepository


# Извлекает Bearer-токен из заголовка Authorization.
# auto_error=False — не даём FastAPI вернуть 403, обрабатываем отсутствие токена сами (401).
bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency: открывает сессию на запрос и закрывает после используя context manager."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    db: DbSession,
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Client:
    """
    Dependency: декодирует JWT, достаёт юзера из БД.
    Если что-то не так — бросает 401.
    Используется в защищённых эндпоинтах через Depends().

    Access-токен принимается либо из заголовка Authorization: Bearer,
    либо из httpOnly-куки client_access_token (основной путь с фронта).
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
        token = request.cookies.get("client_access_token")

    if not token:
        raise unauthorized

    payload = decode_token(token, is_refresh=False)

    if not payload or payload.get("type") != "access" or payload.get("role") != "client":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    subject = payload.get("sub")
    if not isinstance(subject, str):
        raise unauthorized

    try:
        user_id = int(subject)
    except ValueError:
        raise unauthorized

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

@dataclass(frozen=True, slots=True)
class ChatActor:
    """Участник чата: клиент или исполнитель.

    Чат доступен обеим ролям, поэтому у REST-роутов чата нет отдельного
    `CurrentClient`/`CurrentExecutor` — вместо них `CurrentChatActor` с ролью,
    из которой сервис строит проверку участия в беседе и свой Redis-канал
    (`chat:user:{role}:{id}` — без роли id двух таблиц совпали бы).
    """

    role: ActorType  # ActorType.client | ActorType.executor
    id: int


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def authenticate_chat_actor(
    db: AsyncSession, tokens: Iterable[str | None]
) -> ChatActor:
    """Первый валидный access-токен из списка → участник чата.

    Общая точка входа для REST-зависимости и WebSocket-хаба: браузерный
    WebSocket не умеет ставить заголовки, поэтому хаб передаёт сюда токены
    из cookie (и опционально из query). Бросает HTTPException (401/403) —
    если ни один токен не подошёл, поднимается последняя ошибка.
    """
    last_error: HTTPException | None = None

    for token in tokens:
        if not token:
            continue

        payload = decode_token(token, is_refresh=False)
        if not payload or payload.get("type") != "access":
            last_error = HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Invalid or expired token"
            )
            continue

        role = payload.get("role")
        if role not in (ActorType.client.value, ActorType.executor.value):
            last_error = HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Invalid or expired token"
            )
            continue

        subject = payload.get("sub")
        if not isinstance(subject, str):
            last_error = _unauthorized()
            continue

        try:
            user_id = int(subject)
        except (TypeError, ValueError):
            last_error = _unauthorized()
            continue

        if role == ActorType.client.value:
            user = await ClientRepository(db).get_by_id(user_id)
        else:
            user = await ExecutorRepository(db).get_by_id(user_id)

        if user is None:
            last_error = HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
            continue

        if not user.is_active:
            # токен валиден, но аккаунт заблокирован — дальше не пробуем
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, "Account is deactivated"
            )

        return ChatActor(role=ActorType(role), id=user_id)

    raise last_error or _unauthorized()


async def get_chat_actor(
    db: DbSession,
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> ChatActor:
    """Dependency для REST-роутов чата: Bearer-заголовок либо httpOnly-куки.

    Обе роли ходят в одни и те же `/api/conversations*`, токен
    берётся из `client_access_token`/`executor_access_token`, а роль claims-а
    JWT определяет, от чьего имени работает запрос.
    """
    return await authenticate_chat_actor(
        db,
        (
            credentials.credentials if credentials else None,
            request.cookies.get("client_access_token"),
            request.cookies.get("executor_access_token"),
        ),
    )

# Type aliases для инъекций зависимостей
CurrentClient = Annotated[Client, Depends(get_current_user)]
CurrentExecutor = Annotated[Executor, Depends(get_current_executor)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentChatActor = Annotated[ChatActor, Depends(get_chat_actor)]