from fastapi import FastAPI
from app.routes import (
    asset_type_routes,
    asset_transaction_routes,
    performance_routes,
    scalar_ui
)
from vector3_ms.portfolio_manager.app.routes import asset_routes, portfolio_routes, price_routes, transaction_routes

app = FastAPI(
    title="Portfolio Manager API",
    description="REST API for managing financial portfolios using MySQL + yfinance",
    version="1.0.0"
)

# Register routes
app.include_router(portfolio_routes.router)
app.include_router(asset_routes.router)
app.include_router(price_routes.router)
app.include_router(transaction_routes.router)
app.include_router(asset_type_routes.router)
app.include_router(asset_transaction_routes.router)
app.include_router(performance_routes.router)
app.include_router(scalar_ui.router)

@app.get("/")
def root():
    return {"message": "Portfolio Manager API is running"}
