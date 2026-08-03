# This module re-exports the enhanced ML service for backward compatibility
# All implementations have been moved to ml_service_enhanced.py

from app.services.ml_service_enhanced import (
    get_historical_prices,
    predict_price_lstm,
    predict_price_prophet,
    predict_price_linear,
    predict_price_ensemble,
    asset_classification,
    portfolio_health_score
)

__all__ = [
    "get_historical_prices",
    "predict_price_lstm",
    "predict_price_prophet",
    "predict_price_linear",
    "predict_price_ensemble",
    "asset_classification",
    "portfolio_health_score"
]
