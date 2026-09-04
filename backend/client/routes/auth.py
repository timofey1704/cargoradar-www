from fastapi import APIRouter, Request, Response, status

from core.cookies import (
    clear_client_auth_cookies,
    set_client_auth_cookies,
)
from core.dependencies import CurrentClient, DbSession
from core.schemas.common_auth_credentials import CommonCredentialsFields
from core.schemas.token import RefreshRequest, TokenResponse

from client.models import Client
from client.schemas.client_credentials import ClientRegister
from client.schemas.client_read import ClientRead
from client.schemas.client_update import ClientUpdate

from client.services import auth_service, client_service

router = APIRouter(prefix="/auth", tags=["client auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: ClientRegister, db: DbSession, response: Response) -> TokenResponse:
    """Регистрация аккаунта клиента — сразу возвращает пару токенов."""
    result = await auth_service.register_client(data, db)
    set_client_auth_cookies(response, result.access_token, result.refresh_token)
    return result


@router.post("/login", response_model=TokenResponse)
async def login(data: CommonCredentialsFields, db: DbSession, response: Response) -> TokenResponse:
    """Вход по телефону и паролю."""
    result = await auth_service.login_client(data, db)
    set_client_auth_cookies(response, result.access_token, result.refresh_token)
    return result


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: DbSession, response: Response) -> TokenResponse:
    """Ротация refresh-токена: выдаёт новую пару access + refresh."""
    result = await auth_service.refresh_tokens(data.refresh_token, db)
    set_client_auth_cookies(response, result.access_token, result.refresh_token)
    return result


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    db: DbSession,
    response: Response,
    data: RefreshRequest | None = None,
) -> None:
    """Отзывает refresh-токен (берём из тела или из куки) и чистит куки."""
    refresh_token = data.refresh_token if data else request.cookies.get("client_refresh_token")
    if refresh_token:
        await auth_service.logout_user(refresh_token, db)
    clear_client_auth_cookies(response)


@router.get("/me", response_model=ClientRead)
async def get_me(current: CurrentClient) -> Client:
    """Данные текущего аккаунта исполнителя."""
    return current


@router.patch("/update-data", response_model=ClientRead)
async def update_me(
    data: ClientUpdate,
    db: DbSession,
    current: CurrentClient,
) -> Client:
    """Обновляет профиль текущего исполнителя (передаются только изменяемые поля)."""
    return await client_service.update_account_data(
        session=db,
        client_id=current.id,
        name=data.name,
        email=str(data.email) if data.email is not None else None,
        phone_number=data.phone_number,
        is_notifications_enabled=data.is_notifications_enabled,
        is_active=data.is_active
    )