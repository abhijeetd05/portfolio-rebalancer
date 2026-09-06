from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.core.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate
from app.services.portfolio_service import (
    PortfolioAccessDeniedError,
    PortfolioNotFoundError,
)
from app.services.transaction_service import (
    TransactionNotFoundError,
    TransactionService,
)

router = APIRouter(prefix="/api/users/portfolios", tags=["transactions"])


@router.post(
    "/{portfolio_id}/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    portfolio_id: UUID,
    data: TransactionCreate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> TransactionResponse:
    service = TransactionService()
    try:
        transaction = service.create_transaction(db, user_id, portfolio_id, data)
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
    return TransactionResponse.model_validate(transaction)


@router.get(
    "/{portfolio_id}/transactions",
    response_model=list[TransactionResponse],
)
def list_transactions(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> list[TransactionResponse]:
    service = TransactionService()
    try:
        transactions = service.list_transactions(db, user_id, portfolio_id)
    except PortfolioNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return [TransactionResponse.model_validate(transaction) for transaction in transactions]


@router.get(
    "/{portfolio_id}/transactions/{transaction_id}",
    response_model=TransactionResponse,
)
def get_transaction(
    portfolio_id: UUID,
    transaction_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> TransactionResponse:
    service = TransactionService()
    try:
        transaction = service.get_transaction(db, user_id, portfolio_id, transaction_id)
    except PortfolioNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except TransactionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return TransactionResponse.model_validate(transaction)


@router.get(
    "/{portfolio_id}/transactions/asset/{asset_id}",
    response_model=list[TransactionResponse],
)
def list_transactions_by_asset(
    portfolio_id: UUID,
    asset_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> list[TransactionResponse]:
    service = TransactionService()
    try:
        transactions = service.list_transactions_by_asset(db, user_id, portfolio_id, asset_id)
    except PortfolioNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return [TransactionResponse.model_validate(transaction) for transaction in transactions]


@router.put(
    "/{portfolio_id}/transactions/{transaction_id}",
    response_model=TransactionResponse,
)
def update_transaction(
    portfolio_id: UUID,
    transaction_id: UUID,
    data: TransactionUpdate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> TransactionResponse:
    service = TransactionService()
    try:
        transaction = service.update_transaction(db, user_id, portfolio_id, transaction_id, data)
        db.commit()
    except PortfolioNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except TransactionNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise
    return TransactionResponse.model_validate(transaction)


@router.delete(
    "/{portfolio_id}/transactions/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_transaction(
    portfolio_id: UUID,
    transaction_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> Response:
    service = TransactionService()
    try:
        deleted = service.delete_transaction(db, user_id, portfolio_id, transaction_id)
        if deleted:
            db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction {transaction_id} was not found in portfolio {portfolio_id}.",
            )
    except PortfolioNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except TransactionNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
    return Response(status_code=status.HTTP_204_NO_CONTENT)
