from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.schemas.asset import AssetResponse
from app.schemas.asset_search import AssetResolveRequest, AssetSearchResult
from app.services.asset_service import AssetService
from app.services.asset_search_service import AssetSearchService

router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.get("/search", response_model=list[AssetSearchResult])
def search_assets(
    q: str = Query(..., min_length=2, max_length=100),
    _user_id=Depends(get_current_user_id),
) -> list[AssetSearchResult]:
    return AssetSearchService().search(q)


@router.post("/resolve", response_model=AssetResponse)
def resolve_asset(
    data: AssetResolveRequest,
    db: Session = Depends(get_db),
    _user_id=Depends(get_current_user_id),
) -> AssetResponse:
    try:
        asset = AssetSearchService().resolve(db, data)
        db.commit()
        db.refresh(asset)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise
    return AssetResponse.model_validate(asset)


@router.get("", response_model=list[AssetResponse])
def list_assets(
    db: Session = Depends(get_db),
    _user_id=Depends(get_current_user_id),
) -> list[AssetResponse]:
    assets = AssetService().list_active_assets(db)
    return [AssetResponse.model_validate(asset) for asset in assets]
