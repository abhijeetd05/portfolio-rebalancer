from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction


class TransactionRepository:
    def create(self, db: Session, transaction: Transaction) -> Transaction:
        db.add(transaction)
        db.flush()
        return transaction

    def get_by_id(self, db: Session, transaction_id: UUID) -> Transaction | None:
        statement = select(Transaction).where(Transaction.transaction_id == transaction_id)
        return db.scalar(statement)

    def get_by_portfolio_id(self, db: Session, portfolio_id: UUID) -> list[Transaction]:
        statement = (
            select(Transaction)
            .where(Transaction.portfolio_id == portfolio_id)
            .order_by(Transaction.transaction_date.asc())
        )
        return list(db.scalars(statement).all())

    def get_by_portfolio_and_asset(
        self,
        db: Session,
        portfolio_id: UUID,
        asset_id: UUID,
    ) -> list[Transaction]:
        statement = (
            select(Transaction)
            .where(
                Transaction.portfolio_id == portfolio_id,
                Transaction.asset_id == asset_id,
            )
            .order_by(Transaction.transaction_date.asc())
        )
        return list(db.scalars(statement).all())

    def update(
        self,
        db: Session,
        transaction_id: UUID,
        update_data: dict[str, Any],
    ) -> Transaction | None:
        transaction = self.get_by_id(db, transaction_id)
        if transaction is None:
            return None

        allowed_fields = {
            "transaction_type",
            "units",
            "price",
            "transaction_date",
            "fees",
            "notes",
        }
        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(transaction, field, value)

        db.flush()
        return transaction

    def delete(self, db: Session, transaction_id: UUID) -> bool:
        transaction = self.get_by_id(db, transaction_id)
        if transaction is None:
            return False

        db.delete(transaction)
        db.flush()
        return True
