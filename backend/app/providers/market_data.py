from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class MarketPrice:
    asset_id: UUID
    price: Decimal
    currency: str
    price_timestamp: datetime
    data_source: str


@dataclass(frozen=True)
class FXRate:
    from_currency: str
    to_currency: str
    exchange_rate: Decimal
    rate_timestamp: datetime
    data_source: str


class MarketDataProvider(Protocol):
    def get_latest_price(self, asset_id: UUID) -> MarketPrice | None:
        """Return the latest available market price for an asset."""

    def get_price(self, asset_id: UUID, timestamp: datetime) -> MarketPrice | None:
        """Return the market price applicable at the requested timestamp."""

    def get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
    ) -> FXRate | None:
        """Return the latest exchange rate for a currency pair."""
