"""Тесты репозитория заявок клиента (client.repositories.request).

Юнит-часть идёт без БД (сессия подменяется заглушкой). Интеграционной части
нужна живая PostgreSQL с PostGIS и применённой миграцией cargo_requests —
иначе она пропускается (фикстура db_session в client/tests/conftest.py).

    docker compose exec backend uv run pytest client/tests -q
"""

from datetime import date
from typing import Any

import pytest
from geoalchemy2.elements import WKTElement
from sqlalchemy import func, select

from client.models.client import Client
from client.models.enums.client_types import ClientTypes
from client.models.enums.request_statuses import CargoRequestStatus
from client.models.request import CargoRequest
from client.repositories.request import CargoRequestRepository
from client.schemas.request import (
    CargoRequestCreate,
    CargoRequestLocation,
    CargoRequestUpdate,
)

MOSCOW_LNG, MOSCOW_LAT = 37.6173, 55.7558
TVER_LNG, TVER_LAT = 35.9119, 56.8587
LOADING_DATE = date(2026, 9, 25)

CREATE_PAYLOAD: dict[str, Any] = {
    "origin_address": "Москва, Ленинский проспект, 1",
    "origin_location": {"latitude": MOSCOW_LAT, "longitude": MOSCOW_LNG},
    "destination_address": "Тверь",
    "destination_location": {"latitude": TVER_LAT, "longitude": TVER_LNG},
    "cargo_type": "tent",
    "weight_kg": 12_000.0,
    "volume_m3": None,
    "vehicle_type": None,
    "loading_date": LOADING_DATE,
    "budget": None,
    "comment": None,
}


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
    """Заглушка AsyncSession: копит добавленные объекты и запросы."""

    def __init__(self, objects: list[Any] | None = None) -> None:
        self.objects = objects if objects is not None else []
        self.added: list[Any] = []
        self.flushed = 0
        self.statements: list[Any] = []

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    async def flush(self) -> None:
        self.flushed += 1

    async def execute(self, stmt: Any) -> _FakeResult:
        self.statements.append(stmt)
        return _FakeResult(self.objects)


def _make_request(
    client_id: int = 7, status: CargoRequestStatus = CargoRequestStatus.NEW
) -> CargoRequest:
    """ORM-объект заявки со всеми полями, но без БД."""
    request = CargoRequest(
        client_id=client_id,
        origin_address="Москва, Ленинский проспект, 1",
        origin_location=WKTElement(f"POINT({MOSCOW_LNG} {MOSCOW_LAT})", srid=4326),
        destination_address="Тверь",
        destination_location=WKTElement(f"POINT({TVER_LNG} {TVER_LAT})", srid=4326),
        cargo_type="tent",
        weight_kg=12_000.0,
        volume_m3=None,
        vehicle_type=None,
        loading_date=LOADING_DATE,
        budget=500.0,
        comment=None,
        status=status,
    )
    request.id = 42
    request.is_deleted = False
    return request


async def test_create_builds_wkt_points_and_just_flushes() -> None:
    """create переводит координаты в WKT (lng lat, SRID 4326) и не коммитит."""
    session = _FakeSession()
    repo = CargoRequestRepository(session)  # type: ignore[arg-type]

    request = await repo.create(7, CargoRequestCreate(**CREATE_PAYLOAD))

    assert request.client_id == 7
    assert request.origin_address == CREATE_PAYLOAD["origin_address"]
    assert request.origin_location.data == f"POINT({MOSCOW_LNG} {MOSCOW_LAT})"
    assert request.origin_location.srid == 4326
    assert request.destination_location.data == f"POINT({TVER_LNG} {TVER_LAT})"
    assert request.loading_date == LOADING_DATE
    assert session.added == [request]
    assert session.flushed == 1, "репозиторий только flush'ит — коммитит сервис"


async def test_update_applies_only_sent_fields() -> None:
    """Поля, которых нет в PATCH, не трогаем; nullable можно очистить."""
    session = _FakeSession()
    repo = CargoRequestRepository(session)  # type: ignore[arg-type]
    request = _make_request()

    await repo.update(request, CargoRequestUpdate(comment="Правка", budget=None))

    assert request.comment == "Правка"
    assert request.budget is None
    assert request.weight_kg == 12_000.0, "не переданное поле не менялось"
    assert request.destination_address == "Тверь"
    assert session.flushed == 1


async def test_update_moves_coordinates_to_geometry() -> None:
    """Координаты из PATCH пересобираются в WKT, вторую точку не трогаем."""
    session = _FakeSession()
    repo = CargoRequestRepository(session)  # type: ignore[arg-type]
    request = _make_request()

    await repo.update(
        request,
        CargoRequestUpdate(
            origin_location=CargoRequestLocation(latitude=1.0, longitude=2.0),
            vehicle_type=None,
        ),
    )

    assert request.origin_location.data == "POINT(2.0 1.0)"
    assert request.vehicle_type is None
    assert request.destination_location.data == f"POINT({TVER_LNG} {TVER_LAT})"


async def test_soft_delete_marks_row_instead_of_deleting() -> None:
    session = _FakeSession()
    repo = CargoRequestRepository(session)  # type: ignore[arg-type]
    request = _make_request()

    returned = await repo.soft_delete(request)

    assert returned is request
    assert request.is_deleted is True
    assert session.flushed == 1


async def test_get_owned_filters_by_owner_and_soft_delete_in_sql() -> None:
    """Владельца и признак удаления проверяем запросом, а не в Python."""
    session = _FakeSession()
    repo = CargoRequestRepository(session)  # type: ignore[arg-type]

    await repo.get_owned(7, 42)

    sql = str(session.statements[0].compile(compile_kwargs={"literal_binds": True}))
    assert "cargo_requests.client_id = 7" in sql
    assert "cargo_requests.id = 42" in sql
    assert "cargo_requests.is_deleted IS false" in sql


async def test_get_by_client_filters_deleted_and_paginates() -> None:
    session = _FakeSession()
    repo = CargoRequestRepository(session)  # type: ignore[arg-type]

    await repo.get_by_client(7, skip=20, limit=10)

    sql = str(session.statements[0].compile(compile_kwargs={"literal_binds": True}))
    assert "cargo_requests.client_id = 7" in sql
    assert "cargo_requests.is_deleted IS false" in sql
    assert "ORDER BY cargo_requests.created_at DESC" in sql
    assert "LIMIT 10 OFFSET 20" in sql


@pytest.mark.integration
async def test_create_persists_request_with_new_status(db_session, individual_client):
    """Созданная заявка получает статус new и лежит в БД вместе с геометрией."""
    repo = CargoRequestRepository(db_session)

    request = await repo.create(
        individual_client.id, CargoRequestCreate(**CREATE_PAYLOAD)
    )

    assert request.id is not None
    assert request.status is CargoRequestStatus.NEW

    stored = (
        await db_session.execute(
            select(
                func.ST_AsText(CargoRequest.origin_location),
                func.ST_AsText(CargoRequest.destination_location),
                func.ST_SRID(CargoRequest.destination_location),
            ).where(CargoRequest.id == request.id)
        )
    ).one()

    assert stored[0] == f"POINT({MOSCOW_LNG} {MOSCOW_LAT})"
    assert stored[1] == f"POINT({TVER_LNG} {TVER_LAT})"
    assert stored[2] == 4326


@pytest.mark.integration
async def test_get_owned_isolates_clients(db_session, individual_client):
    """Чужую заявку репозиторий не отдаёт: владелец проверяется в запросе."""
    repo = CargoRequestRepository(db_session)
    request = await repo.create(
        individual_client.id, CargoRequestCreate(**CREATE_PAYLOAD)
    )

    foreign_client = Client(
        name="Другой заказчик",
        phone_number="+375000000009",
        email="cargo_request_foreign@example.com",
        type=ClientTypes.individual,
    )
    db_session.add(foreign_client)
    await db_session.flush()

    owned = await repo.get_owned(individual_client.id, request.id)
    assert owned is not None and owned.id == request.id

    assert await repo.get_owned(foreign_client.id, request.id) is None
    assert await repo.get_owned(individual_client.id, request.id + 10_000) is None


@pytest.mark.integration
async def test_update_persists_edits_and_new_coordinates(db_session, individual_client):
    """PATCH сохраняет новые координаты и очищает nullable-поле в БД."""
    repo = CargoRequestRepository(db_session)
    request = await repo.create(
        individual_client.id, CargoRequestCreate(**CREATE_PAYLOAD)
    )

    await repo.update(
        request,
        CargoRequestUpdate(
            origin_location=CargoRequestLocation(latitude=1.0, longitude=2.0),
            comment="Заезд со двора",
            budget=None,
        ),
    )

    stored = (
        await db_session.execute(
            select(
                func.ST_AsText(CargoRequest.origin_location),
                CargoRequest.comment,
                CargoRequest.budget,
            ).where(CargoRequest.id == request.id)
        )
    ).one()

    # PostGIS нормализует WKT: хвостовые нули отбрасываются → "POINT(2 1)"
    assert stored[0] == "POINT(2 1)"
    assert stored[1] == "Заезд со двора"
    assert stored[2] is None


@pytest.mark.integration
async def test_soft_deleted_request_disappears_from_reads(db_session, individual_client):
    """Удалённая заявка пропадает из выборок, но строка в БД остаётся."""
    repo = CargoRequestRepository(db_session)
    first = await repo.create(
        individual_client.id, CargoRequestCreate(**CREATE_PAYLOAD)
    )
    second = await repo.create(
        individual_client.id, CargoRequestCreate(**CREATE_PAYLOAD)
    )

    await repo.soft_delete(first)

    listed = await repo.get_by_client(individual_client.id)
    assert [request.id for request in listed] == [second.id]
    assert await repo.get_owned(individual_client.id, first.id) is None

    stored = (
        await db_session.execute(
            select(CargoRequest.is_deleted).where(CargoRequest.id == first.id)
        )
    ).scalar_one()
    assert stored is True, "строка осталась в БД, но помечена удалённой"


