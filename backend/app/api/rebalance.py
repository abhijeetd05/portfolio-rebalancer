from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.core.database import get_db
from app.providers.external_market_data import ExternalMarketDataProvider
from app.schemas.rebalance import (
    RebalanceActionResponse,
    RebalanceEventCreate,
    RebalanceEventResponse,
)
from app.services.market_data_service import MarketDataService
from app.services.portfolio_service import (
    PortfolioAccessDeniedError,
    PortfolioNotFoundError,
)
from app.services.rebalance_service import (
    RebalanceCalculationError,
    RebalanceNotFoundError,
    RebalanceResult,
    RebalanceService,
)
from app.services.valuation_service import ValuationService

router = APIRouter(prefix="/api/users/portfolios", tags=["rebalance"])


def get_rebalance_service(db: Session = Depends(get_db)) -> RebalanceService:
    market_data_service = MarketDataService(ExternalMarketDataProvider(db))
    return RebalanceService(
        valuation_service=ValuationService(market_data_service=market_data_service)
    )


def _serialize_result(result: RebalanceResult) -> dict[str, object]:
    event = RebalanceEventResponse.model_validate(result.event)
    actions = [
        RebalanceActionResponse.model_validate(action)
        for action in result.actions
    ]
    return {
        "event": event.model_dump(mode="json"),
        "actions": [action.model_dump(mode="json") for action in actions],
    }


def _map_service_error(exc: Exception) -> HTTPException:
    if isinstance(exc, PortfolioNotFoundError | RebalanceNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    if isinstance(exc, PortfolioAccessDeniedError):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )
    if isinstance(exc, RebalanceCalculationError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    raise exc


@router.post(
    "/{portfolio_id}/rebalances",
    status_code=status.HTTP_201_CREATED,
)
def create_rebalance(
    portfolio_id: UUID,
    data: RebalanceEventCreate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    service: RebalanceService = Depends(get_rebalance_service),
) -> dict[str, object]:
    try:
        result = service.create_rebalance(db, user_id, portfolio_id, data)
        db.commit()
    except (PortfolioNotFoundError, PortfolioAccessDeniedError, RebalanceCalculationError) as exc:
        db.rollback()
        raise _map_service_error(exc) from exc
    except Exception:
        db.rollback()
        raise
    return _serialize_result(result)


@router.get(
    "/{portfolio_id}/rebalances/{rebalance_id}",
)
def get_rebalance(
    portfolio_id: UUID,
    rebalance_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    service: RebalanceService = Depends(get_rebalance_service),
) -> dict[str, object]:
    try:
        result = service.get_rebalance(
            db,
            user_id,
            portfolio_id,
            rebalance_id,
        )
    except (
        PortfolioNotFoundError,
        PortfolioAccessDeniedError,
        RebalanceNotFoundError,
    ) as exc:
        raise _map_service_error(exc) from exc
    return _serialize_result(result)


@router.get(
    "/{portfolio_id}/rebalances",
)
def list_rebalances(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    service: RebalanceService = Depends(get_rebalance_service),
) -> list[dict[str, object]]:
    try:
        results = service.list_rebalances(db, user_id, portfolio_id)
    except (PortfolioNotFoundError, PortfolioAccessDeniedError) as exc:
        raise _map_service_error(exc) from exc
    return [_serialize_result(result) for result in results]
