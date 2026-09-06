from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rebalance_event import RebalanceEvent


class RebalanceEventRepository:
    def create(self, db: Session, rebalance_event: RebalanceEvent) -> RebalanceEvent:
        db.add(rebalance_event)
        db.flush()
        return rebalance_event

    def get_by_id(self, db: Session, rebalance_id: UUID) -> RebalanceEvent | None:
        statement = select(RebalanceEvent).where(
            RebalanceEvent.rebalance_id == rebalance_id
        )
        return db.scalar(statement)

    def get_by_portfolio_id(
        self,
        db: Session,
        portfolio_id: UUID,
    ) -> list[RebalanceEvent]:
        statement = select(RebalanceEvent).where(
            RebalanceEvent.portfolio_id == portfolio_id
        ).order_by(
            RebalanceEvent.created_at.desc(),
            RebalanceEvent.rebalance_id.asc(),
        )
        return list(db.scalars(statement).all())
