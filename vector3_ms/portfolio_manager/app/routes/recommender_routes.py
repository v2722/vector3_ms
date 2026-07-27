from fastapi import APIRouter
from app.services.recommender_service import (
    content_based_recommendations, diversification_recommendations, collaborative_filtering
)

router = APIRouter(prefix="/recommend", tags=["Recommendations"])

@router.get("/content/{ticker}")
def get_content_recommendations(ticker: str, limit: int = 5):
    return content_based_recommendations(ticker, limit)

@router.get("/diversify/{portfolio_id}")
def get_diversification_recommendations(portfolio_id: int, limit: int = 5):
    return diversification_recommendations(portfolio_id, limit)

@router.get("/collaborative/{user_id}")
def get_collaborative_recommendations(user_id: int, limit: int = 5):
    return collaborative_filtering(user_id, limit)
