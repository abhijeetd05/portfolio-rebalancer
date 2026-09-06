from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CHAR, Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.holding import Holding
    from app.models.price import Price
    from app.models.transaction import Transaction
    from app.models.rebalance_action import RebalanceAction


class Asset(Base):
    __tablename__ = "assets"

    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    asset_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    asset_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    asset_subtype: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    symbol: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    external_provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    external_asset_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        CHAR(3),
        nullable=False,
    )

    data_source: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        server_default="true",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    holdings: Mapped[list["Holding"]] = relationship(
        back_populates="asset",
    )

    prices: Mapped[list["Price"]] = relationship(
        back_populates="asset",
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="asset",
    )

    rebalance_actions: Mapped[list["RebalanceAction"]] = relationship(
        back_populates="asset",
    )