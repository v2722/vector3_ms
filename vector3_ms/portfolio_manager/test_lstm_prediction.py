#!/usr/bin/env python3
"""
Test script for LSTM price prediction functionality.

Usage:
    python test_lstm_prediction.py

    Or test specific ticker:
    python test_lstm_prediction.py --ticker AAPL --days 14
"""

import sys
import argparse
import json
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database.connection import get_db
from app.services.ml_service_enhanced import (
    predict_price_lstm,
    predict_price_prophet,
    predict_price_linear,
    predict_price_ensemble,
    asset_classification,
    portfolio_health_score
)


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_prediction(result, method_name):
    """Pretty print prediction results"""
    if "error" in result:
        print(f"❌ {method_name} FAILED: {result['error']}")
        return

    print(f"✅ {method_name} SUCCESS")
    print(f"   Ticker: {result['ticker']}")
    print(f"   Current Price: ${result['current_price']:.2f}")
    print(f"   Method: {result['method']}")

    if "model_info" in result:
        print(f"\n   Model Info:")
        for key, value in result["model_info"].items():
            if isinstance(value, float):
                print(f"   - {key}: {value:.6f}")
            else:
                print(f"   - {key}: {value}")

    print(f"\n   Predictions:")
    for pred in result["predictions"]:
        print(f"   Day {pred['day']}:")
        print(f"      Point Estimate: ${pred['predicted_price']:.2f}")
        print(f"      95% Range: ${pred['lower_bound']:.2f} - ${pred['upper_bound']:.2f}")
        print(f"      Confidence: {pred['confidence_level']}")


def compare_methods(ticker: str, days: int = 7):
    """Compare all prediction methods for a ticker"""
    print_section(f"COMPARING ALL METHODS FOR {ticker}")

    # Test LSTM
    print("Running LSTM prediction...")
    lstm_result = predict_price_lstm(ticker, days)
    print_prediction(lstm_result, "LSTM Neural Network")

    # Test Prophet
    print("\nRunning Prophet prediction...")
    prophet_result = predict_price_prophet(ticker, days)
    print_prediction(prophet_result, "Prophet Seasonal Forecasting")

    # Test Linear
    print("\nRunning Linear Regression prediction...")
    linear_result = predict_price_linear(ticker, days)
    print_prediction(linear_result, "Linear Regression")

    # Test Ensemble
    print("\nRunning Ensemble prediction...")
    ensemble_result = predict_price_ensemble(ticker, days)
    print_prediction(ensemble_result, "Ensemble (Average of All 3)")

    # Comparison table
    valid_results = [r for r in [lstm_result, prophet_result, linear_result, ensemble_result] if r.get("predictions")]
    if valid_results:
        print_section("PREDICTION COMPARISON")
        print(f"{'Day':<5} {'LSTM':<12} {'Prophet':<12} {'Linear':<12} {'Ensemble':<12}")
        print("-" * 53)

        num_days = min(len(r.get("predictions", [])) for r in valid_results)
        for day_idx in range(num_days):
            day = day_idx + 1
            lstm_price = lstm_result.get("predictions", [{}])[day_idx].get("predicted_price", 0) if "predictions" in lstm_result else 0
            prophet_price = prophet_result.get("predictions", [{}])[day_idx].get("predicted_price", 0) if "predictions" in prophet_result else 0
            linear_price = linear_result.get("predictions", [{}])[day_idx].get("predicted_price", 0) if "predictions" in linear_result else 0
            ensemble_price = ensemble_result.get("predictions", [{}])[day_idx].get("predicted_price", 0) if "predictions" in ensemble_result else 0

            if any([lstm_price, prophet_price, linear_price, ensemble_price]):
                print(
                    f"{day:<5} ${lstm_price:<11.2f} ${prophet_price:<11.2f} ${linear_price:<11.2f} ${ensemble_price:<11.2f}"
                )


def test_asset_classification(ticker: str):
    """Test asset classification"""
    print_section(f"ASSET CLASSIFICATION FOR {ticker}")

    result = asset_classification(ticker)

    if "error" in result:
        print(f"❌ Classification failed: {result['error']}")
    else:
        print(f"✅ Classification successful")
        print(f"   Ticker: {result['ticker']}")
        print(f"   Risk Class: {result['risk_class']} (volatility: {result['volatility']:.2%})")
        print(f"   Income Class: {result['income_class']} (dividend yield: {result['dividend_yield']:.2%})")


def test_portfolio_health(portfolio_id: int = 1):
    """Test portfolio health score"""
    print_section(f"PORTFOLIO HEALTH SCORE (Portfolio ID: {portfolio_id})")

    result = portfolio_health_score(portfolio_id)

    if "error" in result:
        print(f"❌ Health score calculation failed: {result['error']}")
    else:
        print(f"✅ Health score calculated")
        print(f"   Overall Health Score: {result['overall_health_score']:.1f}/100")
        print(f"   Diversification Score: {result['diversification_score']:.1f}/100")
        print(f"   Volatility Score: {result['volatility_score']:.1f}/100")
        print(f"   Number of Sectors: {result['sectors']}")
        print(f"   Average Volatility: {result['avg_volatility']:.2%}")


def list_available_tickers():
    """List available tickers in the database"""
    print_section("AVAILABLE TICKERS IN DATABASE")

    db = get_db()
    cursor = db.cursor(dictionary=True)
    sql = """
    SELECT DISTINCT ticker, name
    FROM asset
    ORDER BY ticker ASC
    """
    cursor.execute(sql)
    tickers = cursor.fetchall()
    cursor.close()
    db.close()

    if not tickers:
        print("❌ No tickers found in database")
        print("   Please add some assets first using the API or database")
        return []

    print(f"✅ Found {len(tickers)} tickers:\n")
    for ticker in tickers:
        print(f"   {ticker['ticker']:<10} - {ticker['name']}")

    return [t["ticker"] for t in tickers]


def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description="Test LSTM price prediction functionality")
    parser.add_argument("--ticker", type=str, help="Ticker symbol to test (e.g., AAPL)")
    parser.add_argument("--days", type=int, default=7, help="Number of days to forecast (default: 7)")
    parser.add_argument("--list", action="store_true", help="List available tickers and exit")
    parser.add_argument("--portfolio", type=int, default=1, help="Portfolio ID for health check (default: 1)")

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("  LSTM PRICE PREDICTION TEST SUITE")
    print("=" * 70)

    # List available tickers
    available_tickers = list_available_tickers()

    if args.list:
        return

    # Test specific ticker or use first available
    if args.ticker:
        ticker = args.ticker.upper()
        if ticker not in [t.upper() for t in available_tickers]:
            print(f"\n⚠️  Warning: {ticker} not found in database")
            print("   It will still be tested, but may fail if no price history exists")
    else:
        if not available_tickers:
            print("\n❌ No tickers available to test")
            print("   Add some assets using the API first")
            return

        ticker = available_tickers[0]
        print(f"\n💡 No ticker specified, using: {ticker}")

    # Run tests
    compare_methods(ticker, args.days)
    test_asset_classification(ticker)
    test_portfolio_health(args.portfolio)

    # Summary
    print_section("TEST SUMMARY")
    print(f"✅ All tests completed for ticker: {ticker}")
    print(f"✅ Next steps:")
    print(f"   1. Review prediction confidence intervals")
    print(f"   2. Compare predictions across methods")
    print(f"   3. Check model quality metrics (MAE, MSE)")
    print(f"   4. Use ensemble for important trading decisions")
    print(f"\n📚 For more info, see: ML_ENHANCEMENTS.md")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
