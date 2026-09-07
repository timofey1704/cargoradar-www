from pathlib import Path

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.repositories.subscription_repository import SubscriptionRepository

from client.models.client import Client
from client.models.enums.client_types import ClientTypes
from client.models.legal_client import LegalClient
from client.repositories.client import ClientRepository
from client.schemas.client_read import ClientRead, SubscriptionRead
from client.schemas.client_update import ClientUpdate, LegalClientUpdate
from client.exceptions import (
    ClientError,
    ClientNotFoundError,
    ClientNotLegalError,
    DuplicateFieldError,
)

UPLOAD_DIR = Path("uploads/clients/")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


_UNIQUE_CONSTRAINT_FIELD_MAP = {
    "clients_email_key": "email",
    "clients_phone_number_key": "phone_number",
    "clients_vin_code_key": "VIN_code",
    "legal_clients_unp_key": "unp",
}

class ClientService:
    def __init__(self, db: AsyncSession, client_repo: ClientRepository) -> None:
        self.db = db
        self.client_repo = client_repo
        
    async def get_client(self, client_id: int) -> Client:
        client = await self.client_repo.get_by_id(client_id)
        if client is None:
            raise ClientNotFoundError(client_id)
        return client

    async def update_profile(
        self,
        client: Client,
        client_data: ClientUpdate | None = None,
        legal_data: LegalClientUpdate | None = None,
    ) -> Client:
        wants_client_update = client_data is not None and client_data.model_fields_set
        wants_legal_update = legal_data is not None and legal_data.model_fields_set

        if wants_legal_update and client.type != ClientTypes.legal:
            raise ClientNotLegalError(client.id)

        try:
            if wants_client_update:
                assert client_data is not None
                await self.client_repo.change_account_data(client.id, client_data)

            if wants_legal_update:
                assert legal_data is not None
                await self.client_repo.change_legal_client_data(client.id, legal_data)

            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise self._translate_integrity_error(exc) from exc

        await self.db.refresh(client)
        return client

    @staticmethod
    def _translate_integrity_error(exc: IntegrityError) -> ClientError:
        constraint = getattr(exc.orig, "constraint_name", None) or str(exc.orig)
        for name, field in _UNIQUE_CONSTRAINT_FIELD_MAP.items():
            if name in str(constraint):
                return DuplicateFieldError(field)
        return ClientError("Не удалось сохранить изменения")


async def build_client_read(client: Client, db: AsyncSession) -> ClientRead:
    """Собирает ClientRead из объекта клиента, включая юрданные для type=legal

    Используется и в GET /auth/me, и в PATCH /profile/update-data, чтобы оба
    эндпоинта возвращали профиль одинакового вида (со подпиской и юрданными)
    """
    subscription_repo = SubscriptionRepository(db)
    active_subscription = await subscription_repo.get_active_for_client(client.id)

    # грузим явно (relationship не eager loaded,
    # а ленивая загрузка в async сессии бросила бы MissingGreenlet).
    legal_client = None
    if client.type == ClientTypes.legal:
        legal_client = await db.get(LegalClient, client.id)

    return ClientRead(
        id=client.id,
        name=client.name,
        email=client.email,
        phone_number=client.phone_number,
        type=client.type,
        VIN_code=client.VIN_code,
        image_url=client.image_url,
        is_notifications_enabled=client.is_notifications_enabled,
        is_active=client.is_active,
        subscription=SubscriptionRead.model_validate(active_subscription) if active_subscription else None,
        legal_name=legal_client.legal_name if legal_client else None,
        unp=legal_client.unp if legal_client else None,
        address=legal_client.address if legal_client else None,
    )