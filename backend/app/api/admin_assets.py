from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.schemas.admin_asset import AdminAssetCreate, AdminAssetResponse, AdminAssetUpdate
from app.services.admin_asset_service import (
    AdminAccessDeniedError,
    AdminAssetNotFoundError,
    AdminAssetService,
)

router = APIRouter(prefix="/api/admin/assets", tags=["admin-assets"])


def _admin_error(exc: Exception) -> HTTPException:
    if isinstance(exc, AdminAccessDeniedError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("", response_model=list[AdminAssetResponse])
def list_admin_assets(
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> list[AdminAssetResponse]:
    try:
        assets = AdminAssetService().list_assets(db, user_id)
    except AdminAccessDeniedError as exc:
        raise _admin_error(exc) from exc
    return [AdminAssetResponse.model_validate(asset) for asset in assets]


@router.post("", response_model=AdminAssetResponse, status_code=status.HTTP_201_CREATED)
def create_admin_asset(
    data: AdminAssetCreate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> AdminAssetResponse:
    try:
        asset = AdminAssetService().create_asset(db, user_id, data)
        db.commit()
        db.refresh(asset)
    except AdminAccessDeniedError as exc:
        db.rollback()
        raise _admin_error(exc) from exc
    except Exception:
        db.rollback()
        raise
    return AdminAssetResponse.model_validate(asset)


@router.put("/{asset_id}", response_model=AdminAssetResponse)
def update_admin_asset(
    asset_id: UUID,
    data: AdminAssetUpdate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> AdminAssetResponse:
    try:
        asset = AdminAssetService().update_asset(db, user_id, asset_id, data)
        db.commit()
        db.refresh(asset)
    except (AdminAccessDeniedError, AdminAssetNotFoundError) as exc:
        db.rollback()
        raise _admin_error(exc) from exc
    except Exception:
        db.rollback()
        raise
    return AdminAssetResponse.model_validate(asset)
