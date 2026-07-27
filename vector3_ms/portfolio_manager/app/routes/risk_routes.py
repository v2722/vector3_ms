from fastapi import APIRouter
from app.services.risk_service import (
    calculate_volatility, calculate_sharpe_ratio, calculate_var,
    calculate_max_drawdown, correlation_matrix
)

router = APIRouter(prefix="/risk", tags=["Risk Analytics"])

@router.get("/volatility/{ticker}")
def get_volatility(ticker: str, days: int = 252):
    vol = calculate_volatility(ticker, days)
    return {"ticker": ticker, "volatility": vol, "days": days}

@router.get("/sharpe/{portfolio_id}")
def get_sharpe(portfolio_id: int, risk_free_rate: float = 0.03):
    return calculate_sharpe_ratio(portfolio_id, risk_free_rate)

@router.get("/var/{portfolio_id}")
def get_var(portfolio_id: int, confidence: float = 0.95):
    return calculate_var(portfolio_id, confidence)

@router.get("/max-drawdown/{portfolio_id}")
def get_max_drawdown(portfolio_id: int):
    return calculate_max_drawdown(portfolio_id)

@router.get("/correlation/{portfolio_id}")
def get_correlation(portfolio_id: int):
    return correlation_matrix(portfolio_id)
