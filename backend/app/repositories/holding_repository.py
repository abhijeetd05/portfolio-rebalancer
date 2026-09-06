from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.holding import Holding


class HoldingRepository:
    def create(self, db: Session, holding: Holding) -> Holding:
        db.add(holding)
        db.flush()
        return holding

    def get_by_id(self, db: Session, holding_id: UUID) -> Holding | None:
        statement = select(Holding).where(Holding.holding_id == holding_id)
        return db.scalar(statement)

    def get_by_portfolio_id(self, db: Session, portfolio_id: UUID) -> list[Holding]:
        statement = select(Holding).where(Holding.portfolio_id == portfolio_id)
        return list(db.scalars(statement).all())

    def get_by_portfolio_and_asset(
        self,
        db: Session,
        portfolio_id: UUID,
        asset_id: UUID,
    ) -> Holding | None:
        statement = select(Holding).where(
            Holding.portfolio_id == portfolio_id,
            Holding.asset_id == asset_id,
        )
        return db.scalar(statement)

    def update(
        self,
        db: Session,
        holding_id: UUID,
        update_data: dict[str, Any],
    ) -> Holding | None:
        holding = self.get_by_id(db, holding_id)
        if holding is None:
            return None

        allowed_fields = {"units", "avg_buy_price", "purchase_date"}
        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(holding, field, value)

        db.flush()
        return holding

    def delete(self, db: Session, holding_id: UUID) -> bool:
        holding = self.get_by_id(db, holding_id)
        if holding is None:
            return False

        db.delete(holding)
        db.flush()
        return True
