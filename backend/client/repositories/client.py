from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from client.models.client import Client
from client.models.enums.client_types import ClientTypes

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
        type: ClientTypes,
        name: str,
        phone_number: str,
        email: str,
        hashed_password: str | None = None,
        VIN_code: str | None = None,
        privacy_accepted: bool = True
    ) -> Client:
        client = Client(
            type=type,
            name=name,
            email=email,
            hashed_password=hashed_password,
            phone_number=phone_number,
            VIN_code=VIN_code,
            privacy_accepted=privacy_accepted
        )
        self.db.add(client)
        await self.db.commit()
        await self.db.refresh(client)
        return client