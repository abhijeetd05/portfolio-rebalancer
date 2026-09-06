from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.price import Price
from app.providers.market_data import FXRate, MarketDataProvider, MarketPrice


class StaticMarketDataProvider(MarketDataProvider):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_latest_price(self, asset_id: UUID) -> MarketPrice | None:
        statement = (
            select(Price)
            .where(Price.asset_id == asset_id)
            .order_by(Price.price_timestamp.desc())
            .limit(1)
        )
        price_record = self.db.scalar(statement)
        if price_record is None:
            return None

        return MarketPrice(
            asset_id=price_record.asset_id,
            price=price_record.price,
            currency=price_record.currency,
            price_timestamp=price_record.price_timestamp,
            data_source=price_record.data_source,
        )

    def get_price(self, asset_id: UUID, timestamp: datetime) -> MarketPrice | None:
        statement = (
            select(Price)
            .where(
                Price.asset_id == asset_id,
                Price.price_timestamp <= timestamp,
            )
            .order_by(Price.price_timestamp.desc())
            .limit(1)
        )
        price_record = self.db.scalar(statement)
        if price_record is None:
            return None

        return MarketPrice(
            asset_id=price_record.asset_id,
            price=price_record.price,
            currency=price_record.currency,
            price_timestamp=price_record.price_timestamp,
            data_source=price_record.data_source,
        )

    def get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
    ) -> FXRate | None:
        return None
