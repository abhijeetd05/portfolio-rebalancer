from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.core.database import get_db
from app.schemas.target_allocation import (
    TargetAllocationCreate,
    TargetAllocationResponse,
    TargetAllocationUpdate,
)
from app.services.portfolio_service import (
    PortfolioAccessDeniedError,
    PortfolioNotFoundError,
)
from app.services.target_allocation_service import (
    TargetAllocationConflictError,
    TargetAllocationNotFoundError,
    TargetAllocationService,
    TargetAllocationTotalExceededError,
)

router = APIRouter(prefix="/api/users/portfolios", tags=["target_allocations"])


@router.post(
    "/{portfolio_id}/target-allocations",
    response_model=TargetAllocationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_target_allocation(
    portfolio_id: UUID,
    data: TargetAllocationCreate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> TargetAllocationResponse:
    service = TargetAllocationService()
    try:
        target_allocation = service.create_target_allocation(
            db,
            user_id,
            portfolio_id,
            data,
        )
        db.commit()
    except PortfolioNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except TargetAllocationConflictError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except TargetAllocationTotalExceededError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise
    return TargetAllocationResponse.model_validate(target_allocation)


@router.get(
    "/{portfolio_id}/target-allocations",
    response_model=list[TargetAllocationResponse],
)
def list_target_allocations(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> list[TargetAllocationResponse]:
    service = TargetAllocationService()
    try:
        target_allocations = service.list_target_allocations(
            db,
            user_id,
            portfolio_id,
        )
    except PortfolioNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return [
        TargetAllocationResponse.model_validate(target_allocation)
        for target_allocation in target_allocations
    ]


@router.get(
    "/{portfolio_id}/target-allocations/{target_id}",
    response_model=TargetAllocationResponse,
)
def get_target_allocation(
    portfolio_id: UUID,
    target_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> TargetAllocationResponse:
    service = TargetAllocationService()
    try:
        target_allocation = service.get_target_allocation(
            db,
            user_id,
            portfolio_id,
            target_id,
        )
    except PortfolioNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except TargetAllocationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return TargetAllocationResponse.model_validate(target_allocation)


@router.put(
    "/{portfolio_id}/target-allocations/{target_id}",
    response_model=TargetAllocationResponse,
)
def update_target_allocation(
    portfolio_id: UUID,
    target_id: UUID,
    data: TargetAllocationUpdate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> TargetAllocationResponse:
    service = TargetAllocationService()
    try:
        target_allocation = service.update_target_allocation(
            db,
            user_id,
            portfolio_id,
            target_id,
            data,
        )
        db.commit()
    except PortfolioNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except TargetAllocationNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except TargetAllocationTotalExceededError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise
    return TargetAllocationResponse.model_validate(target_allocation)


@router.delete(
    "/{portfolio_id}/target-allocations/{target_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_target_allocation(
    portfolio_id: UUID,
    target_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> Response:
    service = TargetAllocationService()
    try:
        service.delete_target_allocation(
            db,
            user_id,
            portfolio_id,
            target_id,
        )
        db.commit()
    except PortfolioNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PortfolioAccessDeniedError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except TargetAllocationNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
    return Response(status_code=status.HTTP_204_NO_CONTENT)
