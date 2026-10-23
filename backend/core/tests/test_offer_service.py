from datetime import datetime, timezone
from decimal import Decimal
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from client.models.enums.request_statuses import CargoRequestStatus
from core.dependencies import ChatActor
from core.models.enums.actor_types import ActorType
from core.models.enums.message_types import MessageType
from core.models.enums.offer_statuses import OfferStatus
from core.repositories.chat import ChatRepository
from core.redis.chat import EVENT_MESSAGE_CREATED
from core.schemas.offer import OfferCreate
from core.services import offer_service as offer_service_module
from core.services.offer_service import OfferRequestUnavailableError, OfferService


@dataclass
class FakeConversation:
    id: int = 19
    order_id: int = 7
    client_id: int = 11
    executor_id: int = 23


class FakeRepository:
    def __init__(self, *, order_status=CargoRequestStatus.NEW):
        self.order = SimpleNamespace(id=7, client_id=11, status=order_status)
        self.conversation = FakeConversation()
        self.offer: Any = None
        self.message: Any = None
        self.parent_offer = SimpleNamespace(
            id=30,
            conversation_id=self.conversation.id,
            author_type=ActorType.executor,
            status=OfferStatus.pending,
            currency="BYN",
            price=Decimal("125.50"),
            terms=None,
            expires_at=None,
            created_at=datetime.now(timezone.utc),
        )
        self.other_pending_offer = SimpleNamespace(
            id=55,
            status=OfferStatus.pending,
        )
        self.other_conversation = FakeConversation(id=29, executor_id=24)

    async def get_participant_conversation(self, role, user_id, conversation_id):
        return self.conversation if conversation_id == self.conversation.id else None

    async def get_offer_for_update(self, conversation_id, offer_id):
        if conversation_id == self.conversation.id and offer_id == self.parent_offer.id:
            return self.parent_offer
        return None

    async def create_counter_offer_message(
        self, *, conversation, actor_type, actor_id, parent_offer, data
    ):
        self.offer = SimpleNamespace(
            id=32,
            conversation_id=conversation.id,
            author_type=actor_type,
            author_client_id=actor_id if actor_type is ActorType.client else None,
            author_executor_id=actor_id if actor_type is ActorType.executor else None,
            parent_offer_id=parent_offer.id,
            price=data.price,
            currency=parent_offer.currency,
            terms=data.terms,
            status=OfferStatus.pending,
            created_at=datetime.now(timezone.utc),
        )
        parent_offer.status = OfferStatus.countered
        self.message = SimpleNamespace(id=42)
        return self.offer, self.message

    async def accept_offer_for_order(self, *, conversation, order, offer, body):
        offer.status = OfferStatus.accepted
        order.status = CargoRequestStatus.IN_PROGRESS
        self.other_pending_offer.status = OfferStatus.declined
        self.message = SimpleNamespace(id=51, is_system=True, body=body)
        return self.message, [(self.other_pending_offer, self.other_conversation)]

    async def get_order_for_offer(self, order_id):
        return self.order if order_id == self.order.id else None

    async def get_or_create_offer_conversation(self, **kwargs):
        assert kwargs == {"order_id": 7, "client_id": 11, "executor_id": 23}
        return self.conversation

    async def get_pending_offer(self, conversation_id):
        assert conversation_id == self.conversation.id
        return None

    async def create_offer_message(self, *, conversation, executor_id, data):
        assert executor_id == self.conversation.executor_id
        self.offer = SimpleNamespace(
            id=31,
            conversation_id=conversation.id,
            author_type=ActorType.executor,
            author_client_id=None,
            author_executor_id=executor_id,
            parent_offer_id=None,
            price=data.price,
            currency="BYN",
            terms=data.terms,
            status="pending",
            created_at=datetime.now(timezone.utc),
        )
        self.message = SimpleNamespace(id=41)
        return self.offer, self.message

    async def get_message(self, message_id):
        assert message_id == self.message.id
        if getattr(self.message, "is_system", False):
            return SimpleNamespace(
                id=self.message.id,
                conversation_id=19,
                sender_type=ActorType.system,
                sender_client_id=None,
                sender_executor_id=None,
                type=MessageType.system,
                body=self.message.body,
                offer_id=None,
                offer=None,
                attachments=[],
                created_at=datetime.now(timezone.utc),
            )
        return SimpleNamespace(
            id=self.message.id,
            conversation_id=19,
            sender_type=self.offer.author_type,
            sender_client_id=self.offer.author_client_id,
            sender_executor_id=self.offer.author_executor_id,
            type=MessageType.offer,
            body=None,
            offer_id=self.offer.id,
            offer=self.offer,
            attachments=[],
            created_at=datetime.now(timezone.utc),
        )


class FakeDatabase:
    committed = False

    async def commit(self):
        self.committed = True


class FakeRedisClient:
    def __init__(self):
        self.events = []

    async def publish_chat_event(self, **event):
        self.events.append(event)


@pytest.mark.asyncio
async def test_create_offer_persists_offer_and_publishes_chat_message(monkeypatch):
    database = FakeDatabase()
    repository = FakeRepository()
    redis = FakeRedisClient()
    monkeypatch.setattr(offer_service_module, "redis_client", redis)

    service = OfferService(cast(AsyncSession, database))
    service.repository = cast(ChatRepository, repository)
    result = await service.create(
        ChatActor(role=ActorType.executor, id=23),
        7,
        OfferCreate(price=Decimal("125.50"), terms="Доставка завтра"),
    )

    assert result.id == 31
    assert result.conversation_id == 19
    assert result.price == Decimal("125.50")
    assert result.currency == "BYN"
    assert database.committed
    assert redis.events[0]["event_type"] == EVENT_MESSAGE_CREATED
    assert redis.events[0]["data"]["message"]["offer_id"] == 31


@pytest.mark.asyncio
async def test_create_offer_rejects_closed_request_before_creating_conversation():
    database = FakeDatabase()
    service = OfferService(cast(AsyncSession, database))
    service.repository = cast(
        ChatRepository,
        FakeRepository(order_status=CargoRequestStatus.COMPLETED),
    )

    with pytest.raises(OfferRequestUnavailableError):
        await service.create(
            ChatActor(role=ActorType.executor, id=23),
            7,
            OfferCreate(price=Decimal("125.50")),
        )

    assert not database.committed


@pytest.mark.asyncio
async def test_counter_offer_creates_child_offer_and_publishes_chat_message(monkeypatch):
    database = FakeDatabase()
    repository = FakeRepository()
    redis = FakeRedisClient()
    monkeypatch.setattr(offer_service_module, "redis_client", redis)

    service = OfferService(cast(AsyncSession, database))
    service.repository = cast(ChatRepository, repository)
    result = await service.counter(
        ChatActor(role=ActorType.client, id=11),
        19,
        30,
        OfferCreate(price=Decimal("110.00"), terms="Заберу завтра"),
    )

    assert result.id == 32
    assert result.parent_offer_id == 30
    assert result.author_type is ActorType.client
    assert repository.parent_offer.status is OfferStatus.countered
    assert database.committed
    assert redis.events[0]["event_type"] == EVENT_MESSAGE_CREATED
    assert redis.events[0]["data"]["message"]["offer"]["price"] == "110.00"


@pytest.mark.asyncio
async def test_counter_offer_rejects_offer_from_same_actor():
    database = FakeDatabase()
    service = OfferService(cast(AsyncSession, database))
    service.repository = cast(ChatRepository, FakeRepository())

    with pytest.raises(offer_service_module.OfferCannotCounterOwnError):
        await service.counter(
            ChatActor(role=ActorType.executor, id=23),
            19,
            30,
            OfferCreate(price=Decimal("110.00")),
        )

    assert not database.committed


@pytest.mark.asyncio
async def test_accept_offer_starts_order_and_publishes_system_message(monkeypatch):
    database = FakeDatabase()
    repository = FakeRepository()
    redis = FakeRedisClient()
    monkeypatch.setattr(offer_service_module, "redis_client", redis)

    service = OfferService(cast(AsyncSession, database))
    service.repository = cast(ChatRepository, repository)
    result = await service.accept(
        ChatActor(role=ActorType.client, id=11),
        19,
        30,
    )

    assert result.status is OfferStatus.accepted
    assert repository.order.status is CargoRequestStatus.IN_PROGRESS
    assert database.committed
    assert [event["event_type"] for event in redis.events] == [
        offer_service_module.EVENT_OFFER_UPDATED,
        offer_service_module.EVENT_OFFER_UPDATED,
        EVENT_MESSAGE_CREATED,
    ]
    assert redis.events[1]["data"]["status"] == OfferStatus.declined.value
    assert redis.events[-1]["data"]["message"]["type"] == MessageType.system.value
    assert repository.other_pending_offer.status is OfferStatus.declined


@pytest.mark.asyncio
async def test_accept_offer_rejects_offer_from_same_actor():
    database = FakeDatabase()
    service = OfferService(cast(AsyncSession, database))
    service.repository = cast(ChatRepository, FakeRepository())

    with pytest.raises(offer_service_module.OfferCannotAcceptOwnError):
        await service.accept(
            ChatActor(role=ActorType.executor, id=23),
            19,
            30,
        )

    assert not database.committed


def test_offer_endpoint_is_registered_with_expected_status_codes():
    from main import app

    operation = app.openapi()["paths"]["/api/executor/orders/{order_id}/offers"]["post"]

    assert "201" in operation["responses"]
    assert "422" in operation["responses"]

    counter_operation = app.openapi()["paths"][
        "/api/conversations/{conversation_id}/offers/{offer_id}/counter"
    ]["post"]
    assert "201" in counter_operation["responses"]

    accept_operation = app.openapi()["paths"][
        "/api/conversations/{conversation_id}/offers/{offer_id}/accept"
    ]["post"]
    assert "200" in accept_operation["responses"]