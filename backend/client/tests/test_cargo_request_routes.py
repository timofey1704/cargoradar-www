"""Проверяем роуты заявок клиента: регистрацию, контракт и передачу в сервис.

Роуты вызываем напрямую (как в core/tests/test_search_routes.py), подменяя
сервис — HTTP-слой здесь не нужен. Путь и схему проверяем по OpenAPI приложения.

    docker compose exec backend uv run pytest client/tests -q
"""

from datetime import date, datetime, timezone
from typing import Any

import pytest
from fastapi import HTTPException

from client.exceptions import (
    CargoRequestNotDeletableError,
    CargoRequestNotEditableError,
    CargoRequestNotFoundError,
    ClientError,
)
from client.models.client import Client
from client.models.enums.client_types import ClientTypes
from client.models.enums.request_statuses import CargoRequestStatus
from client.routes.request import (
    create_client_order,
    delete_client_order,
    get_client_order,
    get_client_orders,
    update_client_order,
)
from client.schemas.request import (
    CargoRequestCreate,
    CargoRequestDeleted,
    CargoRequestPageRead,
    CargoRequestRead,
    CargoRequestUpdate,
)
from client.services.request_service import CargoRequestService
from main import app

ORDERS_PATH = "/api/client/orders"
ORDER_PATH = "/api/client/orders/{request_id}"

CLIENT_ID = 7
REQUEST_ID = 42

NOW = datetime(2026, 9, 24, 10, 0, tzinfo=timezone.utc)

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


def _current() -> Client:
    """Клиент без БД: из current роут использует только id."""
    return Client(
        id=CLIENT_ID,
        name="Заказчик",
        phone_number="+375000000010",
        email="client_routes_test@example.com",
        type=ClientTypes.individual,
    )


def _read(request_id: int = REQUEST_ID) -> CargoRequestRead:
    return CargoRequestRead(
        id=request_id,
        client_id=CLIENT_ID,
        status=CargoRequestStatus.NEW,
        origin_address="Москва, Ленинский проспект, 1",
        destination_address="Тверь",
        cargo_type="tent",
        weight_kg=12_000.0,
        loading_date=date(2026, 9, 25),
        created_at=NOW,
        updated_at=NOW,
    )


def _deleted() -> CargoRequestDeleted:
    return CargoRequestDeleted(
        id=REQUEST_ID,
        status=CargoRequestStatus.NEW,
        is_deleted=True,
        updated_at=NOW,
    )


def test_client_order_routes_are_registered() -> None:
    """Пять операций видны в OpenAPI — значит, роут подключён к приложению."""
    paths = app.openapi()["paths"]

    assert ORDERS_PATH in paths, "коллекция заказов не зарегистрирована"
    assert ORDER_PATH in paths, "роут одиночной заявки не зарегистрирован"
    assert {"get", "post"} <= set(paths[ORDERS_PATH])
    assert {"get", "patch", "delete"} <= set(paths[ORDER_PATH])


def test_client_order_routes_require_authentication() -> None:
    """У каждой операции объявлен security — доступ только по access-токену."""
    paths = app.openapi()["paths"]

    for path, methods in (
        (ORDERS_PATH, ("get", "post")),
        (ORDER_PATH, ("get", "patch", "delete")),
    ):
        for method in methods:
            operation = paths[path][method]
            assert operation.get("security"), f"у {method.upper()} {path} нет auth"


def test_list_operation_returns_plain_array() -> None:
    """GET отдаёт массив CargoRequestRead — контракт lib/api/client/orders.ts."""
    operation = app.openapi()["paths"][ORDERS_PATH]["get"]
    schema = operation["responses"]["200"]["content"]["application/json"]["schema"]

    assert schema["type"] == "array"
    assert schema["items"]["$ref"].endswith("CargoRequestRead")


def test_create_operation_returns_201() -> None:
    responses = app.openapi()["paths"][ORDERS_PATH]["post"]["responses"]

    assert "201" in responses, "создание заявки должно возвращать 201"


def test_update_and_delete_operations_return_success() -> None:
    paths = app.openapi()["paths"]

    assert "200" in paths[ORDER_PATH]["patch"]["responses"]
    assert "200" in paths[ORDER_PATH]["delete"]["responses"]


async def test_list_route_unwraps_page_for_frontend(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Фронт ждёт массив (CargoRequest[]), а не страницу — route разворачивает items."""
    page = CargoRequestPageRead(items=[_read()], skip=3, limit=5, has_more=True)
    captured: dict[str, object] = {}

    async def fake_list_by_client(
        self, client_id: int, *, skip: int = 0, limit: int = 20
    ) -> CargoRequestPageRead:
        captured.update({"client_id": client_id, "skip": skip, "limit": limit})
        return page

    monkeypatch.setattr(CargoRequestService, "list_by_client", fake_list_by_client)

    result = await get_client_orders(
        current=_current(), db=None, skip=3, limit=5  # type: ignore[arg-type]
    )

    assert result == page.items
    assert captured == {"client_id": CLIENT_ID, "skip": 3, "limit": 5}


async def test_list_route_uses_default_pagination(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Без query-параметров пагинация приходит с дефолтами сервиса."""
    captured: dict[str, object] = {}

    async def fake_list_by_client(
        self, client_id: int, *, skip: int = 0, limit: int = 20
    ) -> CargoRequestPageRead:
        captured.update({"skip": skip, "limit": limit})
        return CargoRequestPageRead(items=[], skip=skip, limit=limit, has_more=False)

    monkeypatch.setattr(CargoRequestService, "list_by_client", fake_list_by_client)

    await get_client_orders(current=_current(), db=None)  # type: ignore[arg-type]

    assert captured == {"skip": 0, "limit": 20}


async def test_create_route_forwards_client_and_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = _read()
    captured: dict[str, object] = {}

    async def fake_create(
        self, client_id: int, data: CargoRequestCreate
    ) -> CargoRequestRead:
        captured.update({"client_id": client_id, "payload": data})
        return expected

    monkeypatch.setattr(CargoRequestService, "create", fake_create)

    result = await create_client_order(
        data=CargoRequestCreate(**CREATE_PAYLOAD),
        current=_current(),
        db=None,  # type: ignore[arg-type]
    )

    assert result is expected
    assert captured["client_id"] == CLIENT_ID
    payload = captured["payload"]
    assert isinstance(payload, CargoRequestCreate)
    assert payload.origin_address == CREATE_PAYLOAD["origin_address"]


async def test_get_route_forwards_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = _read()
    captured: dict[str, int] = {}

    async def fake_get(self, client_id: int, request_id: int) -> CargoRequestRead:
        captured.update({"client_id": client_id, "request_id": request_id})
        return expected

    monkeypatch.setattr(CargoRequestService, "get", fake_get)

    result = await get_client_order(
        request_id=REQUEST_ID, current=_current(), db=None  # type: ignore[arg-type]
    )

    assert result is expected
    assert captured == {"client_id": CLIENT_ID, "request_id": REQUEST_ID}


async def test_update_route_forwards_client_and_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = _read()
    data = CargoRequestUpdate(comment="Правка")
    captured: dict[str, object] = {}

    async def fake_update(
        self, client_id: int, request_id: int, update: CargoRequestUpdate
    ) -> CargoRequestRead:
        captured.update(
            {"client_id": client_id, "request_id": request_id, "payload": update}
        )
        return expected

    monkeypatch.setattr(CargoRequestService, "update", fake_update)

    result = await update_client_order(
        request_id=REQUEST_ID, data=data, current=_current(), db=None  # type: ignore[arg-type]
    )

    assert result is expected
    assert captured == {
        "client_id": CLIENT_ID,
        "request_id": REQUEST_ID,
        "payload": data,
    }


async def test_delete_route_returns_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = _deleted()
    captured: dict[str, int] = {}

    async def fake_delete(self, client_id: int, request_id: int) -> CargoRequestDeleted:
        captured.update({"client_id": client_id, "request_id": request_id})
        return expected

    monkeypatch.setattr(CargoRequestService, "delete", fake_delete)

    result = await delete_client_order(
        request_id=REQUEST_ID, current=_current(), db=None  # type: ignore[arg-type]
    )

    assert result is expected
    assert result.is_deleted is True
    assert captured == {"client_id": CLIENT_ID, "request_id": REQUEST_ID}


async def test_get_route_maps_missing_or_foreign_request_to_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Нет заявки / она чужая / удалена → 404 с одинаковым текстом."""

    async def fake_get(self, client_id: int, request_id: int) -> CargoRequestRead:
        raise CargoRequestNotFoundError(request_id)

    monkeypatch.setattr(CargoRequestService, "get", fake_get)

    with pytest.raises(HTTPException) as exc_info:
        await get_client_order(
            request_id=REQUEST_ID, current=_current(), db=None  # type: ignore[arg-type]
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Заявка не найдена"


async def test_update_route_maps_busy_status_to_409(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Заявка в работе → 409, в тексте виден текущий статус."""

    async def fake_update(
        self, client_id: int, request_id: int, update: CargoRequestUpdate
    ) -> CargoRequestRead:
        raise CargoRequestNotEditableError(request_id, "in_progress")

    monkeypatch.setattr(CargoRequestService, "update", fake_update)

    with pytest.raises(HTTPException) as exc_info:
        await update_client_order(
            request_id=REQUEST_ID,
            data=CargoRequestUpdate(comment="нельзя"),
            current=_current(),
            db=None,  # type: ignore[arg-type]
        )

    assert exc_info.value.status_code == 409
    assert "in_progress" in str(exc_info.value.detail)


async def test_delete_route_maps_busy_status_to_409(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Выполненную заявку удалить нельзя → 409."""

    async def fake_delete(self, client_id: int, request_id: int) -> CargoRequestDeleted:
        raise CargoRequestNotDeletableError(request_id, "completed")

    monkeypatch.setattr(CargoRequestService, "delete", fake_delete)

    with pytest.raises(HTTPException) as exc_info:
        await delete_client_order(
            request_id=REQUEST_ID, current=_current(), db=None  # type: ignore[arg-type]
        )

    assert exc_info.value.status_code == 409
    assert "completed" in str(exc_info.value.detail)


async def test_routes_map_unknown_domain_error_to_400(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Любая другая доменная ошибка сервиса не утекает 500-м."""

    async def fake_get(self, client_id: int, request_id: int) -> CargoRequestRead:
        raise ClientError("Не удалось сохранить заявку")

    monkeypatch.setattr(CargoRequestService, "get", fake_get)

    with pytest.raises(HTTPException) as exc_info:
        await get_client_order(
            request_id=REQUEST_ID, current=_current(), db=None  # type: ignore[arg-type]
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Не удалось сохранить заявку"



