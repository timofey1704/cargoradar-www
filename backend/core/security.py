from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

import bcrypt
from jose import JWTError, jwt

from core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(subject: str) -> str:
    """subject — user.id в виде строки, кладём в поле 'sub'."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload = {
        "sub": subject,
        "iat": now,
        "exp": expire,
        "jti": token_urlsafe(16),
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )


def create_refresh_token(subject: str) -> tuple[str, str, datetime]:
    """
    Создаёт refresh-токен. Подписан ОТДЕЛЬНЫМ секретом (не тем же, что access) —
    так утечка access-секрета (например, из логов на бэкенде) не даёт возможности
    подделать долгоживущий refresh-токен, и наоборот.

    Возвращает (token, jti, expires_at) — jti и expires_at нужны вызывающему коду,
    чтобы сохранить их в БД (для отзыва/ротации).
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.refresh_token_expire_days)
    jti = token_urlsafe(32)

    payload = {
        "sub": subject,
        "iat": now,
        "exp": expire,
        "jti": jti,
        "type": "refresh",
    }

    token = jwt.encode(
        payload,
        settings.refresh_secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )
    return token, jti, expire


def decode_token(token: str, *, is_refresh: bool = False) -> dict | None:
    """Возвращает payload (dict) или None, если токен невалидный/просроченный.
    Намеренно не валидируем jti здесь — это ответственность вызывающего кода
    (для access — не нужно, для refresh — сверка со списком в БД в сервисном слое).
    """
    secret = (
        settings.refresh_secret_key.get_secret_value()
        if is_refresh
        else settings.secret_key.get_secret_value()
    )
    try:
        return jwt.decode(token, secret, algorithms=[settings.algorithm])
    except JWTError:
        return None