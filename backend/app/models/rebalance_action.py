from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.rebalance_event import RebalanceEvent
    from app.models.asset import Asset


class RebalanceAction(Base):
    __tablename__ = "rebalance_actions"

    action_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    rebalance_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("rebalance_events.rebalance_id"),
        nullable=False,
        index=True,
    )

    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("assets.asset_id"),
        nullable=False,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    current_allocation: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    target_allocation: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    recommended_value: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    rebalance_event: Mapped["RebalanceEvent"] = relationship(
        back_populates="actions",
    )

    asset: Mapped["Asset"] = relationship(
        back_populates="rebalance_actions",
    )