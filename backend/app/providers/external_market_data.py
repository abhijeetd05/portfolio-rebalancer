from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from urllib.error import URLError
from urllib.request import Request, urlopen
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.asset import Asset
from app.models.fx_rate import FXRate as FXRateRecord
from app.models.price import Price
from app.providers.market_data import FXRate, MarketDataProvider, MarketPrice


class ExternalMarketDataProvider(MarketDataProvider):
    provider_name = "yahoo_finance"

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_latest_price(self, asset_id: UUID) -> MarketPrice | None:
        asset = self.db.get(Asset, asset_id)
        if asset is None:
            return None

        cached = self._cached_price(asset_id)
        if cached is not None and cached.price_timestamp >= datetime.now(timezone.utc) - timedelta(
            seconds=settings.market_price_cache_seconds
        ):
            return self._to_market_price(cached)

        if asset.external_provider != self.provider_name or not asset.external_asset_id:
            return self._to_market_price(cached) if cached is not None else None

        fetched = self._fetch(asset)
        if fetched is None:
            return self._to_market_price(cached) if cached is not None else None

        existing = self.db.scalar(
            select(Price).where(
                Price.asset_id == asset.asset_id,
                Price.price_timestamp == fetched.price_timestamp,
            )
        )
        if existing is None:
            self.db.add(
                Price(
                    asset_id=asset.asset_id,
                    price=fetched.price,
                    currency=fetched.currency,
                    price_timestamp=fetched.price_timestamp,
                    data_source=fetched.data_source,
                )
            )
            self.db.flush()
        return fetched

    def get_price(self, asset_id: UUID, timestamp: datetime) -> MarketPrice | None:
        statement = (
            select(Price)
            .where(Price.asset_id == asset_id, Price.price_timestamp <= timestamp)
            .order_by(Price.price_timestamp.desc())
            .limit(1)
        )
        price = self.db.scalar(statement)
        return self._to_market_price(price) if price is not None else None

    def get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
    ) -> FXRate | None:
        source = from_currency.upper()
        target = to_currency.upper()
        if source == target:
            return FXRate(
                from_currency=source,
                to_currency=target,
                exchange_rate=Decimal("1"),
                rate_timestamp=datetime.now(timezone.utc),
                data_source=self.provider_name,
            )

        for direct_source, direct_target, inverse in (
            (source, target, False),
            (target, source, True),
        ):
            cached = self._cached_exchange_rate(direct_source, direct_target)
            if cached is None or cached.rate_timestamp < datetime.now(timezone.utc) - timedelta(
                seconds=settings.market_price_cache_seconds
            ):
                fetched = self._fetch_exchange_rate(direct_source, direct_target)
                if fetched is not None:
                    cached = self._persist_exchange_rate(fetched)
            if cached is not None:
                rate = cached.exchange_rate
                if inverse:
                    rate = Decimal("1") / rate
                return FXRate(
                    from_currency=source,
                    to_currency=target,
                    exchange_rate=rate,
                    rate_timestamp=cached.rate_timestamp,
                    data_source=cached.data_source,
                )
        return None

    def _cached_price(self, asset_id: UUID) -> Price | None:
        return self.db.scalar(
            select(Price)
            .where(Price.asset_id == asset_id)
            .order_by(Price.price_timestamp.desc())
            .limit(1)
        )

    def _cached_exchange_rate(self, from_currency: str, to_currency: str) -> FXRateRecord | None:
        return self.db.scalar(
            select(FXRateRecord)
            .where(
                FXRateRecord.from_currency == from_currency,
                FXRateRecord.to_currency == to_currency,
            )
            .order_by(FXRateRecord.rate_timestamp.desc())
            .limit(1)
        )

    def _fetch_exchange_rate(self, from_currency: str, to_currency: str) -> FXRate | None:
        request = Request(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{from_currency}{to_currency}=X",
            headers={"User-Agent": "portfolio-rebalancer/1.0"},
        )
        try:
            with urlopen(request, timeout=5) as response:
                payload = json.load(response)
        except (OSError, URLError, ValueError):
            return None

        results = payload.get("chart", {}).get("result") or []
        if not results:
            return None
        meta = results[0].get("meta") or {}
        raw_rate = meta.get("regularMarketPrice")
        raw_timestamp = meta.get("regularMarketTime")
        if raw_rate is None or raw_timestamp is None:
            return None
        return FXRate(
            from_currency=from_currency,
            to_currency=to_currency,
            exchange_rate=Decimal(str(raw_rate)),
            rate_timestamp=datetime.fromtimestamp(raw_timestamp, tz=timezone.utc),
            data_source=self.provider_name,
        )

    def _persist_exchange_rate(self, fetched: FXRate) -> FXRateRecord:
        existing = self._cached_exchange_rate(fetched.from_currency, fetched.to_currency)
        if existing is not None and existing.rate_timestamp == fetched.rate_timestamp:
            return existing
        record = FXRateRecord(
            from_currency=fetched.from_currency,
            to_currency=fetched.to_currency,
            exchange_rate=fetched.exchange_rate,
            rate_timestamp=fetched.rate_timestamp,
            data_source=fetched.data_source,
        )
        self.db.add(record)
        self.db.flush()
        return record

    def _fetch(self, asset: Asset) -> MarketPrice | None:
        request = Request(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{asset.external_asset_id}",
            headers={"User-Agent": "portfolio-rebalancer/1.0"},
        )
        try:
            with urlopen(request, timeout=5) as response:
                payload = json.load(response)
        except (OSError, URLError, ValueError):
            return None

        results = payload.get("chart", {}).get("result") or []
        if not results:
            return None
        meta = results[0].get("meta") or {}
        raw_price = meta.get("regularMarketPrice")
        if raw_price is None:
            return None
        raw_timestamp = meta.get("regularMarketTime")
        if raw_timestamp is None:
            return None
        timestamp = datetime.fromtimestamp(raw_timestamp, tz=timezone.utc)
        return MarketPrice(
            asset_id=asset.asset_id,
            price=Decimal(str(raw_price)),
            currency=str(meta.get("currency") or asset.currency),
            price_timestamp=timestamp,
            data_source=self.provider_name,
        )

    @staticmethod
    def _to_market_price(price: Price | None) -> MarketPrice | None:
        if price is None:
            return None
        return MarketPrice(
            asset_id=price.asset_id,
            price=price.price,
            currency=price.currency,
            price_timestamp=price.price_timestamp,
            data_source=price.data_source,
        )
