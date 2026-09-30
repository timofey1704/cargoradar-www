import math

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from redis.exceptions import RedisError

from core.cookies import (
    clear_client_auth_cookies,
    set_client_auth_cookies,
)
from core.dependencies import CurrentClient, DbSession
from core.rate_limiter import rate_limiter
from core.schemas.common_auth_credentials import CommonCredentialsFields
from core.schemas.token import RefreshRequest, TokenResponse

from client.schemas.client_credentials import ClientRegister
from client.schemas.client_read import ClientRead
from client.services.client_service import build_client_read

from client.services import auth_service

router = APIRouter(prefix="/auth", tags=["client auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            rate_limiter.limit(
                requests_per_second=0.1,
                burst=5,
                scope="client-register-ip",
                fail_open=False,
            )
        )
    ],
)
async def register(data: ClientRegister, db: DbSession, response: Response) -> TokenResponse:
    """Регистрация аккаунта клиента — сразу возвращает пару токенов."""
    result = await auth_service.register_client(data, db)
    set_client_auth_cookies(response, result.access_token, result.refresh_token)
    return result


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[
        Depends(
            rate_limiter.limit(
                requests_per_second=1,
                burst=10,
                scope="client-login-ip",
                fail_open=False,
            )
        )
    ],
)
async def login(data: CommonCredentialsFields, db: DbSession, response: Response) -> TokenResponse:
    """Вход по телефону и паролю."""
    account_key = rate_limiter.build_key(
        scope="client-login-account",
        identifier=data.phone_number,
    )
    try:
        allowed, retry_after = await rate_limiter.is_allowed(
            key=account_key,
            requests_per_second=0.02,
            burst=5,
        )
    except RedisError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rate limiter unavailable",
            headers={"Retry-After": "1"},
        ) from error

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests",
            headers={"Retry-After": str(max(1, math.ceil(retry_after)))},
        )

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
    """Данные текущего аккаунта клиента (включая юрданные для type=legal)"""
    return await build_client_read(current, db)
