from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.admin_assets import router as admin_assets_router
from app.api.assets import router as assets_router

from app.api.dashboard import router as dashboard_router
from app.api.holdings import router as holding_router
from app.api.market_data import router as market_data_router
from app.api.portfolios import router as portfolio_router
from app.api.rebalance import router as rebalance_router
from app.api.target_allocations import router as target_allocation_router
from app.api.transactions import router as transaction_router
from app.api.valuation import router as valuation_router
from app.api.users import router as users_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(auth_router)
app.include_router(admin_assets_router)
app.include_router(assets_router)
app.include_router(portfolio_router)
app.include_router(holding_router)
app.include_router(target_allocation_router)
app.include_router(rebalance_router)
app.include_router(dashboard_router)
app.include_router(transaction_router)
app.include_router(valuation_router)
app.include_router(users_router)
app.include_router(market_data_router)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "portfolio-rebalancer",
    }