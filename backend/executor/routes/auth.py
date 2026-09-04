from fastapi import APIRouter, Request, Response, status

from core.cookies import (
    clear_executor_auth_cookies,
    set_executor_auth_cookies,
)
from core.dependencies import CurrentExecutor, DbSession
from core.schemas.common_auth_credentials import CommonCredentialsFields
from core.schemas.token import RefreshRequest, TokenResponse

from executor.models import Executor
from executor.schemas.executor_credentials import ExecutorRegister

from executor.schemas.executor_read import ExecutorRead
from executor.schemas.executor_update import ExecutorUpdate
from executor.services import auth_service, executor_service

router = APIRouter(prefix="/auth", tags=["executor auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: ExecutorRegister, db: DbSession, response: Response) -> TokenResponse:
    """Регистрация аккаунта исполнителя — сразу возвращает пару токенов."""
    result = await auth_service.register_executor(data, db)
    set_executor_auth_cookies(response, result.access_token, result.refresh_token)
    return result


@router.post("/login", response_model=TokenResponse)
async def login(data: CommonCredentialsFields, db: DbSession, response: Response) -> TokenResponse:
    """Вход по телефону и паролю."""
    result = await auth_service.login_executor(data, db)
    set_executor_auth_cookies(response, result.access_token, result.refresh_token)
    return result


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: DbSession, response: Response) -> TokenResponse:
    """Ротация refresh-токена: выдаёт новую пару access + refresh."""
    result = await auth_service.refresh_tokens(data.refresh_token, db)
    set_executor_auth_cookies(response, result.access_token, result.refresh_token)
    return result


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    db: DbSession,
    response: Response,
    data: RefreshRequest | None = None,
) -> None:
    """Отзывает refresh-токен (берём из тела или из куки) и чистит куки."""
    refresh_token = data.refresh_token if data else request.cookies.get("executor_refresh_token")
    if refresh_token:
        await auth_service.logout_user(refresh_token, db)
    clear_executor_auth_cookies(response)


@router.get("/me", response_model=ExecutorRead)
async def get_me(current: CurrentExecutor) -> Executor:
    """Данные текущего аккаунта исполнителя."""
    return current


@router.patch("/update-data", response_model=ExecutorRead)
async def update_me(
    data: ExecutorUpdate,
    db: DbSession,
    current: CurrentExecutor,
) -> Executor:
    """Обновляет профиль текущего исполнителя (передаются только изменяемые поля)."""
    return await executor_service.update_account_data(
        session=db,
        executor_id=current.id,
        name=data.name,
        image_url=data.image_url,
        email=str(data.email) if data.email is not None else None,
        phone_number=data.phone_number,
        is_notifications_enabled=data.is_notifications_enabled,
    )