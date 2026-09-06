from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.target_allocation import TargetAllocation


class TargetAllocationRepository:
    def create(self, db: Session, target_allocation: TargetAllocation) -> TargetAllocation:
        db.add(target_allocation)
        db.flush()
        return target_allocation

    def get_by_id(self, db: Session, target_id: UUID) -> TargetAllocation | None:
        statement = select(TargetAllocation).where(TargetAllocation.target_id == target_id)
        return db.scalar(statement)

    def get_by_portfolio_id(self, db: Session, portfolio_id: UUID) -> list[TargetAllocation]:
        statement = select(TargetAllocation).where(
            TargetAllocation.portfolio_id == portfolio_id
        )
        return list(db.scalars(statement).all())

    def get_by_portfolio_and_asset_type(
        self,
        db: Session,
        portfolio_id: UUID,
        asset_type: str,
    ) -> TargetAllocation | None:
        statement = select(TargetAllocation).where(
            TargetAllocation.portfolio_id == portfolio_id,
            TargetAllocation.asset_type == asset_type,
        )
        return db.scalar(statement)

    def update(
        self,
        db: Session,
        target_id: UUID,
        update_data: dict[str, Any],
    ) -> TargetAllocation | None:
        target_allocation = self.get_by_id(db, target_id)
        if target_allocation is None:
            return None

        allowed_fields = {"target_percentage"}
        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(target_allocation, field, value)

        db.flush()
        return target_allocation

    def delete(self, db: Session, target_id: UUID) -> bool:
        target_allocation = self.get_by_id(db, target_id)
        if target_allocation is None:
            return False

        db.delete(target_allocation)
        db.flush()
        return True
