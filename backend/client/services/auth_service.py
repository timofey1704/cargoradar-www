import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import (
    decode_token,
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)
from core.schemas.common_auth_credentials import CommonCredentialsFields
from core.schemas.token import TokenResponse
from client.schemas.client_credentials import ClientRegister

from client.repositories.client import ClientRepository
from client.repositories.refresh_token import RefreshTokenRepository
from client.models.enums.client_types import ClientTypes
from client.models.legal_client import LegalClient

logger = logging.getLogger(__name__)


async def _issue_tokens(client_id: int, db: AsyncSession) -> TokenResponse:
    """Общая точка выдачи пары токенов — используется и в register, и в login"""
    access_token = create_access_token(subject=str(client_id))
    refresh_token, jti, expires_at = create_refresh_token(subject=str(client_id))

    refresh_repo = RefreshTokenRepository(db)
    await refresh_repo.create(client_id=client_id, jti=jti, expires_at=expires_at)
    await db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def register_client(data: ClientRegister, db: AsyncSession) -> TokenResponse:
    """
    Регистрация: проверяем уникальность номера телефона, хэшируем пароль,
    создаём аккаунт и профиль, возвращаем пару токенов сразу —
    чтобы фронт не делал лишний запрос на login.
    """
    logger.info("register_client: email=%s phone_number=%s",
                data.email, data.phone_number)

    repo = ClientRepository(db)

    existing = await repo.get_by_phone_number(data.phone_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number already registered",
        )

    hashed = hash_password(data.password)
    client = await repo.create(
        type=data.type,
        name=data.name,
        email=str(data.email),
        phone_number=data.phone_number,
        hashed_password=hashed,
        VIN_code =data.VIN_code,
        privacy_accepted=data.privacy_accepted
        )

    # Для юридического лица — профиль в отдельной таблице legal_clients.
    # repo.create уже закоммитил клиента; LegalClient уйдёт в БД вместе с
    # commit'ом в _issue_tokens.
    if data.type is ClientTypes.legal:
        db.add(LegalClient(
            client_id=client.id,
            legal_name=data.legal_name,
            unp=data.UNP,
            address=data.address,
        ))

    return await _issue_tokens(client.id, db)


async def login_client(data: CommonCredentialsFields, db: AsyncSession) -> TokenResponse:
    """
    Логин: находим аккаунт, верифицируем пароль.
    Намеренно не говорим что именно неверно — телефон или пароль.
    """
    repo = ClientRepository(db)

    client = await repo.get_by_phone_number(data.phone_number)
    if (
        not client
        or not client.hashed_password
        or not verify_password(data.password, client.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not client.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    return await _issue_tokens(client.id, db)


async def refresh_tokens(refresh_token: str, db: AsyncSession) -> TokenResponse:
    """
    Обменивает валидный refresh-токен на новую пару access+refresh (ротация).
    Старый refresh отзывается сразу — повторное использование одного и того же
    refresh-токена дважды невозможно (защита от повтора украденного токена).
    """
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )

    payload = decode_token(refresh_token, is_refresh=True)
    if not payload or payload.get("type") != "refresh" or payload.get("role") != "client":
        raise unauthorized

    jti = payload.get("jti")
    subject = payload.get("sub")
    if not jti or not subject:
        raise unauthorized

    refresh_repo = RefreshTokenRepository(db)
    stored_token = await refresh_repo.get_by_jti(jti)

    if stored_token is None:
        raise unauthorized

    # RefreshToken хранит ровно одного владельца (check ck_refresh_tokens_one_owner),
    # а для токена исполнителя заполнен именно client_id. Если записи «без владельца»
    # всё же встретились — не доверяем ей.
    owner_id = stored_token.client_id
    if owner_id is None:
        raise unauthorized

    if not stored_token.is_active:
        # ПОВТОРНОЕ использование уже отозванного (ротированного) refresh-токена —
        # сильный сигнал, что токен был украден и легитимный юзер, и атакующий
        # оба пытаются им воспользоваться. Реагируем максимально жёстко:
        # отзываем ВСЕ refresh-токены юзера, заставляя перелогиниться на всех устройствах.
        await refresh_repo.revoke_all_for_user(owner_id)
        await db.commit()
        raise unauthorized

    try:
        client_id = int(subject)
    except ValueError:
        raise unauthorized

    if owner_id != client_id:
        raise unauthorized

    client_repo = ClientRepository(db)
    client = await client_repo.get_by_id(client_id)
    if not client or not client.is_active:
        raise unauthorized

    # ротация: новый access + новый refresh, старый refresh отзываем
    access_token = create_access_token(subject=str(client.id))
    new_refresh_token, new_jti, expires_at = create_refresh_token(subject=str(client.id))

    await refresh_repo.create(client_id=client.id, jti=new_jti, expires_at=expires_at)
    await refresh_repo.revoke(stored_token, replaced_by_jti=new_jti)
    await db.commit()

    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


async def logout_user(refresh_token: str, db: AsyncSession) -> None:
    """Отзывает конкретный refresh-токен (логаут с текущего устройства)"""
    payload = decode_token(refresh_token, is_refresh=True)
    if not payload or payload.get("role") != "client":
        return  # не наш тип токена — отзывать нечего, тихо выходим

    jti = payload.get("jti")
    if not jti:
        return

    refresh_repo = RefreshTokenRepository(db)
    stored_token = await refresh_repo.get_by_jti(jti)
    if stored_token and stored_token.is_active:
        await refresh_repo.revoke(stored_token)
        await db.commit()