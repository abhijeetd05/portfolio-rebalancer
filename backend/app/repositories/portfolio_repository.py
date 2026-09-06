from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio


class PortfolioRepository:
    def create(self, db: Session, portfolio: Portfolio) -> Portfolio:
        db.add(portfolio)
        db.flush()
        return portfolio

    def get_by_id(self, db: Session, portfolio_id: UUID) -> Portfolio | None:
        statement = select(Portfolio).where(Portfolio.portfolio_id == portfolio_id)
        return db.scalar(statement)

    def get_by_user_id(self, db: Session, user_id: UUID) -> list[Portfolio]:
        statement = select(Portfolio).where(Portfolio.user_id == user_id)
        return list(db.scalars(statement).all())

    def update(
        self,
        db: Session,
        portfolio_id: UUID,
        update_data: dict[str, Any],
    ) -> Portfolio | None:
        portfolio = self.get_by_id(db, portfolio_id)
        if portfolio is None:
            return None

        allowed_fields = {"portfolio_name", "base_currency"}
        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(portfolio, field, value)

        db.flush()
        return portfolio

    def delete(self, db: Session, portfolio_id: UUID) -> bool:
        portfolio = self.get_by_id(db, portfolio_id)
        if portfolio is None:
            return False

        db.delete(portfolio)
        db.flush()
        return True
