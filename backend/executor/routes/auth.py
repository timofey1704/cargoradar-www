import math

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from redis.exceptions import RedisError

from core.cookies import (
    clear_executor_auth_cookies,
    set_executor_auth_cookies,
)
from core.dependencies import CurrentExecutor, DbSession
from core.rate_limiter import rate_limiter
from core.schemas.common_auth_credentials import CommonCredentialsFields
from core.schemas.token import RefreshRequest, TokenResponse

from executor.models import Executor
from executor.schemas.executor_credentials import ExecutorRegister

from executor.schemas.executor_read import ExecutorRead
from executor.services import auth_service
from executor.services.executor_service import build_executor_read

router = APIRouter(prefix="/auth", tags=["executor auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            rate_limiter.limit(
                requests_per_second=0.1,
                burst=5,
                scope="executor-register-ip",
                fail_open=False,
            )
        )
    ],
)
async def register(data: ExecutorRegister, db: DbSession, response: Response) -> TokenResponse:
    """Регистрация аккаунта исполнителя — сразу возвращает пару токенов."""
    result = await auth_service.register_executor(data, db)
    set_executor_auth_cookies(response, result.access_token, result.refresh_token)
    return result


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            rate_limiter.limit(
                requests_per_second=1,
                burst=10,
                scope="executor-login-ip",
                fail_open=False,
            )
        )
    ],
)
async def login(data: CommonCredentialsFields, db: DbSession, response: Response) -> TokenResponse:
    """Вход по телефону и паролю."""
    account_key = rate_limiter.build_key(
        scope="executor-login-account",
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

    result = await auth_service.login_executor(data, db)
    set_executor_auth_cookies(response, result.access_token, result.refresh_token)
    return result


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh(
    request: Request,
    db: DbSession,
    response: Response,
    data: RefreshRequest | None = None,
) -> TokenResponse:
    """Ротация refresh-токена: выдаёт новую пару access + refresh.

    Токен принимается из тела (внешние API-клиенты — прежний контракт) либо
    из httpOnly-куки executor_refresh_token — основной путь с фронта, где JS
    не видит cookie, поэтому обёртка apiRequest шлёт POST /auth/refresh без тела.
    """
    refresh_token = data.refresh_token if data else request.cookies.get("executor_refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token",
        )
    result = await auth_service.refresh_tokens(refresh_token, db)
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


@router.get("/me", response_model=ExecutorRead, status_code=status.HTTP_200_OK)
async def get_me(current: CurrentExecutor, db: DbSession) -> ExecutorRead:
    """Данные текущего аккаунта исполнителя."""
    return await build_executor_read(current, db)
