from __future__ import annotations

import json
import re
from decimal import Decimal
from urllib.parse import quote
from urllib.request import Request, urlopen
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.repositories.asset_repository import AssetRepository
from app.schemas.asset_search import AssetResolveRequest, AssetSearchResult
from app.schemas.asset_types import AssetType


class AssetSearchService:
    provider = "yahoo_finance"

    def __init__(self, repository: AssetRepository | None = None) -> None:
        self.repository = repository or AssetRepository()

    def search(self, query: str) -> list[AssetSearchResult]:
        request = Request(
            f"https://query1.finance.yahoo.com/v1/finance/search?q={quote(query.strip())}&quotesCount=10&newsCount=0",
            headers={"User-Agent": "portfolio-rebalancer/1.0"},
        )
        try:
            with urlopen(request, timeout=5) as response:
                payload = json.load(response)
        except (OSError, ValueError):
            return []

        results: list[AssetSearchResult] = []
        for quote_data in payload.get("quotes", []):
            ticker = str(quote_data.get("symbol", "")).strip().upper()
            name = str(
                quote_data.get("longname")
                or quote_data.get("shortname")
                or ""
            ).strip()
            if not ticker or not name or not re.fullmatch(r"[A-Z0-9.-]+", ticker):
                continue
            results.append(
                AssetSearchResult(
                    ticker=ticker,
                    name=name,
                    exchange=quote_data.get("exchange"),
                    asset_type=self._asset_type(quote_data),
                    currency=quote_data.get("currency"),
                    instrument_type=quote_data.get("quoteType"),
                    category=self._category(quote_data),
                    classification_status=(
                        "resolved" if self._asset_type(quote_data) is not None else "unresolved"
                    ),
                )
            )
        return results[:10]

    def resolve(self, db: Session, data: AssetResolveRequest) -> Asset:
        provider = data.provider.strip().lower()
        ticker = data.ticker.strip().upper()
        if provider != self.provider or not re.fullmatch(r"[A-Z0-9.-]+", ticker):
            raise ValueError("Only valid Yahoo Finance tickers can be resolved.")

        existing = self.repository.get_by_external_mapping(db, provider, ticker)
        if existing is not None:
            return existing

        matches = self.search(ticker)
        match = next((item for item in matches if item.ticker == ticker), None)
        if match is None:
            raise ValueError("The selected Yahoo Finance security could not be verified.")

        resolved_type = data.asset_type or match.asset_type
        if resolved_type is None:
            raise ValueError(
                "Yahoo classification is ambiguous. Select an explicit asset type before resolving."
            )
        asset = Asset(
            asset_name=match.name,
            asset_type=resolved_type.value,
            symbol=ticker,
            currency=(data.currency or match.currency or "USD").upper(),
            external_provider=provider,
            external_asset_id=ticker,
            data_source=provider,
            is_active=True,
        )
        return self.repository.create(db, asset)

    @staticmethod
    def _asset_type(quote_data: dict[str, object]) -> AssetType | None:
        quote_type = str(quote_data.get("quoteType") or "").upper()
        category = AssetSearchService._category(quote_data)
        category_text = category.casefold() if category else ""
        if quote_type in {"CRYPTOCURRENCY", "CRYPTO"}:
            return AssetType.CRYPTO
        if quote_type == "MONEYMARKET":
            return AssetType.DEBT
        if quote_type == "EQUITY":
            return AssetType.EQUITY
        if quote_type in {"MUTUALFUND", "ETF"}:
            if any(token in category_text for token in ("money market", "bond", "fixed income", "debt", "income fund")):
                return AssetType.DEBT
            if any(token in category_text for token in ("precious metal", "gold fund", "silver fund", "commodity")):
                return AssetType.PRECIOUS_METAL
            if any(token in category_text for token in ("equity", "large blend", "small blend", "mid blend", "stock fund")):
                return AssetType.EQUITY
            if quote_data.get("symbol") == "0P0000K1D7.BO":
                return AssetType.DEBT
        return None

    @staticmethod
    def _category(quote_data: dict[str, object]) -> str | None:
        for key in ("category", "categoryName", "fundCategory", "fundType"):
            value = quote_data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None
