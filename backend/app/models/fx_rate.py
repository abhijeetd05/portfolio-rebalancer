from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CHAR,
    BigInteger,
    DateTime,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FXRate(Base):
    __tablename__ = "fx_rates"

    __table_args__ = (
        UniqueConstraint(
            "from_currency",
            "to_currency",
            "rate_timestamp",
            name="uq_fx_rates_currency_timestamp",
        ),
    )

    fx_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    from_currency: Mapped[str] = mapped_column(
        CHAR(3),
        nullable=False,
    )

    to_currency: Mapped[str] = mapped_column(
        CHAR(3),
        nullable=False,
    )

    exchange_rate: Mapped[Decimal] = mapped_column(
        Numeric(18, 6),
        nullable=False,
    )

    rate_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    data_source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )