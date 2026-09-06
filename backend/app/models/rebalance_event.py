from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.portfolio import Portfolio
    from app.models.rebalance_action import RebalanceAction


class RebalanceEvent(Base):
    __tablename__ = "rebalance_events"

    rebalance_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    portfolio_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("portfolios.portfolio_id"),
        nullable=False,
        index=True,
    )

    trigger_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    trigger_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    recommended_action: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    portfolio: Mapped["Portfolio"] = relationship(
        back_populates="rebalance_events",
    )

    actions: Mapped[list["RebalanceAction"]] = relationship(
        back_populates="rebalance_event",
        cascade="all, delete-orphan",
    )