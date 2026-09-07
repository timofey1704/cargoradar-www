from fastapi import APIRouter, HTTPException, status

from core.dependencies import CurrentClient, DbSession

from client.exceptions import (
    ClientError,
    ClientNotLegalError,
    DuplicateFieldError,
)
from client.repositories.client import ClientRepository
from client.schemas.client_read import ClientRead
from client.schemas.client_update import (
    ClientUpdate,
    LegalClientUpdate,
    ProfileUpdateRequest,
)
from client.services.client_service import ClientService, build_client_read

router = APIRouter(prefix="/profile", tags=["client profile"])

_LEGAL_FIELDS = {"legal_name", "unp", "address"}

@router.patch("/update-data", response_model=ClientRead, status_code=status.HTTP_200_OK)
async def update_profile_data(
    data: ProfileUpdateRequest,
    current: CurrentClient,
    db: DbSession,
) -> ClientRead:
    """Обновляет профиль текущего клиента.

    Принимает плоское тело; обновляются только переданные поля. Приходят как
    обычные поля (name, email, ...), так и юридические (legal_name, unp, address) —
    для type=legal они уходят в таблицу legal_clients.
    """
    raw = data.model_dump(exclude_none=True)

    client_fields = {key: value for key, value in raw.items() if key not in _LEGAL_FIELDS}
    legal_fields = {
        key: value
        for key, value in raw.items()
        if key in _LEGAL_FIELDS and value not in ("", None)
    }

    if not client_fields and not legal_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нужно передать хотя бы одно поле для обновления",
        )

    client_data = ClientUpdate(**client_fields) if client_fields else None
    legal_data = LegalClientUpdate(**legal_fields) if legal_fields else None

    service = ClientService(db=db, client_repo=ClientRepository(db))

    try:
        client = await service.update_profile(
            client=current,
            client_data=client_data,
            legal_data=legal_data,
        )
    except ClientNotLegalError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Аккаунт не является юридическим лицом",
        ) from None
    except DuplicateFieldError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Поле '{exc.field}' уже занято",
        ) from exc
    except ClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return await build_client_read(client, db)
