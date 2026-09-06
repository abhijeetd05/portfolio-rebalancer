from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset


class AssetRepository:
    def get_all(self, db: Session) -> list[Asset]:
        return list(db.scalars(select(Asset).order_by(Asset.asset_name, Asset.symbol)).all())

    def get_active(self, db: Session) -> list[Asset]:
        return list(
            db.scalars(
                select(Asset)
                .where(Asset.is_active.is_(True))
                .order_by(Asset.asset_name, Asset.symbol)
            ).all()
        )

    def get_by_id(self, db: Session, asset_id: UUID) -> Asset | None:
        return db.get(Asset, asset_id)

    def get_by_external_mapping(
        self, db: Session, provider: str, external_asset_id: str
    ) -> Asset | None:
        return db.scalar(
            select(Asset).where(
                Asset.external_provider == provider,
                Asset.external_asset_id == external_asset_id,
            )
        )

    def create(self, db: Session, asset: Asset) -> Asset:
        db.add(asset)
        db.flush()
        return asset

    def update(self, db: Session, asset_id: UUID, data: dict[str, object]) -> Asset | None:
        asset = self.get_by_id(db, asset_id)
        if asset is None:
            return None
        for field, value in data.items():
            setattr(asset, field, value)
        db.flush()
        return asset
