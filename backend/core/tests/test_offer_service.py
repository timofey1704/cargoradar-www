from datetime import datetime, timezone
from decimal import Decimal
from dataclasses import dataclass
from types import SimpleNamespace
from typing import cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from client.models.enums.request_statuses import CargoRequestStatus
from core.dependencies import ChatActor
from core.models.enums.actor_types import ActorType
from core.models.enums.message_types import MessageType
from core.repositories.chat import ChatRepository
from core.redis.chat import EVENT_MESSAGE_CREATED
from core.schemas.offer import OfferCreate
from core.services import offer_service as offer_service_module
from core.services.offer_service import OfferRequestUnavailableError, OfferService


@dataclass
class FakeConversation:
    id: int = 19
    client_id: int = 11
    executor_id: int = 23


class FakeRepository:
    def __init__(self, *, order_status=CargoRequestStatus.NEW):
        self.order = SimpleNamespace(id=7, client_id=11, status=order_status)
        self.conversation = FakeConversation()
        self.offer = None
        self.message = None

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
            price=data.price,
            currency="BYN",
            terms=data.terms,
            status="pending",
            created_at=datetime.now(timezone.utc),
        )
        self.message = SimpleNamespace(id=41)
        return self.offer, self.message

    async def get_message(self, message_id):
        assert message_id == 41
        return SimpleNamespace(
            id=41,
            conversation_id=19,
            sender_type=ActorType.executor,
            sender_client_id=None,
            sender_executor_id=23,
            type=MessageType.offer,
            body=None,
            offer_id=31,
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


def test_offer_endpoint_is_registered_with_expected_status_codes():
    from main import app

    operation = app.openapi()["paths"]["/api/executor/orders/{order_id}/offers"]["post"]

    assert "201" in operation["responses"]
    assert "422" in operation["responses"]