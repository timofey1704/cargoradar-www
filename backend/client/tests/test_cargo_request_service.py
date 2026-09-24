"""Юнит-тесты схем и сервиса заявок клиента на перевозку (CargoRequest).

БД не нужна: AsyncSession подменяется заглушкой, поэтому тесты идут и без
PostGIS. Проверки самого репозитория на живой БД — в
client/tests/test_cargo_request_repository.py.

    docker compose exec backend uv run pytest client/tests -q
"""

from datetime import date, datetime, timezone
from typing import Any

import pytest
from pydantic import ValidationError

from client.exceptions import (
    CargoRequestNotDeletableError,
    CargoRequestNotEditableError,
    CargoRequestNotFoundError,
)
from client.models.enums.request_statuses import CargoRequestStatus
from client.models.request import CargoRequest
from client.schemas.request import (
    CargoRequestCreate,
    CargoRequestDeleted,
    CargoRequestLocation,
    CargoRequestPageRead,
    CargoRequestRead,
    CargoRequestUpdate,
)
from client.services.request_service import (
    DELETABLE_STATUSES,
    EDITABLE_STATUSES,
    CargoRequestService,
)

CREATE_PAYLOAD: dict[str, Any] = {
    "origin_address": "Москва, Ленинский проспект, 1",
    "origin_location": {"latitude": 55.7558, "longitude": 37.6173},
    "destination_address": "Тверь",
    "destination_location": {"latitude": 56.8587, "longitude": 35.9119},
    "cargo_type": "tent",
    "weight_kg": 12_000.0,
    "volume_m3": None,
    "vehicle_type": None,
    "loading_date": date(2026, 9, 25),
    "budget": None,
    "comment": None,
}

REQUEST_ID = 42
CLIENT_ID = 7


def _make_request(
    status: CargoRequestStatus = CargoRequestStatus.NEW,
    client_id: int = CLIENT_ID,
) -> CargoRequest:
    """ORM-объект заявки без БД: только атрибуты, которые читают схемы/сервис."""
    request = CargoRequest(
        client_id=client_id,
        origin_address="Москва, Ленинский проспект, 1",
        destination_address="Тверь",
        cargo_type="tent",
        weight_kg=12_000.0,
        volume_m3=None,
        vehicle_type=None,
        loading_date=date(2026, 9, 25),
        budget=None,
        comment=None,
        status=status,
    )
    request.id = REQUEST_ID
    request.is_deleted = False
    request.created_at = datetime(2026, 9, 24, 10, 0, tzinfo=timezone.utc)
    request.updated_at = request.created_at
    return request


class _FakeResult:
    """Заглушка результата execute: отдаёт заранее заданные объекты."""

    def __init__(self, objects: list[Any]) -> None:
        self._objects = objects

    def scalar_one_or_none(self) -> Any:
        return self._objects[0] if self._objects else None

    def scalars(self) -> "_FakeResult":
        return self

    def all(self) -> list[Any]:
        return list(self._objects)


class _FakeSession:
    """Заглушка AsyncSession: считает flush/commit и отдаёт заявку на execute."""

    def __init__(self, objects: list[Any] | None = None) -> None:
        self.objects = objects if objects is not None else []
        self.added: list[Any] = []
        self.flushed = 0
        self.commits = 0
        self.refreshed: list[Any] = []

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    async def flush(self) -> None:
        self.flushed += 1

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        pass

    async def refresh(self, obj: Any) -> None:
        self.refreshed.append(obj)

    async def execute(self, stmt: Any) -> _FakeResult:
        return _FakeResult(self.objects)


def test_create_schema_accepts_frontend_payload() -> None:
    """Create-схема принимает точки как {latitude, longitude} — форму фронта."""
    data = CargoRequestCreate(**CREATE_PAYLOAD)

    assert data.loading_date == date(2026, 9, 25)
    assert data.origin_location.longitude == 37.6173
    assert data.volume_m3 is None


def test_create_schema_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        CargoRequestCreate(**{**CREATE_PAYLOAD, "unexpected": 1})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("latitude", 90.5),
        ("latitude", -90.5),
        ("longitude", 180.5),
        ("longitude", -180.5),
    ],
)
def test_location_bounds_are_validated(field: str, value: float) -> None:
    with pytest.raises(ValidationError):
        CargoRequestLocation(**{"latitude": 0.0, "longitude": 0.0, field: value})


def test_update_requires_at_least_one_field() -> None:
    with pytest.raises(ValidationError):
        CargoRequestUpdate()


@pytest.mark.parametrize(
    "payload",
    [
        {"origin_address": None},
        {"origin_location": None},
        {"destination_address": None},
        {"destination_location": None},
        {"cargo_type": None},
        {"weight_kg": None},
        {"loading_date": None},
    ],
)
def test_update_rejects_null_for_not_null_columns(payload: dict[str, Any]) -> None:
    """В модели это NOT NULL — явный null должен падать на валидации, а не в БД."""
    with pytest.raises(ValidationError):
        CargoRequestUpdate(**payload)


def test_update_allows_clearing_nullable_fields() -> None:
    data = CargoRequestUpdate(
        volume_m3=None, vehicle_type=None, budget=None, comment=None
    )

    assert data.model_dump(exclude_unset=True) == {
        "volume_m3": None,
        "vehicle_type": None,
        "budget": None,
        "comment": None,
    }


def test_update_dumps_only_sent_fields() -> None:
    data = CargoRequestUpdate(comment="Новый комментарий", weight_kg=500.0)

    assert data.model_dump(exclude_unset=True) == {
        "comment": "Новый комментарий",
        "weight_kg": 500.0,
    }


def test_read_schema_maps_orm_object() -> None:
    read = CargoRequestRead.model_validate(_make_request())

    assert read.id == REQUEST_ID
    assert read.client_id == CLIENT_ID
    assert read.status is CargoRequestStatus.NEW
    assert read.volume_m3 is None
    assert read.updated_at == datetime(2026, 9, 24, 10, 0, tzinfo=timezone.utc)


def test_deleted_schema_maps_orm_object() -> None:
    request = _make_request()
    request.is_deleted = True

    deleted = CargoRequestDeleted.model_validate(request)

    assert deleted.id == REQUEST_ID
    assert deleted.is_deleted is True


def test_page_schema_wraps_items() -> None:
    page = CargoRequestPageRead(
        items=[CargoRequestRead.model_validate(_make_request())],
        total=None,
        skip=0,
        limit=20,
        has_more=False,
    )

    assert page.items[0].id == REQUEST_ID


def test_status_rules() -> None:
    """Править можно только новую заявку; удалять — новую и отменённую."""
    assert EDITABLE_STATUSES == {CargoRequestStatus.NEW}
    assert DELETABLE_STATUSES == {CargoRequestStatus.NEW, CargoRequestStatus.CANCELLED}


async def test_get_returns_owned_request() -> None:
    request = _make_request()
    session = _FakeSession([request])
    service = CargoRequestService(db=session)  # type: ignore[arg-type]

    read = await service.get(CLIENT_ID, REQUEST_ID)

    assert read.id == REQUEST_ID
    assert read.status is CargoRequestStatus.NEW


async def test_get_raises_not_found_when_request_is_missing_or_foreign() -> None:
    """Репозиторий ничего не нашёл (нет заявки / чужая / удалённая) — 404."""
    session = _FakeSession([])
    service = CargoRequestService(db=session)  # type: ignore[arg-type]

    with pytest.raises(CargoRequestNotFoundError) as exc_info:
        await service.get(CLIENT_ID, REQUEST_ID)

    assert exc_info.value.request_id == REQUEST_ID


@pytest.mark.parametrize(
    "status",
    [
        CargoRequestStatus.IN_PROGRESS,
        CargoRequestStatus.COMPLETED,
        CargoRequestStatus.CANCELLED,
    ],
)
async def test_update_rejects_not_editable_status(status: CargoRequestStatus) -> None:
    session = _FakeSession([_make_request(status)])
    service = CargoRequestService(db=session)  # type: ignore[arg-type]

    with pytest.raises(CargoRequestNotEditableError) as exc_info:
        await service.update(CLIENT_ID, REQUEST_ID, CargoRequestUpdate(comment="нельзя"))

    assert exc_info.value.status == status.value
    assert session.commits == 0, "без изменений коммитить нечего"


@pytest.mark.parametrize(
    "status", [CargoRequestStatus.IN_PROGRESS, CargoRequestStatus.COMPLETED]
)
async def test_delete_rejects_running_or_completed(status: CargoRequestStatus) -> None:
    session = _FakeSession([_make_request(status)])
    service = CargoRequestService(db=session)  # type: ignore[arg-type]

    with pytest.raises(CargoRequestNotDeletableError) as exc_info:
        await service.delete(CLIENT_ID, REQUEST_ID)

    assert exc_info.value.status == status.value
    assert session.commits == 0


async def test_create_commits_and_returns_read(monkeypatch: pytest.MonkeyPatch) -> None:
    """Сервис коммитит и обновляет объект, чтобы отдать server_default-поля."""
    session = _FakeSession([])
    service = CargoRequestService(db=session)  # type: ignore[arg-type]
    created = _make_request()

    async def fake_create(client_id: int, data: CargoRequestCreate) -> CargoRequest:
        created.client_id = client_id
        return created

    monkeypatch.setattr(service.repository, "create", fake_create)

    read = await service.create(CLIENT_ID, CargoRequestCreate(**CREATE_PAYLOAD))

    assert read.id == REQUEST_ID
    assert read.client_id == CLIENT_ID
    assert session.commits == 1
    assert session.refreshed == [created]


async def test_update_applies_fields_and_commits() -> None:
    request = _make_request()
    request.budget = 500.0
    session = _FakeSession([request])
    service = CargoRequestService(db=session)  # type: ignore[arg-type]

    read = await service.update(
        CLIENT_ID, REQUEST_ID, CargoRequestUpdate(comment="Правка", budget=None)
    )

    assert read.comment == "Правка"
    assert read.budget is None, "nullable-поле очищено"
    assert read.weight_kg == 12_000.0, "не переданное поле не менялось"
    assert session.flushed == 1
    assert session.commits == 1
    assert session.refreshed == [request]


async def test_delete_soft_deletes_and_commits() -> None:
    request = _make_request()
    session = _FakeSession([request])
    service = CargoRequestService(db=session)  # type: ignore[arg-type]

    result = await service.delete(CLIENT_ID, REQUEST_ID)

    assert result.is_deleted is True
    assert request.is_deleted is True, "строка не удаляется физически"
    assert session.flushed == 1
    assert session.commits == 1
    assert session.refreshed == [request]


async def test_list_by_client_builds_page() -> None:
    request = _make_request()
    session = _FakeSession([request])
    service = CargoRequestService(db=session)  # type: ignore[arg-type]

    page = await service.list_by_client(CLIENT_ID, skip=0, limit=20)

    assert [item.id for item in page.items] == [REQUEST_ID]
    assert page.skip == 0
    assert page.limit == 20
    assert page.has_more is False


