from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from client.models.enums.request_statuses import CargoRequestStatus
from core.dependencies import ChatActor
from core.exceptions import ChatError, ConversationNotFoundError
from core.models.enums.actor_types import ActorType
from core.models.enums.offer_statuses import OfferStatus
from core.redis.chat import EVENT_MESSAGE_CREATED, EVENT_OFFER_UPDATED
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


class OfferNotPendingError(ChatError):
    pass


class OfferCannotCounterOwnError(ChatError):
    pass


class OfferCannotAcceptOwnError(ChatError):
    pass


class OfferExpiredError(ChatError):
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

    async def counter(
        self,
        actor: ChatActor,
        conversation_id: int,
        offer_id: int,
        data: OfferCreate,
    ) -> OfferRead:
        conversation = await self.repository.get_participant_conversation(
            actor.role, actor.id, conversation_id
        )
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)

        parent_offer = await self.repository.get_offer_for_update(
            conversation.id, offer_id
        )
        if parent_offer is None:
            raise OfferRequestNotFoundError()
        if parent_offer.author_type is actor.role:
            raise OfferCannotCounterOwnError()
        if parent_offer.status is not OfferStatus.pending:
            raise OfferNotPendingError()

        offer, message = await self.repository.create_counter_offer_message(
            conversation=conversation,
            actor_type=actor.role,
            actor_id=actor.id,
            parent_offer=parent_offer,
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

    async def accept(
        self,
        actor: ChatActor,
        conversation_id: int,
        offer_id: int,
    ) -> OfferRead:
        conversation = await self.repository.get_participant_conversation(
            actor.role, actor.id, conversation_id
        )
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)

        offer = await self.repository.get_offer_for_update(conversation.id, offer_id)
        if offer is None:
            raise OfferRequestNotFoundError()
        if offer.author_type is actor.role:
            raise OfferCannotAcceptOwnError()
        if offer.status is not OfferStatus.pending:
            raise OfferNotPendingError()
        if offer.expires_at is not None and offer.expires_at <= datetime.now(timezone.utc):
            raise OfferExpiredError()

        order = await self.repository.get_order_for_offer(conversation.order_id)
        if order is None:
            raise OfferRequestNotFoundError()
        if order.status is not CargoRequestStatus.NEW:
            raise OfferRequestUnavailableError()

        message, closed_offers = await self.repository.accept_offer_for_order(
            conversation=conversation,
            order=order,
            offer=offer,
            body=(
                f"Предложение принято: {offer.price} {offer.currency}. "
                "Заказ взят в работу."
            ),
        )
        await self.db.commit()

        await redis_client.publish_chat_event(
            client_id=conversation.client_id,
            executor_id=conversation.executor_id,
            event_type=EVENT_OFFER_UPDATED,
            data={
                "conversation_id": conversation.id,
                "offer_id": offer.id,
                "status": OfferStatus.accepted.value,
            },
        )
        for closed_offer, closed_conversation in closed_offers:
            await redis_client.publish_chat_event(
                client_id=closed_conversation.client_id,
                executor_id=closed_conversation.executor_id,
                event_type=EVENT_OFFER_UPDATED,
                data={
                    "conversation_id": closed_conversation.id,
                    "offer_id": closed_offer.id,
                    "status": OfferStatus.declined.value,
                },
            )

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