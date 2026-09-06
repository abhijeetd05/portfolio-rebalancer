from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.schemas.portfolio import PortfolioCreate, PortfolioResponse, PortfolioUpdate
from app.services.portfolio_service import (
    PortfolioAccessDeniedError,
    PortfolioNotFoundError,
    PortfolioService,
)

router = APIRouter(prefix="/api/users", tags=["portfolios"])


@router.post(
    "/portfolios",
    response_model=PortfolioResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_portfolio(
    data: PortfolioCreate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> PortfolioResponse:
    service = PortfolioService()
    try:
        portfolio = service.create_portfolio(db, user_id, data)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return PortfolioResponse.model_validate(portfolio)


@router.get("/portfolios", response_model=list[PortfolioResponse])
def list_portfolios(
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> list[PortfolioResponse]:
    service = PortfolioService()
    portfolios = service.list_portfolios(db, user_id)
    return [PortfolioResponse.model_validate(portfolio) for portfolio in portfolios]


@router.get("/portfolios/{portfolio_id}", response_model=PortfolioResponse)
def get_portfolio(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> PortfolioResponse:
    service = PortfolioService()
    try:
        portfolio = service.get_portfolio(db, user_id, portfolio_id)
    except PortfolioNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return PortfolioResponse.model_validate(portfolio)


@router.put("/portfolios/{portfolio_id}", response_model=PortfolioResponse)
def update_portfolio(
    portfolio_id: UUID,
    data: PortfolioUpdate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> PortfolioResponse:
    service = PortfolioService()
    try:
        portfolio = service.update_portfolio(db, user_id, portfolio_id, data)
        db.commit()
    except PortfolioNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise
    return PortfolioResponse.model_validate(portfolio)


@router.delete(
    "/portfolios/{portfolio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_portfolio(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> Response:
    service = PortfolioService()
    try:
        deleted = service.delete_portfolio(db, user_id, portfolio_id)
        if deleted:
            db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portfolio {portfolio_id} was not found.",
            )
    except PortfolioNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
    return Response(status_code=status.HTTP_204_NO_CONTENT)
