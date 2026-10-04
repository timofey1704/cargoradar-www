"""Проверяем сервис общей ленты: маппинг в read-схемы, пагинацию и кеш."""

from datetime import date, datetime, timezone

import pytest

from core.config import settings
from client.models.enums.request_statuses import CargoRequestStatus
from client.models.request import CargoRequest
from core.models.enums.post_creator_type import PostCreatorType
from core.models.post import Post
from core.redis.cache import cache_key
from core.repositories.search.feed import FeedItem, FeedMapPoint
from core.services.search.feed import FeedService
from executor.models.route import Route

# сервис кеширует ответы — все тесты модуля идут с подменённым (in-memory) Redis
pytestmark = pytest.mark.usefixtures("cache_client")

CREATED_AT = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)


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
        creator_type=PostCreatorType.CLIENT,
        client_id=3,
        title="Нужен рефрижератор",
        request_text="Минск → Гомель, 10 тонн",
        created_at=CREATED_AT,
    )


def _request(request_id: int) -> CargoRequest:
    return CargoRequest(
        id=request_id,
        client_id=8,
        status=CargoRequestStatus.NEW,
        origin_address="Минск",
        origin_location=None,
        destination_address="Брест",
        destination_location=None,
        cargo_type="Стройматериалы",
        weight_kg=1200.0,
        loading_date=date(2026, 10, 10),
        created_at=CREATED_AT,
    )


def _feed_items() -> list[FeedItem]:
    """Лента из двух элементов: маршрут водителя и пост клиента (свежие сверху)."""
    return [
        FeedItem(kind="route", id=1, created_at=CREATED_AT, object=_route(1)),
        FeedItem(kind="post", id=2, created_at=CREATED_AT, object=_post(2)),
    ]


def _posts_feed(count: int) -> list[FeedItem]:
    return [
        FeedItem(kind="post", id=post_id, created_at=CREATED_AT, object=_post(post_id))
        for post_id in range(1, count + 1)
    ]


class FakeFeedRepository:
    """Заглушка репозитория ленты: отдаёт заданные элементы и считает обращения."""

    def __init__(self, items: list[FeedItem]) -> None:
        self.items = items
        self.feed_calls = 0
        self.count_calls = 0

    async def get_feed(self, *, skip: int = 0, limit: int = 20) -> list[FeedItem]:
        self.feed_calls += 1
        return self.items[skip : skip + limit]

    async def count_feed(self) -> int:
        self.count_calls += 1
        return len(self.items)


def _service(items: list[FeedItem]) -> tuple[FeedService, FakeFeedRepository]:
    service = FeedService(db=None)  # type: ignore[arg-type]
    repository = FakeFeedRepository(items)
    service.repository = repository  # type: ignore[assignment]
    return service, repository


async def test_feed_maps_route_and_post_to_read_schemas():
    service, _ = _service(_feed_items())

    page = await service.get_feed()

    assert [item.kind for item in page.items] == ["route", "post"]
    assert [item.id for item in page.items] == [1, 2]
    assert all(item.created_at == CREATED_AT for item in page.items)

    route_item, post_item = page.items
    # в элементе-маршруте заполнены только route-поля
    assert route_item.route is not None
    assert route_item.route.point_a == "Минск"
    assert route_item.route.point_b == "Брест"
    assert route_item.route.distance_km == 350.5
    assert route_item.route.price == 500.0
    assert route_item.post is None

    # в элементе-посте заполнены только post-поля
    assert post_item.post is not None
    assert post_item.post.title == "Нужен рефрижератор"
    assert post_item.post.creator_type == PostCreatorType.CLIENT
    assert post_item.post.client_id == 3
    assert post_item.route is None


async def test_feed_maps_cargo_request_to_read_schema():
    request = _request(3)
    item = FeedItem(
        kind="request",
        id=3,
        created_at=CREATED_AT,
        object=request,
        map_points=[FeedMapPoint("Минск", 53.9, 27.56)],
    )
    service, _ = _service([item])

    page = await service.get_feed()

    assert len(page.items) == 1
    feed_item = page.items[0]
    assert feed_item.kind == "request"
    assert feed_item.request is not None
    assert feed_item.request.origin_address == "Минск"
    assert feed_item.request.destination_address == "Брест"
    assert feed_item.request.cargo_type == "Стройматериалы"
    assert feed_item.route is None
    assert feed_item.post is None
    assert feed_item.map_points[0].label == "Минск"
    assert feed_item.map_points[0].latitude == 53.9
    assert feed_item.map_points[0].longitude == 27.56


async def test_feed_pagination_sets_total_and_has_more():
    service, repository = _service(_posts_feed(3))

    first_page = await service.get_feed(skip=0, limit=2)

    assert len(first_page.items) == 2
    assert first_page.total == 3
    assert (first_page.skip, first_page.limit) == (0, 2)
    assert first_page.has_more is True

    last_page = await service.get_feed(skip=2, limit=2)

    assert len(last_page.items) == 1
    assert last_page.has_more is False
    assert last_page.total == 3
    assert repository.feed_calls == 2
    assert repository.count_calls == 2


async def test_empty_feed_has_no_more_pages():
    service, _ = _service([])

    page = await service.get_feed()

    assert page.items == []
    assert page.total == 0
    assert page.has_more is False


async def test_feed_is_cached_with_ttl(cache_client, fake_redis):
    service, repository = _service(_feed_items())

    first = await service.get_feed(skip=0, limit=20)
    second = await service.get_feed(skip=0, limit=20)

    assert repository.feed_calls == 1, "в БД ходим только на промахе кеша"
    assert repository.count_calls == 1
    assert first == second
    assert await fake_redis.exists(cache_key("search:feed:v2:limit=20:skip=0")) == 1
    assert (
        fake_redis.ttl_of(cache_key("search:feed:v2:limit=20:skip=0"))
        == settings.cache_ttl_search
    )


async def test_each_feed_page_has_its_own_cache_key(cache_client, fake_redis):
    service, repository = _service(_posts_feed(3))

    await service.get_feed(skip=0, limit=2)
    await service.get_feed(skip=2, limit=2)
    await service.get_feed(skip=0, limit=2)  # снова первая страница — уже из кеша

    assert repository.feed_calls == 2, "у каждой страницы свой ключ кеша"
    assert fake_redis.contains(
        cache_key("search:feed:v2:limit=2:skip=0"),
        cache_key("search:feed:v2:limit=2:skip=2"),
    )


async def test_feed_is_reloaded_after_invalidation(cache_client):
    service, repository = _service(_feed_items())
    await service.get_feed()

    await cache_client.delete_cached_keys(cache_key("search:feed:v2:limit=20:skip=0"))
    await service.get_feed()

    assert repository.feed_calls == 2
