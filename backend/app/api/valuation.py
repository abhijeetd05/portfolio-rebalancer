from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.core.database import get_db
from app.providers.external_market_data import ExternalMarketDataProvider
from app.repositories.holding_repository import HoldingRepository
from app.repositories.portfolio_repository import PortfolioRepository
from app.schemas.valuation import PortfolioValuationResponse
from app.services.market_data_service import MarketDataService, MarketPriceNotFoundError
from app.services.portfolio_service import (
    PortfolioAccessDeniedError,
    PortfolioNotFoundError,
)
from app.services.valuation_service import ValuationService

router = APIRouter(prefix="/api/users/portfolios", tags=["valuation"])


def get_valuation_service(db: Session = Depends(get_db)) -> ValuationService:
    provider = ExternalMarketDataProvider(db)
    market_data_service = MarketDataService(provider)
    return ValuationService(
        holding_repository=HoldingRepository(),
        portfolio_repository=PortfolioRepository(),
        market_data_service=market_data_service,
    )


@router.get(
    "/{portfolio_id}/valuation",
    response_model=PortfolioValuationResponse,
)
def get_portfolio_valuation(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    service: ValuationService = Depends(get_valuation_service),
) -> PortfolioValuationResponse:
    try:
        valuation = service.get_portfolio_valuation(db, user_id, portfolio_id)
    except PortfolioNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except MarketPriceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    db.commit()
    return PortfolioValuationResponse.model_validate(valuation)
