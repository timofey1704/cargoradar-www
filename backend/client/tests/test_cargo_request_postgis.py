"""Интеграционные тесты схемы грузовых заявок (client.models.request.CargoRequest).

Нужны живой PostgreSQL с расширением PostGIS (образ postgis/postgis) и
применённая миграция cargo_requests. Если БД недоступна — тесты пропускаются.

    docker compose exec backend uv run pytest client/tests -q
"""

import datetime
from typing import Any

import pytest
from geoalchemy2 import Geography
from geoalchemy2.elements import WKTElement
from sqlalchemy import cast, func, select, text
from sqlalchemy.exc import DBAPIError, IntegrityError

from client.models.enums.request_statuses import CargoRequestStatus
from client.models.request import CargoRequest
from client.repositories.request import find_requests_near_route
from executor.models.route import Route

pytestmark = pytest.mark.integration

TABLE = "cargo_requests"

# Москва и Тверь — заведомо разные точки примерно в 170 км друг от друга
MOSCOW_LNG, MOSCOW_LAT = 37.6173, 55.7558
TVER_LNG, TVER_LAT = 35.9119, 56.8587

LOADING_DATE = datetime.date(2026, 9, 25)


def _point(lng: float, lat: float, srid: int = 4326) -> WKTElement:
    """WKT-точка в порядке (lng lat) — так PostGIS хранит WGS84-геометрию."""
    return WKTElement(f"POINT({lng} {lat})", srid=srid)


async def _add_request(session, client_id: int, **overrides) -> CargoRequest:
    params: dict[str, Any] = {
        "client_id": client_id,
        "origin_address": "Москва, Ленинский проспект, 1",
        "origin_location": _point(MOSCOW_LNG, MOSCOW_LAT),
        "destination_address": "Тверь",
        "destination_location": _point(TVER_LNG, TVER_LAT),
        "cargo_type": "tent",
        "weight_kg": 12_000.0,
        "loading_date": LOADING_DATE,
    }
    params.update(overrides)
    request = CargoRequest(**params)
    session.add(request)
    await session.flush()
    await session.refresh(request)
    return request


async def _add_route(session, executor_id: int, path: WKTElement | None = None) -> Route:
    route = Route(
        executor_id=executor_id,
        point_a="Москва",
        point_b="Тверь",
        point_a_location=_point(MOSCOW_LNG, MOSCOW_LAT),
        point_b_location=_point(TVER_LNG, TVER_LAT),
        path=path,
    )
    session.add(route)
    await session.flush()
    await session.refresh(route)
    return route


async def test_geometry_columns_are_registered_in_postgis(db_session):
    """Колонки точек заявки зарегистрированы в PostGIS как POINT с SRID 4326."""
    rows = (
        await db_session.execute(
            text(
                "SELECT f_geometry_column, coord_dimension, srid, type "
                "FROM geometry_columns WHERE f_table_name = :table "
                "ORDER BY f_geometry_column"
            ),
            {"table": TABLE},
        )
    ).all()

    assert [(r.f_geometry_column, r.coord_dimension, r.srid, r.type) for r in rows] == [
        ("destination_location", 2, 4326, "POINT"),
        ("origin_location", 2, 4326, "POINT"),
    ]


async def test_geo_columns_have_gist_indexes(db_session):
    """Под пространственные фильтры есть GiST-индексы (ST_DWithin / ST_Distance)."""
    indexes = (
        await db_session.execute(
            text(
                "SELECT indexname FROM pg_indexes "
                "WHERE tablename = :table AND indexdef ILIKE '%USING gist%'"
            ),
            {"table": TABLE},
        )
    ).scalars().all()

    assert set(indexes) == {
        "idx_cargo_requests_origin_location",
        "idx_cargo_requests_destination_location",
    }


def _normalize_predicate(predicate: str) -> str:
    """Убираем скобки и каст enum — Postgres рендерит предикат по-своему."""
    return (
        predicate.replace("(", "").replace(")", "").replace("::cargo_request_status", "").strip()
    )


async def test_partial_indexes_filter_deleted_and_non_new_rows(db_session):
    """Частичные индексы покрывают только неудалённые строки, а по дате — только новые заявки."""
    rows = (
        await db_session.execute(
            text(
                "SELECT indexname, indexdef FROM pg_indexes "
                "WHERE tablename = :table AND indexdef ILIKE '%WHERE%'"
            ),
            {"table": TABLE},
        )
    ).all()

    predicates = {}
    for row in rows:
        _, _, predicate = row.indexdef.partition(" WHERE ")
        predicates[row.indexname] = _normalize_predicate(predicate)

    assert predicates == {
        "ix_cargo_requests_feed": "NOT is_deleted",
        "ix_cargo_requests_client_created": "NOT is_deleted",
        "ix_cargo_requests_loading_date": "NOT is_deleted AND status = 'new'",
    }


async def test_status_enum_uses_lowercase_values(db_session):
    """В БД лежат значения enum, а не имена членов (иначе ломается server_default 'new')."""
    labels = (
        await db_session.execute(
            text(
                "SELECT enumlabel FROM pg_enum e JOIN pg_type t ON t.oid = e.enumtypid "
                "WHERE t.typname = 'cargo_request_status' ORDER BY e.enumsortorder"
            )
        )
    ).scalars().all()

    assert labels == ["new", "in_progress", "completed", "cancelled"]


async def test_status_default_is_new(db_session, individual_client):
    """Без явного статуса заявка создаётся новой — default и server_default совпадают."""
    request = await _add_request(db_session, individual_client.id)

    stored = (
        await db_session.execute(
            text("SELECT status::text FROM cargo_requests WHERE id = :id"), {"id": request.id}
        )
    ).scalar_one()

    assert stored == "new"
    assert request.status is CargoRequestStatus.NEW


async def test_coordinates_roundtrip_through_orm(db_session, individual_client):
    """Координаты сохраняются и читаются обратно как корректные WGS84-точки."""
    request = await _add_request(db_session, individual_client.id)
    assert request.id is not None
    assert request.is_deleted is False, "значение по умолчанию из модели"

    stored = (
        await db_session.execute(
            select(
                func.ST_AsText(CargoRequest.origin_location),
                func.ST_AsText(CargoRequest.destination_location),
                func.ST_SRID(CargoRequest.destination_location),
                func.GeometryType(CargoRequest.origin_location),
            ).where(CargoRequest.id == request.id)
        )
    ).one()

    assert stored[0] == f"POINT({MOSCOW_LNG} {MOSCOW_LAT})"
    assert stored[1] == f"POINT({TVER_LNG} {TVER_LAT})"
    assert stored[2] == 4326
    assert stored[3] == "POINT"


async def test_request_is_found_by_point_nearby(db_session, individual_client):
    """Поиск заявок рядом с точкой (ST_DWithin по точке загрузки) — сценарий карты."""
    request = await _add_request(db_session, individual_client.id)
    near_moscow = func.ST_GeomFromText(f"POINT({MOSCOW_LNG + 0.01} {MOSCOW_LAT})", 4326)

    found = (
        await db_session.execute(
            select(CargoRequest.id).where(
                func.ST_DWithin(CargoRequest.origin_location, near_moscow, 0.05)
            )
        )
    ).scalars().all()
    assert found == [request.id]

    far_point = func.ST_GeomFromText("POINT(0 0)", 4326)
    not_found = (
        await db_session.execute(
            select(CargoRequest.id).where(
                func.ST_DWithin(CargoRequest.origin_location, far_point, 0.05)
            )
        )
    ).scalars().all()
    assert not_found == []


async def test_distance_between_points_is_calculated(db_session, individual_client):
    """PostGIS считает расстояние между точками заявки (Москва → Тверь ≈ 170 км)."""
    request = await _add_request(db_session, individual_client.id)

    distance_m = (
        await db_session.execute(
            select(
                func.ST_Distance(
                    cast(CargoRequest.origin_location, Geography),
                    cast(CargoRequest.destination_location, Geography),
                )
            ).where(CargoRequest.id == request.id)
        )
    ).scalar()

    assert 150_000 < distance_m < 190_000, f"Москва → Тверь ≈ 170 км, получили {distance_m:.0f} м"


async def test_active_new_request_is_found_near_route(db_session, individual_client, carrier_executor):
    """Репозиторий отдаёт только новые неудалённые заявки, лежащие рядом с маршрутом."""
    route = await _add_route(
        db_session,
        carrier_executor.id,
        path=WKTElement(
            f"LINESTRING({MOSCOW_LNG} {MOSCOW_LAT}, {TVER_LNG} {TVER_LAT})", srid=4326
        ),
    )
    near = await _add_request(db_session, individual_client.id)
    await _add_request(
        db_session,
        individual_client.id,
        origin_address="Санкт-Петербург",
        origin_location=_point(30.3141, 59.9386),
        destination_address="Колпино",
        destination_location=_point(30.6, 59.75),
    )
    await _add_request(db_session, individual_client.id, status=CargoRequestStatus.CANCELLED)
    await _add_request(db_session, individual_client.id, is_deleted=True)

    found = await find_requests_near_route(db_session, route.id, radius_meters=50_000)

    assert [request.id for request in found] == [near.id]


async def test_coordinates_are_required(db_session, individual_client):
    """Без координат точку загрузки сохранить нельзя — колонка NOT NULL."""
    with pytest.raises(IntegrityError):
        await _add_request(db_session, individual_client.id, origin_location=None)

    await db_session.rollback()


async def test_wrong_srid_is_rejected(db_session, individual_client):
    """PostGIS не даст записать точку с SRID, отличным от SRID колонки (4326)."""
    with pytest.raises(DBAPIError):
        await _add_request(
            db_session, individual_client.id, destination_location=_point(0, 0, srid=3857)
        )

    await db_session.rollback()
