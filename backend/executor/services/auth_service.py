import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import (
    create_executor_access_token,
    create_executor_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from core.schemas.common_auth_credentials import CommonCredentialsFields
from core.schemas.token import TokenResponse
from core.repositories.membership_repository import MembershipRepository
from core.repositories.subscription_repository import SubscriptionRepository

from executor.models.enums.car_brands import CarBrands
from executor.models.service import Service
from executor.models.supplier import Supplier
from executor.models.towtruck import TowTruck
from executor.models.vehicles import Vehicle
from executor.repositories.executor import ExecutorRepository
from executor.repositories.refresh_token import RefreshTokenRepository
from executor.schemas.executor_credentials import ExecutorRegister

logger = logging.getLogger(__name__)


async def _issue_tokens(executor_id: int, db: AsyncSession) -> TokenResponse:
    """Общая точка выдачи пары токенов — используется и в register, и в login."""
    access_token = create_executor_access_token(executor_id)
    refresh_token, jti, expires_at = create_executor_refresh_token(executor_id)

    refresh_repo = RefreshTokenRepository(db)
    await refresh_repo.create(executor_id=executor_id, jti=jti, expires_at=expires_at)
    await db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def register_executor(data: ExecutorRegister, db: AsyncSession) -> TokenResponse:
    logger.info("register_executor: email=%s phone_number=%s", data.email, data.phone_number)

    repo = ExecutorRepository(db)

    existing = await repo.get_by_phone_number(data.phone_number)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone number already registered")

    try:
        hashed = hash_password(data.password)
        executor = await repo.create(
            type=data.type,
            name=data.name,
            email=data.email,
            phone_number=data.phone_number,
            hashed_password=hashed,
            privacy_accepted=data.privacy_accepted,
        )

        await _create_profile(data, executor.id, db)
        await db.flush()

        membership_repo = MembershipRepository(db)
        trial_plan = await membership_repo.get_trial_plan()
        if trial_plan is None:
            logger.error(
                "Trial membership plan is not configured, executor will be registered without subscription"
            )
        else:
            subscription_repo = SubscriptionRepository(db)
            await subscription_repo.grant_trial_to_executor(executor_id=executor.id, membership_id=trial_plan.id)

        await db.commit()
        await db.refresh(executor)
    except Exception:
        await db.rollback()
        raise

    return await _issue_tokens(executor.id, db)

async def _create_profile(data: ExecutorRegister, executor_id: int, db: AsyncSession) -> None:
    """Создаёт профиль, соответствующий типу аккаунта (схема требует ровно один).

    Для перевозчика (carrier) из списка `cars` создаётся по строке в таблице
    vehicles — один исполнитель может иметь несколько автомобилей.
    """
    if data.cars is not None:
        for car in data.cars:
            db.add(Vehicle(executor_id=executor_id, **car.model_dump()))
        return

    if data.service is not None:
        # В текущей схеме колонка brands — одиночный enum, а не массив,
        # поэтому сохраняем первую марку из списка выбранных.
        brands = data.service.brands
        db.add(
            Service(
                executor_id=executor_id,
                **data.service.model_dump(exclude={"brands"}),
                brands=brands[0] if brands else CarBrands.all,
            )
        )
        return

    if data.supplier is not None:
        db.add(Supplier(executor_id=executor_id, **data.supplier.model_dump()))
        return

    if data.towtruck is not None:
        db.add(TowTruck(executor_id=executor_id, **data.towtruck.model_dump()))
        return

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Profile for account type is required",
    )


async def login_executor(data: CommonCredentialsFields, db: AsyncSession) -> TokenResponse:
    """
    Логин: находим аккаунт, верифицируем пароль.
    Намеренно не говорим что именно неверно — телефон или пароль.
    """
    repo = ExecutorRepository(db)

    executor = await repo.get_by_phone_number(data.phone_number)
    if (
        not executor
        or not executor.hashed_password
        or not verify_password(data.password, executor.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not executor.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    return await _issue_tokens(executor.id, db)


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
    if not payload or payload.get("type") != "refresh" or payload.get("role") != "executor":
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
    # а для токена исполнителя заполнен именно executor_id. Если записи «без владельца»
    # всё же встретились — не доверяем ей.
    owner_id = stored_token.executor_id
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
        executor_id = int(subject)
    except ValueError:
        raise unauthorized

    if owner_id != executor_id:
        raise unauthorized

    executor_repo = ExecutorRepository(db)
    executor = await executor_repo.get_by_id(executor_id)
    if not executor or not executor.is_active:
        raise unauthorized

    # ротация: новый access + новый refresh, старый refresh отзываем
    access_token = create_executor_access_token(executor.id)
    new_refresh_token, new_jti, expires_at = create_executor_refresh_token(executor.id)

    await refresh_repo.create(executor_id=executor.id, jti=new_jti, expires_at=expires_at)
    await refresh_repo.revoke(stored_token, replaced_by_jti=new_jti)
    await db.commit()

    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


async def logout_user(refresh_token: str, db: AsyncSession) -> None:
    """Отзывает конкретный refresh-токен (логаут с текущего устройства)"""
    payload = decode_token(refresh_token, is_refresh=True)
    if not payload or payload.get("role") != "executor":
        return  # не наш тип токена — отзывать нечего, тихо выходим

    jti = payload.get("jti")
    if not jti:
        return

    refresh_repo = RefreshTokenRepository(db)
    stored_token = await refresh_repo.get_by_jti(jti)
    if stored_token and stored_token.is_active:
        await refresh_repo.revoke(stored_token)
        await db.commit()