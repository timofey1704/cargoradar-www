"""Проверяем, что реальные сервисы кешируются: ключи, TTL и отсутствие лишних запросов."""

from decimal import Decimal

from core.config import settings
from core.models.faq import FAQ
from core.models.membership import Feature, Membership
from core.redis.cache import cache_key
from core.repositories.membership_repository import MembershipRepository
from core.services.main_page_service import MainPageService
from core.services.membership_service import MembershipService


class FakeFaqRepository:
    """Заглушка репозитория: считает обращения в «БД»."""

    def __init__(self) -> None:
        self.calls = 0

    async def get_faqs(self) -> list[FAQ]:
        self.calls += 1
        return [
            FAQ(id=1, title="Как оформить заказ?", content="Через личный кабинет"),
            FAQ(id=2, title="Как оплатить?", content="Картой онлайн"),
        ]


async def test_main_page_faqs_are_cached(cache_client, fake_redis):
    service = MainPageService(db=None)  # type: ignore[arg-type]
    repository = FakeFaqRepository()
    service.repository = repository  # type: ignore[assignment]

    first = await service.get_faqs()
    second = await service.get_faqs()

    assert repository.calls == 1, "в БД ходим только на промахе кеша"
    assert first == second
    assert [faq.title for faq in first] == ["Как оформить заказ?", "Как оплатить?"]
    assert await fake_redis.exists(cache_key("main:faq")) == 1
    assert fake_redis.ttl_of(cache_key("main:faq")) == settings.cache_ttl_faq


async def test_main_page_faqs_are_reloaded_after_invalidation(cache_client):
    service = MainPageService(db=None)  # type: ignore[arg-type]
    repository = FakeFaqRepository()
    service.repository = repository  # type: ignore[assignment]
    await service.get_faqs()

    await cache_client.delete_cached_keys(cache_key("main:faq"))
    await service.get_faqs()

    assert repository.calls == 2


async def test_membership_plans_are_cached(cache_client, fake_redis, monkeypatch):
    calls: list[int] = []

    async def fake_get_available_with_features(self) -> list[Membership]:
        calls.append(1)
        return [
            Membership(
                id=1,
                name="Старт",
                description="Базовый тариф",
                price=Decimal("10.00"),
                is_popular=False,
                is_available=True,
                is_trial=False,
                features=[Feature(id=1, membership_id=1, name="Геолокация")],
            )
        ]

    monkeypatch.setattr(
        MembershipRepository,
        "get_available_with_features",
        fake_get_available_with_features,
    )

    service = MembershipService(db=None)  # type: ignore[arg-type]

    first = await service.get_plans()
    second = await service.get_plans()

    assert len(calls) == 1, "каталог тарифов читаем из кеша"
    assert first == second
    assert first[0].name == "Старт"
    assert first[0].features[0].name == "Геолокация"
    assert await fake_redis.exists(cache_key("membership:plans")) == 1
    assert fake_redis.ttl_of(cache_key("membership:plans")) == settings.cache_ttl_membership_plans
