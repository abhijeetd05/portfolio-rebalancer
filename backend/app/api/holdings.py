from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.core.database import get_db
from app.schemas.holding import HoldingCreate, HoldingResponse, HoldingUpdate
from app.services.holding_service import (
    HoldingConflictError,
    HoldingNotFoundError,
    HoldingService,
)
from app.services.portfolio_service import (
    PortfolioAccessDeniedError,
    PortfolioNotFoundError,
)

router = APIRouter(prefix="/api/users/portfolios", tags=["holdings"])


@router.post(
    "/{portfolio_id}/holdings",
    response_model=HoldingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_holding(
    portfolio_id: UUID,
    data: HoldingCreate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> HoldingResponse:
    service = HoldingService()
    try:
        holding = service.create_holding(db, user_id, portfolio_id, data)
        db.commit()
    except PortfolioNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except HoldingConflictError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise
    return HoldingResponse.model_validate(holding)


@router.get(
    "/{portfolio_id}/holdings",
    response_model=list[HoldingResponse],
)
def list_holdings(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> list[HoldingResponse]:
    service = HoldingService()
    try:
        holdings = service.list_holdings(db, user_id, portfolio_id)
    except PortfolioNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return [HoldingResponse.model_validate(holding) for holding in holdings]


@router.get(
    "/{portfolio_id}/holdings/{holding_id}",
    response_model=HoldingResponse,
)
def get_holding(
    portfolio_id: UUID,
    holding_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> HoldingResponse:
    service = HoldingService()
    try:
        holding = service.get_holding(db, user_id, portfolio_id, holding_id)
    except PortfolioNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except HoldingNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return HoldingResponse.model_validate(holding)


@router.put(
    "/{portfolio_id}/holdings/{holding_id}",
    response_model=HoldingResponse,
)
def update_holding(
    portfolio_id: UUID,
    holding_id: UUID,
    data: HoldingUpdate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> HoldingResponse:
    service = HoldingService()
    try:
        holding = service.update_holding(db, user_id, portfolio_id, holding_id, data)
        db.commit()
    except PortfolioNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except HoldingNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise
    return HoldingResponse.model_validate(holding)


@router.delete(
    "/{portfolio_id}/holdings/{holding_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_holding(
    portfolio_id: UUID,
    holding_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> Response:
    service = HoldingService()
    try:
        deleted = service.delete_holding(db, user_id, portfolio_id, holding_id)
        if deleted:
            db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Holding {holding_id} was not found in portfolio {portfolio_id}.",
            )
    except PortfolioNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except HoldingNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
    return Response(status_code=status.HTTP_204_NO_CONTENT)
