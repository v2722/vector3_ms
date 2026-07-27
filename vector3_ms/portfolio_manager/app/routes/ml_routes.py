from fastapi import APIRouter
from app.services.ml_service import predict_price_linear, asset_classification, portfolio_health_score

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

@router.get("/predict/{ticker}")
def predict_price(ticker: str, days: int = 7):
    return predict_price_linear(ticker, days)

@router.get("/classify/{ticker}")
def classify_asset(ticker: str):
    return asset_classification(ticker)

@router.get("/health/{portfolio_id}")
def portfolio_health(portfolio_id: int):
    return portfolio_health_score(portfolio_id)
