from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.core.database import get_db
from app.providers.external_market_data import ExternalMarketDataProvider
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService
from app.services.market_data_service import MarketDataService, MarketPriceNotFoundError
from app.services.portfolio_service import (
    PortfolioAccessDeniedError,
    PortfolioNotFoundError,
)
from app.services.valuation_service import ValuationService

router = APIRouter(prefix="/api/users/portfolios", tags=["dashboard"])


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    market_data_service = MarketDataService(ExternalMarketDataProvider(db))
    valuation_service = ValuationService(market_data_service=market_data_service)
    return DashboardService(valuation_service=valuation_service)


@router.get(
    "/{portfolio_id}/dashboard",
    response_model=DashboardResponse,
)
def get_dashboard(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardResponse:
    try:
        response = service.get_dashboard(db, user_id, portfolio_id)
        db.commit()
        return response
    except PortfolioNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PortfolioAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except MarketPriceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
