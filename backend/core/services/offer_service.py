from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from client.models.enums.request_statuses import CargoRequestStatus
from core.dependencies import ChatActor
from core.exceptions import ChatError
from core.models.enums.actor_types import ActorType
from core.redis.chat import EVENT_MESSAGE_CREATED
from core.redis.redis_client import redis_client
from core.repositories.chat import ChatRepository
from core.schemas.chat import MessageRead
from core.schemas.offer import OfferCreate, OfferRead


class OfferRequestNotFoundError(ChatError):
    pass


class OfferRequestUnavailableError(ChatError):
    pass


class OfferAlreadyPendingError(ChatError):
    pass


class OfferService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = ChatRepository(db)

    async def create(self, actor: ChatActor, order_id: int, data: OfferCreate) -> OfferRead:
        if actor.role is not ActorType.executor:
            raise OfferRequestNotFoundError()

        order = await self.repository.get_order_for_offer(order_id)
        if order is None:
            raise OfferRequestNotFoundError()
        if order.status is not CargoRequestStatus.NEW:
            raise OfferRequestUnavailableError()

        conversation = await self.repository.get_or_create_offer_conversation(
            order_id=order.id,
            client_id=order.client_id,
            executor_id=actor.id,
        )
        pending_offer = await self.repository.get_pending_offer(conversation.id)
        if pending_offer is not None:
            raise OfferAlreadyPendingError()

        offer, message = await self.repository.create_offer_message(
            conversation=conversation,
            executor_id=actor.id,
            data=data,
        )
        await self.db.commit()

        stored_message = await self.repository.get_message(message.id)
        if stored_message is not None:
            await redis_client.publish_chat_event(
                client_id=conversation.client_id,
                executor_id=conversation.executor_id,
                event_type=EVENT_MESSAGE_CREATED,
                data={
                    "conversation_id": conversation.id,
                    "message": MessageRead.model_validate(stored_message).model_dump(
                        mode="json"
                    ),
                },
            )

        return OfferRead.model_validate(offer)