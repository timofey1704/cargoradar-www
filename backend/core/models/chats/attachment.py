from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from core.models.enums.actor_types import ActorType

if TYPE_CHECKING:
    from core.models.chats.message import Message


class Attachment(Base):
    """Вложение (медиа) сообщения.

    Файл сохраняется в локальное хранилище (каталог ``uploads/``) и отдаётся
    статикой по ``/uploads/...``; здесь хранится относительный путь/URL и
    метаданные. ``message_id`` пуст до привязки вложения к сообщению.
    """

    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)

    # полиморфный загрузчик: клиент или исполнитель (system запрещён)
    uploader_type: Mapped[ActorType] = mapped_column(
        SAEnum(
            ActorType,
            name="attachment_uploader_type",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    uploader_client_id: Mapped[int | None] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), nullable=True
    )
    uploader_executor_id: Mapped[int | None] = mapped_column(
        ForeignKey("executors.id", ondelete="CASCADE"), nullable=True
    )

    message_id: Mapped[int | None] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # относительный путь к файлу в локальном хранилище, отдаётся по /uploads/...
    url: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    message: Mapped["Message | None"] = relationship(back_populates="attachments")

    __table_args__ = (
        CheckConstraint(
            "(uploader_type = 'client'   AND uploader_client_id IS NOT NULL AND uploader_executor_id IS NULL) OR "
            "(uploader_type = 'executor' AND uploader_executor_id IS NOT NULL AND uploader_client_id IS NULL)",
            name="ck_attachments_uploader",
        ),
    )