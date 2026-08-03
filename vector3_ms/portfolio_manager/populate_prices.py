#!/usr/bin/env python3
"""
Populate price history for testing LSTM.

Usage:
    python populate_prices.py              # Default: AAPL, MSFT, TSLA
    python populate_prices.py AAPL MSFT    # Specific tickers
"""

import sys
from app.services.price_service import import_price_history

def main():
    # Default tickers if none specified
    if len(sys.argv) > 1:
        tickers = sys.argv[1:]
    else:
        tickers = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN"]

    print("\n" + "=" * 60)
    print("PRICE HISTORY IMPORTER")
    print("=" * 60 + "\n")

    for ticker in tickers:
        print(f"Fetching price history for {ticker}...", end=" ", flush=True)
        try:
            result = import_price_history(ticker, period="2y", interval="1d")
            print("✅ Complete")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    print("\n" + "=" * 60)
    print("✅ Price history imported successfully!")
    print("\nNow test with:")
    print("  curl \"http://localhost:8000/ml/predict/lstm/AAPL?days=7\"")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
