from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import (
    asset_type_routes,
    asset_transaction_routes,
    performance_routes,
    scalar_ui,
    asset_routes,
    portfolio_routes,
    user_routes,
    price_routes,
    transaction_routes,
    auth_routes,
    csv_routes,
    ml_routes,
    recommender_routes,
    risk_routes,
    optimization_routes,
    realtime_routes,
    chat_routes
)

app = FastAPI(
    title="Portfolio Manager API",
    description="REST API for managing financial portfolios using MySQL + yfinance",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth_routes.router)
app.include_router(portfolio_routes.router)
app.include_router(user_routes.router)
app.include_router(asset_routes.router)
app.include_router(price_routes.router)
app.include_router(transaction_routes.router)
app.include_router(asset_type_routes.router)
app.include_router(asset_transaction_routes.router)
app.include_router(performance_routes.router)
app.include_router(csv_routes.router)
app.include_router(ml_routes.router)
app.include_router(recommender_routes.router)
app.include_router(risk_routes.router)
app.include_router(optimization_routes.router)
app.include_router(realtime_routes.router)
app.include_router(chat_routes.router)
app.include_router(scalar_ui.router)

@app.get("/")
def root():
    return {"message": "Portfolio Manager API is running"}
