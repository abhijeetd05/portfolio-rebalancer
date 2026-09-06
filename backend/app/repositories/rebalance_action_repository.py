from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rebalance_action import RebalanceAction


class RebalanceActionRepository:
    def create(self, db: Session, rebalance_action: RebalanceAction) -> RebalanceAction:
        db.add(rebalance_action)
        db.flush()
        return rebalance_action

    def get_by_id(self, db: Session, action_id: UUID) -> RebalanceAction | None:
        statement = select(RebalanceAction).where(
            RebalanceAction.action_id == action_id
        )
        return db.scalar(statement)

    def get_by_rebalance_id(
        self,
        db: Session,
        rebalance_id: UUID,
    ) -> list[RebalanceAction]:
        statement = select(RebalanceAction).where(
            RebalanceAction.rebalance_id == rebalance_id
        ).order_by(RebalanceAction.action_id.asc())
        return list(db.scalars(statement).all())

    def delete_by_rebalance_id(self, db: Session, rebalance_id: UUID) -> int:
        actions = self.get_by_rebalance_id(db, rebalance_id)
        for action in actions:
            db.delete(action)
        db.flush()
        return len(actions)
