from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import (
    Asset,
    FXRate,
    Holding,
    Portfolio,
    Price,
    TargetAllocation,
    Transaction,
    User,
)


def seed_database() -> None:
    db = SessionLocal()

    try:
        '''
        1.USER
        '''
        user = db.scalar(
            select(User).where(User.user_name == "Abhijeet Demo")
        )

        if user is None:
            user = User(
                user_name="Abhijeet Demo",
                pass_hash="development-only-hash",
                age=21,
                gender="M",
            )
            db.add(user)
            db.flush()

        # ---------------------------------------------------------
        # 2. PORTFOLIO
        # ---------------------------------------------------------
        portfolio = db.scalar(
            select(Portfolio).where(
                Portfolio.user_id == user.user_id,
                Portfolio.portfolio_name == "Demo INR Portfolio",
            )
        )

        if portfolio is None:
            portfolio = Portfolio(
                user_id=user.user_id,
                portfolio_name="Demo INR Portfolio",
                base_currency="INR",
            )
            db.add(portfolio)
            db.flush()

        # ---------------------------------------------------------
        # 3. ASSETS
        # ---------------------------------------------------------
        asset_data = [
            {
                "asset_name": "HDFC Bank",
                "asset_type": "Equity",
                "asset_subtype": "Large Cap",
                "symbol": "HDFCBANK",
                "currency": "INR",
                "data_source": "DEV_SEED",
            },
            {
                "asset_name": "Reliance Industries",
                "asset_type": "Equity",
                "asset_subtype": "Large Cap",
                "symbol": "RELIANCE",
                "currency": "INR",
                "data_source": "DEV_SEED",
            },
            {
                "asset_name": "Infosys",
                "asset_type": "Equity",
                "asset_subtype": "Large Cap",
                "symbol": "INFY",
                "currency": "INR",
                "data_source": "DEV_SEED",
            },
            {
                "asset_name": "SBI Nifty 50 ETF",
                "asset_type": "Equity",
                "asset_subtype": "ETF",
                "symbol": "SETFNIF50",
                "currency": "INR",
                "data_source": "DEV_SEED",
            },
            {
                "asset_name": "HDFC Short Term Debt Fund",
                "asset_type": "Debt",
                "asset_subtype": "Mutual Fund",
                "symbol": "HDFCSHORT",
                "currency": "INR",
                "data_source": "DEV_SEED",
            },
            {
                "asset_name": "Nippon India ETF Gold BeES",
                "asset_type": "Precious Metal",
                "asset_subtype": "Gold ETF",
                "symbol": "GOLDBEES",
                "currency": "INR",
                "data_source": "DEV_SEED",
            },
            {
                "asset_name": "Bitcoin",
                "asset_type": "Crypto",
                "asset_subtype": "Cryptocurrency",
                "symbol": "BTC",
                "currency": "INR",
                "data_source": "DEV_SEED",
            },
        ]

        assets: dict[str, Asset] = {}

        for data in asset_data:
            asset = db.scalar(
                select(Asset).where(Asset.symbol == data["symbol"])
            )

            if asset is None:
                asset = Asset(**data)
                db.add(asset)
                db.flush()

            assets[data["symbol"]] = asset

        # ---------------------------------------------------------
        # 4. DEVELOPMENT PRICES
        # ---------------------------------------------------------
        prices = {
            "HDFCBANK": Decimal("1700.00"),
            "RELIANCE": Decimal("1400.00"),
            "INFY": Decimal("1600.00"),
            "SETFNIF50": Decimal("250.00"),
            "HDFCSHORT": Decimal("30.00"),
            "GOLDBEES": Decimal("65.00"),
            "BTC": Decimal("9000000.00"),
        }

        price_timestamp = datetime(
            2026,
            8,
            31,
            15,
            30,
            tzinfo=timezone.utc,
        )

        for symbol, value in prices.items():
            existing_price = db.scalar(
                select(Price).where(
                    Price.asset_id == assets[symbol].asset_id,
                    Price.price_timestamp == price_timestamp,
                )
            )

            if existing_price is None:
                db.add(
                    Price(
                        asset_id=assets[symbol].asset_id,
                        price=value,
                        currency="INR",
                        price_timestamp=price_timestamp,
                        data_source="DEV_SEED",
                    )
                )

        # ---------------------------------------------------------
        # 5. TARGET ALLOCATIONS
        # ---------------------------------------------------------
        targets = {
            "Equity": Decimal("60.00"),
            "Debt": Decimal("25.00"),
            "Precious Metal": Decimal("10.00"),
            "Crypto": Decimal("5.00"),
        }

        for asset_type, percentage in targets.items():
            existing_target = db.scalar(
                select(TargetAllocation).where(
                    TargetAllocation.portfolio_id == portfolio.portfolio_id,
                    TargetAllocation.asset_type == asset_type,
                )
            )

            if existing_target is None:
                db.add(
                    TargetAllocation(
                        portfolio_id=portfolio.portfolio_id,
                        asset_type=asset_type,
                        target_percentage=percentage,
                    )
                )

        # ---------------------------------------------------------
        # 6. HOLDINGS
        #
        # Values are intentionally chosen to create allocation drift.
        # ---------------------------------------------------------
        holdings = {
            "HDFCBANK": Decimal("160"),
            "RELIANCE": Decimal("150"),
            "INFY": Decimal("125"),
            "SETFNIF50": Decimal("400"),
            "HDFCSHORT": Decimal("1000"),
            "GOLDBEES": Decimal("769.23076923"),
            "BTC": Decimal("0.0388888889"),
        }

        purchase_date = datetime(
            2026,
            1,
            15,
            tzinfo=timezone.utc,
        ).date()

        for symbol, units in holdings.items():
            existing_holding = db.scalar(
                select(Holding).where(
                    Holding.portfolio_id == portfolio.portfolio_id,
                    Holding.asset_id == assets[symbol].asset_id,
                )
            )

            if existing_holding is None:
                db.add(
                    Holding(
                        portfolio_id=portfolio.portfolio_id,
                        asset_id=assets[symbol].asset_id,
                        units=units,
                        avg_buy_price=prices[symbol],
                        purchase_date=purchase_date,
                    )
                )

        # ---------------------------------------------------------
        # 7. TRANSACTIONS
        # ---------------------------------------------------------
        transaction_date = datetime(
            2026,
            1,
            15,
            10,
            0,
            tzinfo=timezone.utc,
        )

        for symbol, units in holdings.items():
            existing_transaction = db.scalar(
                select(Transaction).where(
                    Transaction.portfolio_id == portfolio.portfolio_id,
                    Transaction.asset_id == assets[symbol].asset_id,
                    Transaction.transaction_date == transaction_date,
                )
            )

            if existing_transaction is None:
                db.add(
                    Transaction(
                        portfolio_id=portfolio.portfolio_id,
                        asset_id=assets[symbol].asset_id,
                        transaction_type="BUY",
                        units=units,
                        price=prices[symbol],
                        transaction_date=transaction_date,
                        fees=Decimal("0.00"),
                        notes="Development seed transaction",
                    )
                )

        # ---------------------------------------------------------
        # 8. FX RATE
        # ---------------------------------------------------------
        existing_fx = db.scalar(
            select(FXRate).where(
                FXRate.from_currency == "USD",
                FXRate.to_currency == "INR",
                FXRate.rate_timestamp == price_timestamp,
            )
        )

        if existing_fx is None:
            db.add(
                FXRate(
                    from_currency="USD",
                    to_currency="INR",
                    exchange_rate=Decimal("83.00"),
                    rate_timestamp=price_timestamp,
                    data_source="DEV_SEED",
                )
            )

        db.commit()

        print("Development database seeded successfully.")
        print(f"User: {user.user_name}")
        print(f"Portfolio: {portfolio.portfolio_name}")
        print(f"Portfolio ID: {portfolio.portfolio_id}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()