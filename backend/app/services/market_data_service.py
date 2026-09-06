from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.providers.market_data import MarketDataProvider, MarketPrice


class MarketPriceNotFoundError(ValueError):
    """Raised when no market price is available for the requested asset/time."""


class MarketDataService:
    def __init__(self, provider: MarketDataProvider) -> None:
        self.provider = provider

    def get_latest_price(self, asset_id: UUID) -> MarketPrice:
        price = self.provider.get_latest_price(asset_id)
        if price is None:
            raise MarketPriceNotFoundError(f"No market price found for asset {asset_id}.")
        return price

    def get_price(self, asset_id: UUID, timestamp: datetime) -> MarketPrice:
        price = self.provider.get_price(asset_id, timestamp)
        if price is None:
            raise MarketPriceNotFoundError(
                f"No market price found for asset {asset_id} at {timestamp.isoformat()}"
            )
        return price
