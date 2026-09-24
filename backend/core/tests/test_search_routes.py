"""Проверяем роуты поиска: регистрацию, фильтры в OpenAPI и передачу параметров в сервисы."""

import pytest

from client.models.enums.request_statuses import CargoRequestStatus
from core.models.enums.post_creator_type import PostCreatorType
from core.routes.search.feed import get_feed
from core.routes.search.post import get_posts
from core.routes.search.request import get_requests_feed
from core.routes.search.route import get_routes
from core.schemas.search.feed import FeedPageRead
from core.schemas.search.post import PostPageRead
from core.schemas.search.request import CargoRequestPageRead
from core.schemas.search.route import RoutePageRead
from core.services.search.feed import FeedService
from core.services.search.post import PostService
from core.services.search.request import CargoRequestService
from core.services.search.route import RouteService
from main import app

SEARCH_PATHS = (
    "/api/search/feed",
    "/api/search/requests",
    "/api/search/posts",
    "/api/search/routes",
)


def test_search_routes_are_registered():
    """Все четыре поисковых роута есть в схеме (заодно проверяем, что схема вообще собирается)."""
    paths = app.openapi()["paths"]

    for path in SEARCH_PATHS:
        assert path in paths, f"роут {path} не зарегистрирован"
        assert "get" in paths[path], f"у {path} нет GET"


def test_search_requests_route_declares_all_filters():
    """Фильтры ленты заявок видны в OpenAPI — значит, клиент может их передавать."""
    parameters = app.openapi()["paths"]["/api/search/requests"]["get"]["parameters"]
    names = {parameter["name"] for parameter in parameters}

    assert names == {
        "status",
        "cargo_type",
        "vehicle_type",
        "loading_date_from",
        "loading_date_to",
        "origin_lat",
        "origin_lon",
        "radius_km",
        "skip",
        "limit",
    }


async def test_feed_route_forwards_pagination_to_service(monkeypatch):
    expected = FeedPageRead(items=[], total=0, skip=5, limit=10, has_more=False)
    captured: dict[str, object] = {}

    async def fake_get_feed(self, *, skip: int = 0, limit: int = 20) -> FeedPageRead:
        captured.update({"skip": skip, "limit": limit})
        return expected

    monkeypatch.setattr(FeedService, "get_feed", fake_get_feed)

    result = await get_feed(db=None, skip=5, limit=10)  # type: ignore[arg-type]

    assert result is expected
    assert captured == {"skip": 5, "limit": 10}


async def test_requests_route_forwards_filters_to_service(monkeypatch):
    expected = CargoRequestPageRead(items=[], skip=0, limit=20, has_more=False)
    captured: dict[str, object] = {}

    async def fake_get_feed(self, **kwargs: object) -> CargoRequestPageRead:
        captured.update(kwargs)
        return expected

    monkeypatch.setattr(CargoRequestService, "get_feed", fake_get_feed)

    result = await get_requests_feed(
        db=None,  # type: ignore[arg-type]
        cargo_type="Тент",
        radius_km=50.0,
        origin_lat=53.9,
        origin_lon=27.56,
    )

    assert result is expected
    assert captured == {
        "status": CargoRequestStatus.NEW,
        "cargo_type": "Тент",
        "vehicle_type": None,
        "loading_date_from": None,
        "loading_date_to": None,
        "origin_lat": 53.9,
        "origin_lon": 27.56,
        "radius_km": 50.0,
        "skip": 0,
        "limit": 20,
    }


async def test_posts_route_requires_creator_type(monkeypatch):
    expected = PostPageRead(items=[], skip=0, limit=20, has_more=False)
    captured: dict[str, object] = {}

    async def fake_get_by_creator_type(
        self,
        creator_type: PostCreatorType,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> PostPageRead:
        captured.update(
            {"creator_type": creator_type, "skip": skip, "limit": limit}
        )
        return expected

    monkeypatch.setattr(PostService, "get_by_creator_type", fake_get_by_creator_type)

    result = await get_posts(
        db=None,  # type: ignore[arg-type]
        creator_type=PostCreatorType.EXECUTOR,
    )

    assert result is expected
    assert captured == {
        "creator_type": PostCreatorType.EXECUTOR,
        "skip": 0,
        "limit": 20,
    }


async def test_routes_route_forwards_executor_id(monkeypatch):
    expected = RoutePageRead(items=[], skip=0, limit=20, has_more=False)
    captured: dict[str, object] = {}

    async def fake_get_by_executor(
        self, executor_id: int, *, skip: int = 0, limit: int = 20
    ) -> RoutePageRead:
        captured.update(
            {"executor_id": executor_id, "skip": skip, "limit": limit}
        )
        return expected

    monkeypatch.setattr(RouteService, "get_by_executor", fake_get_by_executor)

    result = await get_routes(db=None, executor_id=7)  # type: ignore[arg-type]

    assert result is expected
    assert captured == {"executor_id": 7, "skip": 0, "limit": 20}

