"""Проверяем сервисы поиска (маршруты, посты, заявки): маппинг, пагинацию и кеш."""

from datetime import date, datetime, timezone

import pytest
from fastapi import HTTPException

from client.models.enums.request_statuses import CargoRequestStatus
from client.models.request import CargoRequest
from core.models.enums.post_creator_type import PostCreatorType
from core.models.post import Post
from core.redis.cache import cache_key
from core.services.search.post import PostService
from core.services.search.request import CargoRequestService
from core.services.search.route import RouteService
from executor.models.route import Route

# сервисы кешируют ответы — все тесты модуля идут с подменённым (in-memory) Redis
pytestmark = pytest.mark.usefixtures("cache_client")

CREATED_AT = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)
LOADING_DATE = date(2026, 9, 5)


def _route(route_id: int) -> Route:
    return Route(
        id=route_id,
        executor_id=7,
        point_a="Минск",
        point_b="Брест",
        distance_km=350.5,
        duration_min=270,
        comment="Тент 20 тонн",
        price=500.0,
        created_at=CREATED_AT,
    )


def _post(post_id: int) -> Post:
    return Post(
        id=post_id,
        creator_type=PostCreatorType.EXECUTOR,
        executor_id=7,
        title="Свободная фура Минск—Брест",
        request_text="Возьму попутный груз до 20 тонн",
        created_at=CREATED_AT,
    )


def _request(request_id: int) -> CargoRequest:
    return CargoRequest(
        id=request_id,
        client_id=3,
        status=CargoRequestStatus.NEW,
        origin_address="Минск, ул. Складская 1",
        destination_address="Гомель, ул. Заводская 5",
        cargo_type="Тент",
        weight_kg=10000.0,
        volume_m3=40.0,
        vehicle_type="Фура",
        loading_date=LOADING_DATE,
        budget=1500.0,
        comment="Срочная погрузка",
        created_at=CREATED_AT,
    )



class FakeRouteRepository:
    """Заглушка репозитория маршрутов: считает обращения и запоминает аргументы."""

    def __init__(self, routes: list[Route]) -> None:
        self.routes = routes
        self.calls = 0
        self.last_args: dict[str, object] = {}

    async def get_by_executor(
        self, executor_id: int, *, skip: int = 0, limit: int = 20
    ) -> list[Route]:
        self.calls += 1
        self.last_args = {"executor_id": executor_id, "skip": skip, "limit": limit}
        return self.routes[skip : skip + limit]


class FakePostRepository:
    """Заглушка репозитория постов."""

    def __init__(self, posts: list[Post]) -> None:
        self.posts = posts
        self.calls = 0
        self.last_args: dict[str, object] = {}

    def _page(self, key: str, value: object, *, skip: int, limit: int) -> list[Post]:
        self.calls += 1
        self.last_args = {key: value, "skip": skip, "limit": limit}
        return self.posts[skip : skip + limit]

    async def get_by_client(
        self, client_id: int, *, skip: int = 0, limit: int = 20
    ) -> list[Post]:
        return self._page("client_id", client_id, skip=skip, limit=limit)

    async def get_by_executor(
        self, executor_id: int, *, skip: int = 0, limit: int = 20
    ) -> list[Post]:
        return self._page("executor_id", executor_id, skip=skip, limit=limit)

    async def get_by_creator_type(
        self, creator_type: PostCreatorType, *, skip: int = 0, limit: int = 20
    ) -> list[Post]:
        return self._page("creator_type", creator_type, skip=skip, limit=limit)


class FakeCargoRequestRepository:
    """Заглушка репозитория заявок: повторяет сигнатуру get_feed и считает обращения."""

    def __init__(self, requests: list[CargoRequest]) -> None:
        self.requests = requests
        self.feed_calls = 0
        self.client_calls = 0
        self.feed_filters: dict[str, object] = {}

    async def get_feed(
        self,
        *,
        status: CargoRequestStatus | None = CargoRequestStatus.NEW,
        cargo_type: str | None = None,
        vehicle_type: str | None = None,
        loading_date_from: date | None = None,
        loading_date_to: date | None = None,
        origin_lat: float | None = None,
        origin_lon: float | None = None,
        radius_km: float | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[CargoRequest]:
        self.feed_calls += 1
        self.feed_filters = {
            "status": status,
            "cargo_type": cargo_type,
            "vehicle_type": vehicle_type,
            "loading_date_from": loading_date_from,
            "loading_date_to": loading_date_to,
            "origin_lat": origin_lat,
            "origin_lon": origin_lon,
            "radius_km": radius_km,
            "skip": skip,
            "limit": limit,
        }
        return self.requests[skip : skip + limit]

    async def get_by_client(
        self, client_id: int, *, skip: int = 0, limit: int = 20
    ) -> list[CargoRequest]:
        self.client_calls += 1
        return self.requests[skip : skip + limit]


def _route_service(routes: list[Route]) -> tuple[RouteService, FakeRouteRepository]:
    service = RouteService(db=None)  # type: ignore[arg-type]
    repository = FakeRouteRepository(routes)
    service.repository = repository  # type: ignore[assignment]
    return service, repository


def _post_service(posts: list[Post]) -> tuple[PostService, FakePostRepository]:
    service = PostService(db=None)  # type: ignore[arg-type]
    repository = FakePostRepository(posts)
    service.repository = repository  # type: ignore[assignment]
    return service, repository


def _request_service(
    requests: list[CargoRequest],
) -> tuple[CargoRequestService, FakeCargoRequestRepository]:
    service = CargoRequestService(db=None)  # type: ignore[arg-type]
    repository = FakeCargoRequestRepository(requests)
    service.repository = repository  # type: ignore[assignment]
    return service, repository


async def test_route_service_maps_routes_of_executor():
    service, repository = _route_service([_route(1), _route(2)])

    page = await service.get_by_executor(7, skip=0, limit=20)

    assert repository.last_args == {"executor_id": 7, "skip": 0, "limit": 20}
    assert [route.id for route in page.items] == [1, 2]
    assert page.items[0].point_a == "Минск"
    assert page.items[0].distance_km == 350.5
    assert page.items[0].price == 500.0
    assert page.items[0].created_at == CREATED_AT
    # total не считаем: про следующую страницу говорит has_more
    assert page.total is None
    assert page.has_more is False


async def test_post_service_maps_posts_and_forwards_author():
    service, repository = _post_service([_post(1)])

    by_client = await service.get_by_client(3, skip=0, limit=20)

    assert repository.last_args == {"client_id": 3, "skip": 0, "limit": 20}

    by_creator = await service.get_by_creator_type(PostCreatorType.EXECUTOR)

    assert repository.last_args == {
        "creator_type": PostCreatorType.EXECUTOR,
        "skip": 0,
        "limit": 20,
    }

    post = by_client.items[0]
    assert post.title == "Свободная фура Минск—Брест"
    assert post.creator_type == PostCreatorType.EXECUTOR
    assert post.executor_id == 7
    assert post.client_id is None
    assert post.created_at == CREATED_AT




async def test_request_service_maps_feed_and_forwards_filters():
    service, repository = _request_service([_request(1)])

    page = await service.get_feed(
        cargo_type="Тент",
        loading_date_from=LOADING_DATE,
        origin_lat=53.9,
        origin_lon=27.56,
        radius_km=50.0,
        limit=10,
    )

    assert repository.feed_filters == {
        "status": CargoRequestStatus.NEW,
        "cargo_type": "Тент",
        "vehicle_type": None,
        "loading_date_from": LOADING_DATE,
        "loading_date_to": None,
        "origin_lat": 53.9,
        "origin_lon": 27.56,
        "radius_km": 50.0,
        "skip": 0,
        "limit": 10,
    }

    request = page.items[0]
    assert request.status == CargoRequestStatus.NEW
    assert request.origin_address == "Минск, ул. Складская 1"
    assert request.destination_address == "Гомель, ул. Заводская 5"
    assert request.loading_date == LOADING_DATE
    assert request.budget == 1500.0
    assert page.total is None
    assert page.has_more is False


async def test_request_service_maps_requests_by_client():
    service, repository = _request_service([_request(1)])

    page = await service.get_by_client(3)

    assert repository.client_calls == 1
    assert page.items[0].client_id == 3


async def test_route_service_caches_pages_separately(fake_redis):
    service, repository = _route_service([_route(1), _route(2), _route(3)])

    first = await service.get_by_executor(7, skip=0, limit=2)
    second = await service.get_by_executor(7, skip=0, limit=2)
    other_page = await service.get_by_executor(7, skip=2, limit=2)
    other_executor = await service.get_by_executor(8, skip=0, limit=2)

    assert repository.calls == 3, "повторный запрос той же страницы берём из кеша"
    assert first == second
    assert first.has_more is True
    assert len(other_page.items) == 1
    assert other_page.has_more is False
    assert other_executor.items  # у другого исполнителя свой ключ кеша
    assert fake_redis.contains(
        cache_key("search:route:executor_id=7:limit=2:skip=0"),
        cache_key("search:route:executor_id=7:limit=2:skip=2"),
        cache_key("search:route:executor_id=8:limit=2:skip=0"),
    )


async def test_post_service_caches_by_author_and_creator_type(fake_redis):
    service, repository = _post_service([_post(1)])

    await service.get_by_client(3)
    await service.get_by_client(3)
    await service.get_by_executor(7)
    await service.get_by_creator_type(PostCreatorType.CLIENT)

    assert repository.calls == 3, "кеш по автору и по типу автора не пересекаются"
    assert fake_redis.contains(
        cache_key("search:post:client_id=3:limit=20:skip=0"),
        cache_key("search:post:executor_id=7:limit=20:skip=0"),
        cache_key("search:post:creator_type=client:limit=20:skip=0"),
    )


async def test_request_service_caches_by_filters(fake_redis):
    service, repository = _request_service([_request(1)])

    await service.get_feed()
    await service.get_feed()
    await service.get_feed(cargo_type="Тент")

    assert repository.feed_calls == 2, "разные фильтры — разные страницы кеша"
    assert fake_redis.contains(
        cache_key("search:request:feed:limit=20:skip=0:status=new"),
        cache_key("search:request:feed:cargo_type=Тент:limit=20:skip=0:status=new"),
    )



async def test_request_service_rejects_incomplete_geo_filter():
    """Часть гео-параметров без остальных — 400, и до репозитория дело не доходит."""
    service, repository = _request_service([_request(1)])

    with pytest.raises(HTTPException) as exc_info:
        await service.get_feed(origin_lat=53.9, radius_km=50.0)

    assert exc_info.value.status_code == 400
    assert repository.feed_calls == 0


async def test_request_service_accepts_full_geo_filter():
    service, repository = _request_service([_request(1)])

    page = await service.get_feed(origin_lat=53.9, origin_lon=27.56, radius_km=50.0)

    assert repository.feed_calls == 1
    assert page.has_more is False

