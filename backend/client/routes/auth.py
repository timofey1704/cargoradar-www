from fastapi import APIRouter, HTTPException, Request, Response, status

from core.cookies import (
    clear_client_auth_cookies,
    set_client_auth_cookies,
)
from core.dependencies import CurrentClient, DbSession
from core.schemas.common_auth_credentials import CommonCredentialsFields
from core.schemas.token import RefreshRequest, TokenResponse
from core.repositories.subscription_repository import SubscriptionRepository

from client.models import Client
from client.schemas.client_credentials import ClientRegister
from client.schemas.client_read import ClientRead
from client.schemas.client_update import ClientUpdate
from client.schemas.client_read import SubscriptionRead

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
async def refresh(
    request: Request,
    db: DbSession,
    response: Response,
    data: RefreshRequest | None = None,
) -> TokenResponse:
    """Ротация refresh-токена: выдаёт новую пару access + refresh.

    Токен принимается из тела (внешние API-клиенты — прежний контракт) либо
    из httpOnly-куки client_refresh_token — основной путь с фронта, где JS
    не видит cookie, поэтому обёртка apiRequest шлёт POST /auth/refresh без тела.
    """
    refresh_token = data.refresh_token if data else request.cookies.get("client_refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token",
        )
    result = await auth_service.refresh_tokens(refresh_token, db)
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


@router.get("/me", response_model=ClientRead, status_code=status.HTTP_200_OK)
async def get_me(current: CurrentClient, db: DbSession) -> ClientRead:
    """Данные текущего аккаунта клиента."""
    subscription_repo = SubscriptionRepository(db)
    active_subscription = await subscription_repo.get_active_for_client(current.id)

    return ClientRead(
        id=current.id,
        name=current.name,
        email=current.email,
        phone_number=current.phone_number,
        type=current.type,
        VIN_code=current.VIN_code,
        image_url=current.image_url,
        is_notifications_enabled=current.is_notifications_enabled,
        is_active=current.is_active,
        subscription=SubscriptionRead.model_validate(active_subscription) if active_subscription else None,
    )


@router.patch("/update-data", response_model=ClientRead, status_code=status.HTTP_200_OK)
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