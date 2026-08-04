from fastapi import APIRouter
from app.services.recommender_service import (
    content_based_recommendations,
    collaborative_filtering,
    hybrid_recommendations,
    correlation_diversification,
    diversification_recommendations,
    trending_recommendations,
    portfolio_gap_completion,
    similar_portfolios,
)

router = APIRouter(prefix="/recommend", tags=["Recommendations"])


@router.get("/content/{ticker}")
def get_content_recommendations(ticker: str, limit: int = 5):
    return content_based_recommendations(ticker, limit)


@router.get("/diversify/{portfolio_id}")
def get_diversification_recommendations(portfolio_id: int, limit: int = 5):
    return diversification_recommendations(portfolio_id, limit)


@router.get("/correlation/{portfolio_id}")
def get_correlation_recommendations(portfolio_id: int, limit: int = 5):
    return correlation_diversification(portfolio_id, limit)


@router.get("/collaborative/{portfolio_id}")
def get_collaborative_recommendations(portfolio_id: int, limit: int = 5):
    return collaborative_filtering(portfolio_id, limit)


@router.get("/hybrid/{portfolio_id}")
def get_hybrid_recommendations(portfolio_id: int, limit: int = 5, content_weight: float = 0.5):
    return hybrid_recommendations(portfolio_id, limit, content_weight)


@router.get("/trending")
def get_trending_recommendations(limit: int = 5):
    return trending_recommendations(limit)


@router.get("/gaps/{portfolio_id}")
def get_portfolio_gaps(portfolio_id: int, limit: int = 5):
    return portfolio_gap_completion(portfolio_id, limit)


@router.get("/similar-portfolios/{portfolio_id}")
def get_similar_portfolios(portfolio_id: int, limit: int = 5):
    return similar_portfolios(portfolio_id, limit)
