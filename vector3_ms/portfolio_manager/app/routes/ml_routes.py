from fastapi import APIRouter
from app.services.ml_service_enhanced import (
    predict_price_lstm,
    predict_price_prophet,
    predict_price_linear,
    predict_price_ensemble,
    asset_classification,
    portfolio_health_score
)

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

@router.get("/predict/{ticker}")
def predict_price(ticker: str, days: int = 7, method: str = "lstm"):
    """
    Predict stock price using selected method.

    Methods:
    - lstm: LSTM neural network (best accuracy, uses 2 years of data)
    - prophet: Prophet seasonal model (good for trends)
    - linear: Linear regression baseline (simple, fast)
    - ensemble: Average of all 3 methods (most robust)

    Returns:
    - predicted_price: Forecasted price for each day
    - upper_bound: 95% confidence interval upper bound
    - lower_bound: 95% confidence interval lower bound
    - confidence_level: 95%
    """
    if method == "lstm":
        return predict_price_lstm(ticker, days)
    elif method == "prophet":
        return predict_price_prophet(ticker, days)
    elif method == "linear":
        return predict_price_linear(ticker, days)
    elif method == "ensemble":
        return predict_price_ensemble(ticker, days)
    else:
        return {"error": f"Unknown method: {method}. Choose from: lstm, prophet, linear, ensemble"}

@router.get("/predict/lstm/{ticker}")
def predict_lstm(ticker: str, days: int = 7):
    """LSTM Neural Network prediction (most advanced)"""
    return predict_price_lstm(ticker, days)

@router.get("/predict/prophet/{ticker}")
def predict_prophet(ticker: str, days: int = 7):
    """Prophet seasonal forecasting model"""
    return predict_price_prophet(ticker, days)

@router.get("/predict/linear/{ticker}")
def predict_linear(ticker: str, days: int = 7):
    """Linear Regression baseline model"""
    return predict_price_linear(ticker, days)

@router.get("/predict/ensemble/{ticker}")
def predict_ensemble(ticker: str, days: int = 7):
    """Ensemble prediction (average of all models)"""
    return predict_price_ensemble(ticker, days)

@router.get("/classify/{ticker}")
def classify_asset(ticker: str):
    """Classify asset by risk profile and income characteristics"""
    return asset_classification(ticker)

@router.get("/health/{portfolio_id}")
def portfolio_health(portfolio_id: int):
    """Calculate portfolio health score (diversification + volatility)"""
    return portfolio_health_score(portfolio_id)
