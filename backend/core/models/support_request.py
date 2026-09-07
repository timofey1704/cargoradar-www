from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from core.database import Base

from core.models.enums.support_statuses import SupportRequestTypes, RequestStatuses


if TYPE_CHECKING:
    from executor.models.executor import Executor
    from client.models.client import Client
    from admin.models.admin import Admin
    
class SupportRequest(Base):
    """Заявки в службу поддержки от клиентов и исполнителей"""

    __tablename__ = "support_requests"
    __table_args__ = (
        # заявка привязана ровно к одному владельцу: либо клиент, либо исполнитель
        CheckConstraint(
            "(client_id IS NULL) <> (executor_id IS NULL)",
            name="ck_request_one_owner",
        ),
        # заявка не может быть без админа, если статус !new
       CheckConstraint(
            "status = 'new' OR admin_id IS NOT NULL",
            name="ck_support_request_admin_required",
        )
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id"), index=True)
    executor_id: Mapped[int | None] = mapped_column(ForeignKey("executors.id"), index=True)
    admin_id: Mapped[int | None] = mapped_column(ForeignKey("admins.id"), index=True)
    
    client: Mapped["Client | None"] = relationship(back_populates="support_requests")
    executor: Mapped["Executor | None"] = relationship(back_populates="support_requests")
    admin: Mapped["Admin| None"] = relationship(back_populates="support_requests")
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    request_type: Mapped[SupportRequestTypes] = mapped_column(
    SQLEnum(
        SupportRequestTypes,
        name="support_request_type_enum",
        values_callable=lambda x: [e.value for e in x],
        ),
    nullable=False,
    index=True)
    
    status: Mapped[RequestStatuses] = mapped_column(
    SQLEnum(
        RequestStatuses,
        name="support_request_status_enum",
        values_callable=lambda x: [e.value for e in x],
    ),
    default=RequestStatuses.NEW,
    nullable=False,
    index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    support_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)