from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from user.models.client import Client

class ClientRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, client_id: int) -> Client | None:
        result = await self.db.execute(select(Client).where(Client.id == client_id))
        return result.scalar_one_or_none()

    async def get_by_phone_number(self, phone_number: str) -> Client | None:
        result = await self.db.execute(select(Client).where(Client.phone_number == phone_number))
        return result.scalar_one_or_none()

    async def create(
        self,
        name: str,
        phone_number: str,
        email: str,
        hashed_password: str | None = None,
        VIN_code: str | None = None
    ) -> Client:
        client = Client(
            name=name,
            email=email,
            hashed_password=hashed_password,
            phone_number=phone_number,
            VIN_code=VIN_code
        )
        self.db.add(client)
        await self.db.commit()
        await self.db.refresh(client)
        return client