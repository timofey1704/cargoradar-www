"""Интеграционные тесты PostGIS-координат маршрута (executor.models.route.Route).

Нужны живой PostgreSQL с расширением PostGIS (образ postgis/postgis) и
применённая миграция routes. Если БД недоступна — тесты пропускаются.

    docker compose exec backend uv run pytest executor/tests -q
"""

from typing import Any

import pytest
from geoalchemy2 import Geography
from geoalchemy2.elements import WKTElement
from sqlalchemy import cast, func, select, text
from sqlalchemy.exc import DBAPIError, IntegrityError

from executor.models.route import Route

pytestmark = pytest.mark.integration

# Минск и Борисов — заведомо разные точки примерно в 70 км друг от друга
MINSK_LNG, MINSK_LAT = 27.5615, 53.9006
BORISOV_LNG, BORISOV_LAT = 28.5, 54.2279

TABLE = "routes"


def _point(lng: float, lat: float, srid: int = 4326) -> WKTElement:
    """WKT-точка в порядке (lng lat) — так PostGIS хранит WGS84-геометрию."""
    return WKTElement(f"POINT({lng} {lat})", srid=srid)


async def _add_route(session, executor_id: int, **overrides) -> Route:
    params: dict[str, Any] = {
        "executor_id": executor_id,
        "point_a": "Минск",
        "point_b": "Борисов",
        "point_a_location": _point(MINSK_LNG, MINSK_LAT),
        "point_b_location": _point(BORISOV_LNG, BORISOV_LAT),
    }
    params.update(overrides)
    route = Route(**params)
    session.add(route)
    await session.flush()
    await session.refresh(route)
    return route


async def test_geometry_columns_are_registered_in_postgis(db_session):
    """Колонки координат зарегистрированы в PostGIS как POINT с SRID 4326."""
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
        ("point_a_location", 2, 4326, "POINT"),
        ("point_b_location", 2, 4326, "POINT"),
    ]


async def test_coordinate_columns_have_gist_indexes(db_session):
    """Под пространственные фильтры есть GiST-индексы (ST_DWithin / ST_Distance)."""
    rows = (
        await db_session.execute(
            text(
                "SELECT indexname, indexdef FROM pg_indexes "
                "WHERE tablename = :table AND indexdef ILIKE '%USING gist%'"
            ),
            {"table": TABLE},
        )
    ).all()
    gist_indexes = {row.indexname: row.indexdef for row in rows}

    assert set(gist_indexes) == {
        "idx_routes_point_a_location",
        "idx_routes_point_b_location",
    }


async def test_coordinates_roundtrip_through_orm(db_session, carrier_executor):
    """Координаты сохраняются и читаются обратно как корректные WGS84-точки."""
    route = await _add_route(db_session, carrier_executor.id)
    assert route.id is not None
    assert route.is_deleted is False, "значение по умолчанию из модели"

    stored = (
        await db_session.execute(
            select(
                func.ST_AsText(Route.point_a_location),
                func.ST_AsText(Route.point_b_location),
                func.ST_SRID(Route.point_a_location),
                func.GeometryType(Route.point_b_location),
            ).where(Route.id == route.id)
        )
    ).one()

    assert stored[0] == f"POINT({MINSK_LNG} {MINSK_LAT})"
    assert stored[1] == f"POINT({BORISOV_LNG} {BORISOV_LAT})"
    assert stored[2] == 4326
    assert stored[3] == "POINT"


async def test_distance_and_dwithin_between_points(db_session, carrier_executor):
    """PostGIS считает расстояние между точками маршрута и фильтрует по нему."""
    route = await _add_route(db_session, carrier_executor.id)

    distance_m = (
        await db_session.execute(
            select(
                func.ST_Distance(
                    cast(Route.point_a_location, Geography),
                    cast(Route.point_b_location, Geography),
                )
            ).where(Route.id == route.id)
        )
    ).scalar()
    assert 50_000 < distance_m < 90_000, f"Минск → Борисов ≈ 70 км, получили {distance_m:.0f} м"

    near = (
        await db_session.execute(
            select(Route.id).where(
                func.ST_DWithin(
                    cast(Route.point_a_location, Geography),
                    cast(Route.point_b_location, Geography),
                    100_000,
                )
            )
        )
    ).scalars().all()
    assert route.id in near

    far = (
        await db_session.execute(
            select(Route.id).where(
                func.ST_DWithin(
                    cast(Route.point_a_location, Geography),
                    cast(Route.point_b_location, Geography),
                    10_000,
                )
            )
        )
    ).scalars().all()
    assert route.id not in far


async def test_route_is_found_by_point_nearby(db_session, carrier_executor):
    """Поиск маршрутов рядом с точкой (ST_DWithin по A) — типовой сценарий карты."""
    route = await _add_route(db_session, carrier_executor.id)
    near_minsk = func.ST_GeomFromText(f"POINT({MINSK_LNG + 0.01} {MINSK_LAT})", 4326)

    found = (
        await db_session.execute(
            select(Route.id).where(func.ST_DWithin(Route.point_a_location, near_minsk, 0.05))
        )
    ).scalars().all()
    assert found == [route.id]

    far_point = func.ST_GeomFromText("POINT(0 0)", 4326)
    not_found = (
        await db_session.execute(
            select(Route.id).where(func.ST_DWithin(Route.point_a_location, far_point, 0.05))
        )
    ).scalars().all()
    assert not_found == []


async def test_coordinates_are_required(db_session, carrier_executor):
    """Без координат маршрут сохранить нельзя — колонки NOT NULL."""
    with pytest.raises(IntegrityError):
        await _add_route(db_session, carrier_executor.id, point_a_location=None)

    await db_session.rollback()


async def test_wrong_srid_is_rejected(db_session, carrier_executor):
    """PostGIS не даст записать точку с SRID, отличным от SRID колонки (4326)."""
    with pytest.raises(DBAPIError):
        await _add_route(db_session, carrier_executor.id, point_a_location=_point(0, 0, srid=3857))

    await db_session.rollback()
