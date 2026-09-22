from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from datetime import datetime

from sqlalchemy import (
    Boolean, String, DateTime, func, ForeignKey, Text,
    CheckConstraint, Enum as SAEnum, Index, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from core.models.enums.post_creator_type import PostCreatorType

if TYPE_CHECKING:
    from executor.models.executor import Executor
    from client.models.client import Client


class Post(Base):
    __tablename__ = "posts"

    __table_args__ = (
        CheckConstraint(
            "(creator_type = 'client' AND client_id IS NOT NULL AND executor_id IS NULL) OR "
            "(creator_type = 'executor' AND executor_id IS NOT NULL AND client_id IS NULL)",
            name="ck_posts_single_creator",
        ),
        Index(
            "ix_posts_feed",
            "created_at",
            postgresql_where=text("NOT is_deleted"),
        ),
        Index(
            "ix_posts_client_created",
            "client_id",
            "created_at",
            postgresql_where=text("client_id IS NOT NULL AND NOT is_deleted"),
        ),
        Index(
            "ix_posts_executor_created",
            "executor_id",
            "created_at",
            postgresql_where=text("executor_id IS NOT NULL AND NOT is_deleted"),
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(255))
    request_text: Mapped[str] = mapped_column(Text)

    creator_type: Mapped[PostCreatorType] = mapped_column(
        SAEnum(
            PostCreatorType,
            name="post_creator_type",
            values_callable=lambda x: [e.value for e in x],
        )
    )
    client_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), nullable=True
    )
    executor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("executors.id", ondelete="CASCADE"), nullable=True
    )

    client: Mapped[Optional["Client"]] = relationship(back_populates="posts")
    executor: Mapped[Optional["Executor"]] = relationship(back_populates="posts")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")