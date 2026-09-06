from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.repositories.asset_repository import AssetRepository


class AssetService:
    def __init__(self, repository: AssetRepository | None = None) -> None:
        self.repository = repository or AssetRepository()

    def list_active_assets(self, db: Session) -> list[Asset]:
        return self.repository.get_active(db)
