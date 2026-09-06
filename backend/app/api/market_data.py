from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.providers.external_market_data import ExternalMarketDataProvider
from app.schemas.market_data import MarketPriceResponse
from app.services.market_data_service import MarketDataService, MarketPriceNotFoundError

router = APIRouter(prefix="/api/assets", tags=["market-data"])


def get_market_data_service(db: Session = Depends(get_db)) -> MarketDataService:
    provider = ExternalMarketDataProvider(db)
    return MarketDataService(provider)


@router.get(
    "/{asset_id}/price/latest",
    response_model=MarketPriceResponse,
)
def get_latest_asset_price(
    asset_id: UUID,
    db: Session = Depends(get_db),
    service: MarketDataService = Depends(get_market_data_service),
    _user_id: UUID = Depends(get_current_user_id),
) -> MarketPriceResponse:
    try:
        price = service.get_latest_price(asset_id)
    except MarketPriceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    db.commit()
    return MarketPriceResponse.model_validate(price)


@router.get(
    "/{asset_id}/price",
    response_model=MarketPriceResponse,
)
def get_asset_price_at_timestamp(
    asset_id: UUID,
    timestamp: datetime = Query(...),
    db: Session = Depends(get_db),
    service: MarketDataService = Depends(get_market_data_service),
    _user_id: UUID = Depends(get_current_user_id),
) -> MarketPriceResponse:
    try:
        price = service.get_price(asset_id, timestamp)
    except MarketPriceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    db.commit()
    return MarketPriceResponse.model_validate(price)
