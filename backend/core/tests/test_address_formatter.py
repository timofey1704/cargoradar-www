"""Проверяем форматтер адресов Nominatim: display_name -> "Страна, Город, Улица Дом"."""

from datetime import date, datetime, timezone

import pytest

from client.models.enums.request_statuses import CargoRequestStatus
from core.schemas.chat import OrderBriefRead
from utils.address_formatter import format_address

NOMINATIM = "41, улица Одинцова, Запад, Фрунзенский район, Минск, 220018, Беларусь"
SHORT = "Беларусь, Минск, Одинцова 41"
NOW = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # пример из задачи
        (
            "41, улица Одинцова, Запад, Фрунзенский район, Минск, 220018, Беларусь",
            "Беларусь, Минск, Одинцова 41",
        ),
        # без квартала
        (
            "41, улица Одинцова, Минск, 220018, Беларусь",
            "Беларусь, Минск, Одинцова 41",
        ),
        # без номера дома
        (
            "улица Одинцова, Минск, 220018, Беларусь",
            "Беларусь, Минск, Одинцова",
        ),
        # область между городом и страной отбрасываем
        (
            "10, проспект Независимости, Минск, Минская область, 220030, Беларусь",
            "Беларусь, Минск, Независимости 10",
        ),
        # буква в номере дома
        (
            "12А, улица Ленина, Гомель, 246000, Беларусь",
            "Беларусь, Гомель, Ленина 12А",
        ),
    ],
)
def test_format_address_cuts_nominatim_display_name(raw: str, expected: str) -> None:
    assert format_address(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "Минск",  # одна часть — сокращать нечего
        "Минск, ул. Складская 1",  # пользовательский формат, не Nominatim
        "Москва, Россия",  # две части — недостаточно признаков Nominatim
        "Беларусь, Минск, Одинцова 41",  # уже сокращённый — идемпотентность
        "",  # пустая строка
    ],
)
def test_format_address_keeps_unknown_formats(raw: str) -> None:
    assert format_address(raw) == raw


def test_route_read_formats_points() -> None:
    from core.schemas.search.route import RouteRead

    route = RouteRead(
        id=1, executor_id=2, point_a=NOMINATIM, point_b="Брест", created_at=NOW
    )

    assert route.point_a == SHORT
    assert route.point_b == "Брест"


def test_search_request_read_formats_addresses() -> None:
    from core.schemas.search.request import CargoRequestRead

    request = CargoRequestRead(
        id=1,
        client_id=2,
        status=CargoRequestStatus.NEW,
        origin_address=NOMINATIM,
        destination_address="Брест",
        cargo_type="Тент",
        weight_kg=1000.0,
        loading_date=date(2026, 9, 5),
        created_at=NOW,
    )

    assert request.origin_address == SHORT
    assert request.destination_address == "Брест"


def test_client_request_read_formats_addresses() -> None:
    from client.schemas.request import CargoRequestRead

    request = CargoRequestRead(
        id=1,
        client_id=2,
        status=CargoRequestStatus.NEW,
        origin_address=NOMINATIM,
        destination_address="Брест",
        cargo_type="Тент",
        weight_kg=1000.0,
        loading_date=date(2026, 9, 5),
        created_at=NOW,
        updated_at=NOW,
    )

    assert request.origin_address == SHORT
    assert request.destination_address == "Брест"


def test_order_brief_read_formats_addresses() -> None:
    order = OrderBriefRead(
        id=1,
        origin_address=NOMINATIM,
        destination_address="Брест",
        cargo_type="Тент",
    )

    assert order.origin_address == SHORT
    assert order.destination_address == "Брест"
