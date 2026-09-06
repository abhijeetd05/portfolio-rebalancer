from sqlalchemy.exc import IntegrityError

from app.core.database import SessionLocal
from app.models import Portfolio, Holding, TargetAllocation


def test_duplicate_holding():
    db = SessionLocal()

    try:
        portfolio = db.query(Portfolio).first()

        holding = (
            db.query(Holding)
            .filter_by(portfolio_id=portfolio.portfolio_id)
            .first()
        )

        duplicate = Holding(
            portfolio_id=holding.portfolio_id,
            asset_id=holding.asset_id,
            units=1,
            avg_buy_price=1,
        )

        db.add(duplicate)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            print("DUPLICATE HOLDING CONSTRAINT: PASS")
            return

        print("DUPLICATE HOLDING CONSTRAINT: FAIL")

    finally:
        db.close()


def test_duplicate_target_allocation():
    db = SessionLocal()

    try:
        portfolio = db.query(Portfolio).first()

        target = (
            db.query(TargetAllocation)
            .filter_by(portfolio_id=portfolio.portfolio_id)
            .first()
        )

        duplicate = TargetAllocation(
            portfolio_id=target.portfolio_id,
            asset_type=target.asset_type,
            target_percentage=1,
        )

        db.add(duplicate)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            print("DUPLICATE TARGET CONSTRAINT: PASS")
            return

        print("DUPLICATE TARGET CONSTRAINT: FAIL")

    finally:
        db.close()


if __name__ == "__main__":
    test_duplicate_holding()
    test_duplicate_target_allocation()