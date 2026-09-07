from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from client.models.client import Client
from client.models.legal_client import LegalClient
from client.models.enums.client_types import ClientTypes
from client.schemas.client_update import ClientUpdate, LegalClientUpdate


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
        privacy_accepted: bool = True,
    ) -> Client:
        client = Client(
            type=type,
            name=name,
            email=email,
            hashed_password=hashed_password,
            phone_number=phone_number,
            VIN_code=VIN_code,
            privacy_accepted=privacy_accepted,
        )
        self.db.add(client)
        await self.db.flush()  # получаем client.id без завершения транзакции, коммитит всегда сервис
        return client
    
    async def change_account_data(
        self,
        client_id: int,
        data: ClientUpdate,
    ) -> Client:
        client = await self.db.get(Client, client_id)
        if client is None:
            raise ValueError(f"Client {client_id} not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(client, field, value)

        await self.db.flush()
        return client
    
    async def change_legal_client_data(
        self,
        client_id: int,
        data: LegalClientUpdate,
    ) -> LegalClient:
        legal_client = await self.db.get(LegalClient, client_id)
        if legal_client is None:
            raise ValueError(
                f"У клиента {client_id} нет юр. профиля для обновления"
            )

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(legal_client, field, value)

        await self.db.flush()
        return legal_client