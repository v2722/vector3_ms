from fastapi import APIRouter
from app.services.optimization_service import (
    efficient_frontier, optimal_allocation, risk_parity, monte_carlo_simulation
)

router = APIRouter(prefix="/optimize", tags=["Portfolio Optimization"])

@router.get("/frontier/{portfolio_id}")
def get_efficient_frontier(portfolio_id: int, num_portfolios: int = 10000):
    return efficient_frontier(portfolio_id, num_portfolios)

@router.get("/optimal/{portfolio_id}")
def get_optimal_allocation(portfolio_id: int):
    return optimal_allocation(portfolio_id)

@router.get("/risk-parity/{portfolio_id}")
def get_risk_parity(portfolio_id: int):
    return risk_parity(portfolio_id)

@router.get("/monte-carlo/{portfolio_id}")
def get_monte_carlo(portfolio_id: int, days: int = 252, num_simulations: int = 1000):
    return monte_carlo_simulation(portfolio_id, days, num_simulations)
