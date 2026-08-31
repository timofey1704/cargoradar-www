from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.auth import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, executor_id: int, jti: str, expires_at: datetime) -> RefreshToken:
        token = RefreshToken(executor_id=executor_id, jti=jti, expires_at=expires_at)
        self.session.add(token)
        await self.session.flush()  # чтобы получить id, коммит делает вызывающий сервис
        return token

    async def get_by_jti(self, jti: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.jti == jti)
        )
        return result.scalar_one_or_none()

    async def revoke(self, token: RefreshToken, *, replaced_by_jti: str | None = None) -> None:
        token.revoked_at = datetime.now(timezone.utc)
        token.replaced_by_jti = replaced_by_jti

    async def revoke_all_for_user(self, executor_id: int) -> None:
        """Для 'выйти со всех устройств' — отзывает все активные refresh-токены юзера."""
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.executor_id == executor_id,
                RefreshToken.revoked_at.is_(None),
            )
        )
        now = datetime.now(timezone.utc)
        for token in result.scalars():
            token.revoked_at = now