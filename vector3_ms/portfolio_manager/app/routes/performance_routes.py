from fastapi import APIRouter
from app.services.performance_service import list_performance, add_performance

router = APIRouter(prefix="/performance", tags=["Portfolio Performance"])

@router.get("/{portfolio_id}")
def get_performance(portfolio_id: int):
    return list_performance(portfolio_id)

@router.post("/{portfolio_id}")
def add_perf(portfolio_id: int, data: dict):
    return add_performance(portfolio_id, data)
