"""Интеграционные тесты OSRM (роутинг по дорогам, профиль truck-soft).

Требуют запущенный OSRM с подготовленными данными (см. README, шаг 5).
Если OSRM недоступен — тесты пропускаются.

    docker compose up -d osrm
    docker compose exec backend uv run pytest core/tests/test_osrm_integration.py -q

При запуске с хоста (не из контейнера) нужен адрес проброшенного порта:

    OSRM_URL=http://localhost:5001 uv run pytest core/tests/test_osrm_integration.py -q
"""

import json
import urllib.error
import urllib.request

import pytest

from core.config import settings

pytestmark = pytest.mark.integration

# Минск и Борисов — заведомо разные точки примерно в 70 км друг от друга
MINSK_LNG, MINSK_LAT = 27.5615, 53.9006
BORISOV_LNG, BORISOV_LAT = 28.5, 54.2279

COORDS = f"{MINSK_LNG},{MINSK_LAT};{BORISOV_LNG},{BORISOV_LAT}"


def _osrm(path: str, timeout: float = 15.0) -> dict:
    """GET к OSRM по адресу из настроек (stdlib, чтобы не тянуть http-клиент в тесты)."""
    url = f"{settings.osrm_url.rstrip('/')}{path}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode())
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        pytest.skip(f"OSRM недоступен по {settings.osrm_url} ({exc}) — тесты пропущены")


def test_route_service_returns_distance_and_duration():
    """OSRM отдаёт маршрут с километражем и временем в пути — база для расчёта ставки."""
    data = _osrm(f"/route/v1/driving/{COORDS}?overview=false")

    assert data["code"] == "Ok"
    route = data["routes"][0]
    assert 60_000 < route["distance"] < 100_000, (
        f"Минск → Борисов ≈ 70 км, получили {route['distance']:.0f} м"
    )
    assert route["duration"] > 0


def test_route_goes_by_roads_not_straight_line():
    """Профиль ведёт по дорогам: путь длиннее прямой линии между точками."""
    data = _osrm(f"/route/v1/driving/{COORDS}?overview=false")
    distance_km = data["routes"][0]["distance"] / 1000

    straight_line_km = 70.0
    assert distance_km > straight_line_km, "маршрут не может быть короче прямой между точками"
    assert distance_km < straight_line_km * 2, "слишком большой крюк — похоже на ошибку данных"


def test_nearest_service_snaps_point_to_road():
    """`/nearest` привязывает координату к дороге — нужно для поиска заявок рядом с маршрутом."""
    data = _osrm(f"/nearest/v1/driving/{MINSK_LNG},{MINSK_LAT}")

    assert data["code"] == "Ok"
    waypoint = data["waypoints"][0]
    assert len(waypoint["location"]) == 2
    assert waypoint["distance"] < 1_000, "точка в центре Минска должна быть рядом с дорогой"


def test_table_service_returns_distance_matrix():
    """`/table` считает матрицу расстояний — нужно для подбора машин под заявки."""
    data = _osrm(f"/table/v1/driving/{COORDS}?annotations=distance")

    assert data["code"] == "Ok"
    distances = data["distances"]
    assert distances[0][1] == distances[1][0] > 0
    assert distances[0][0] == 0
