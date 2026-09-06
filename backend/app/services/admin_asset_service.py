from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.repositories.asset_repository import AssetRepository
from app.repositories.user_repository import UserRepository


class AdminAccessDeniedError(PermissionError):
    pass


class AdminAssetNotFoundError(LookupError):
    pass


class AdminAssetService:
    def __init__(self, repository: AssetRepository | None = None) -> None:
        self.repository = repository or AssetRepository()
        self.user_repository = UserRepository()

    def _check_admin(self, db: Session, user_id: UUID) -> None:
        user = self.user_repository.get_by_id(db, user_id)
        if user is None or not user.is_admin:
            raise AdminAccessDeniedError("Administrator access is required.")

    def list_assets(self, db: Session, user_id: UUID) -> list[Asset]:
        self._check_admin(db, user_id)
        return self.repository.get_all(db)

    def create_asset(self, db: Session, user_id: UUID, data) -> Asset:
        self._check_admin(db, user_id)
        return self.repository.create(db, Asset(**data.model_dump(), is_active=True))

    def update_asset(self, db: Session, user_id: UUID, asset_id: UUID, data) -> Asset:
        self._check_admin(db, user_id)
        asset = self.repository.update(db, asset_id, data.model_dump(exclude_unset=True))
        if asset is None:
            raise AdminAssetNotFoundError(f"Asset {asset_id} was not found.")
        return asset
