#!/usr/bin/env python3
"""
End-to-End Test Suite for Portfolio Manager API
Tests all major endpoints and features mentioned in README
"""

import requests
import json
import time
from typing import Any, Dict, Optional

API_BASE = "http://localhost:8000"
TEST_RESULTS = []

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text: str):
    print(f"\n{BLUE}{BOLD}{'='*60}{RESET}")
    print(f"{BLUE}{BOLD}{text}{RESET}")
    print(f"{BLUE}{BOLD}{'='*60}{RESET}\n")


def print_test(name: str, success: bool, details: str = ""):
    status = f"{GREEN}✓ PASS{RESET}" if success else f"{RED}✗ FAIL{RESET}"
    print(f"{status} | {name}")
    if details:
        print(f"  → {details}")
    TEST_RESULTS.append({"test": name, "success": success, "details": details})


def check_endpoint(method: str, endpoint: str, data: Optional[Dict] = None,
                   expect_status: int = 200, name: str = "", timeout: int = 10) -> Dict[str, Any]:
    """Generic endpoint tester"""
    url = f"{API_BASE}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=timeout)
        else:
            raise ValueError(f"Unsupported method: {method}")

        success = response.status_code == expect_status
        details = f"Status {response.status_code} (expected {expect_status})"

        if response.text:
            try:
                response_json = response.json()
                details += f" | Response keys: {list(response_json.keys())[:3]}"
            except:
                details += f" | Response length: {len(response.text)}"

        print_test(name or f"{method} {endpoint}", success, details)
        return {"success": success, "data": response.json() if response.text else {}, "status": response.status_code}

    except requests.exceptions.ConnectionError:
        print_test(name or f"{method} {endpoint}", False, "Connection failed - API not running")
        return {"success": False, "data": {}, "status": 0}
    except Exception as e:
        print_test(name or f"{method} {endpoint}", False, str(e))
        return {"success": False, "data": {}, "status": 0}


def test_health():
    """Test API health/root endpoint"""
    print_header("Health & API Status")
    check_endpoint("GET", "/", expect_status=200, name="API Root Endpoint")


def test_auth():
    """Test authentication endpoints"""
    print_header("Authentication (Auth Routes)")

    # Register test user
    register_data = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "TestPassword123"
    }
    result = check_endpoint("POST", "/auth/register", register_data, expect_status=200, name="Register User")

    # Login
    if result["success"]:
        login_data = {
            "username": register_data["username"],
            "password": register_data["password"]
        }
        login_result = check_endpoint("POST", "/auth/login", login_data, expect_status=200, name="Login User")

    # Get current user
    check_endpoint("GET", "/auth/me", expect_status=200, name="Get Current User")


def test_portfolios(test_portfolio_id: Optional[int] = None):
    """Test portfolio endpoints"""
    print_header("Portfolios (Portfolio Routes)")

    # List portfolios
    list_result = check_endpoint("GET", "/portfolios/", expect_status=200, name="List Portfolios")

    portfolios = list_result.get("data", [])
    if isinstance(portfolios, list) and len(portfolios) > 0:
        portfolio_id = portfolios[0].get("id") or test_portfolio_id
    else:
        portfolio_id = test_portfolio_id

    # Create portfolio
    portfolio_data = {
        "name": f"Test Portfolio {int(time.time())}",
        "description": "E2E Test Portfolio"
    }
    create_result = check_endpoint("POST", "/portfolios/", portfolio_data, expect_status=200, name="Create Portfolio")

    return portfolio_id or (create_result.get("data", {}).get("id") if create_result["success"] else None)


def test_assets():
    """Test asset endpoints"""
    print_header("Assets (Asset Routes)")

    # List all assets
    check_endpoint("GET", "/assets/", expect_status=200, name="List Assets")

    # Get specific asset
    check_endpoint("GET", "/assets/AAPL", expect_status=200, name="Get Asset by Ticker (AAPL)")

    # Upsert asset
    asset_data = {
        "name": "Apple Inc",
        "sector": "Technology",
        "industry": "Computers"
    }
    check_endpoint("POST", "/assets/AAPL", asset_data, expect_status=200, name="Upsert Asset")


def test_prices():
    """Test price endpoints"""
    print_header("Prices (Price Routes)")

    # Get price history
    check_endpoint("GET", "/prices/AAPL", expect_status=200, name="Get Price History (AAPL)")

    # Fetch/update prices (fetching from Yahoo Finance can be slow)
    price_data = {
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    }
    check_endpoint("POST", "/prices/AAPL", price_data, expect_status=200, name="Fetch Price History", timeout=30)


def test_transactions(portfolio_id: int):
    """Test transaction endpoints"""
    print_header("Transactions (Transaction Routes)")

    # List transactions
    check_endpoint("GET", f"/transactions/{portfolio_id}", expect_status=200, name="List Transactions")

    # Create transaction
    transaction_data = {
        "asset_id": 1,
        "transaction_type": "BUY",
        "quantity": 10,
        "price_per_unit": 150.0,
        "transaction_date": "2024-01-01"
    }
    check_endpoint("POST", f"/transactions/{portfolio_id}", transaction_data, expect_status=200, name="Create Transaction")


def test_asset_types():
    """Test asset type endpoints"""
    print_header("Asset Types (Asset Type Routes)")

    # List asset types
    check_endpoint("GET", "/asset-types/", expect_status=200, name="List Asset Types")

    # Create asset type
    asset_type_data = {
        "name": "Tech Stock",
        "description": "Technology sector stocks"
    }
    check_endpoint("POST", "/asset-types/", asset_type_data, expect_status=200, name="Create Asset Type")


def test_performance(portfolio_id: int):
    """Test portfolio performance endpoints"""
    print_header("Performance (Performance Routes)")

    # Get performance
    check_endpoint("GET", f"/performance/{portfolio_id}", expect_status=200, name="Get Portfolio Performance")

    # Calculate/update performance
    perf_data = {
        "performance_date": "2024-01-31",
        "total_value": 15000.0,
        "daily_change": 500.0
    }
    check_endpoint("POST", f"/performance/{portfolio_id}", perf_data, expect_status=200, name="Update Portfolio Performance")


def test_ml_predictions():
    """Test Machine Learning prediction endpoints"""
    print_header("Machine Learning (ML Routes)")

    # LSTM prediction (long timeout - neural network is slow)
    check_endpoint("GET", "/ml/predict/AAPL?days=7&method=lstm", expect_status=200, name="LSTM Price Prediction", timeout=30)

    # Prophet prediction
    check_endpoint("GET", "/ml/predict/AAPL?days=7&method=prophet", expect_status=200, name="Prophet Price Prediction", timeout=15)

    # Linear prediction
    check_endpoint("GET", "/ml/predict/AAPL?days=7&method=linear", expect_status=200, name="Linear Regression Prediction")

    # Ensemble prediction (long timeout - runs all models)
    check_endpoint("GET", "/ml/predict/AAPL?days=7&method=ensemble", expect_status=200, name="Ensemble Prediction", timeout=30)

    # Asset classification
    check_endpoint("GET", "/ml/classify/AAPL", expect_status=200, name="Asset Classification")

    # Portfolio health score
    check_endpoint("GET", "/ml/health/1", expect_status=200, name="Portfolio Health Score")


def test_recommendations(portfolio_id: int):
    """Test recommendation endpoints"""
    print_header("Recommendations (Recommender Routes)")

    # Content-based recommendations
    check_endpoint("GET", "/recommend/content/AAPL?limit=5", expect_status=200, name="Content-Based Recommendations")

    # Collaborative filtering
    check_endpoint("GET", f"/recommend/collaborative/{portfolio_id}?limit=5", expect_status=200, name="Collaborative Filtering")

    # Hybrid recommendations
    check_endpoint("GET", f"/recommend/hybrid/{portfolio_id}?limit=5", expect_status=200, name="Hybrid Recommendations")

    # Correlation/diversification
    check_endpoint("GET", f"/recommend/correlation/{portfolio_id}?limit=5", expect_status=200, name="Correlation-Based Diversification")

    # Trending recommendations
    check_endpoint("GET", "/recommend/trending?limit=5", expect_status=200, name="Trending Assets")

    # Portfolio gaps
    check_endpoint("GET", f"/recommend/gaps/{portfolio_id}?limit=5", expect_status=200, name="Portfolio Gap Completion")

    # Similar portfolios
    check_endpoint("GET", f"/recommend/similar-portfolios/{portfolio_id}?limit=5", expect_status=200, name="Similar Portfolios")


def test_risk_analytics(portfolio_id: int):
    """Test risk analytics endpoints"""
    print_header("Risk Analytics (Risk Routes)")

    # Volatility
    check_endpoint("GET", "/risk/volatility/AAPL?days=252", expect_status=200, name="Asset Volatility")

    # Sharpe ratio
    check_endpoint("GET", f"/risk/sharpe/{portfolio_id}?risk_free_rate=0.03", expect_status=200, name="Sharpe Ratio")

    # Value at Risk
    check_endpoint("GET", f"/risk/var/{portfolio_id}?confidence=0.95", expect_status=200, name="Value at Risk (VaR)")

    # Maximum drawdown
    check_endpoint("GET", f"/risk/max-drawdown/{portfolio_id}", expect_status=200, name="Maximum Drawdown")

    # Correlation matrix
    check_endpoint("GET", f"/risk/correlation/{portfolio_id}", expect_status=200, name="Correlation Matrix")


def test_optimization(portfolio_id: int):
    """Test portfolio optimization endpoints"""
    print_header("Portfolio Optimization (Optimization Routes)")

    # Efficient frontier
    check_endpoint("GET", f"/optimize/frontier/{portfolio_id}?num_portfolios=1000", expect_status=200, name="Efficient Frontier")

    # Optimal allocation
    check_endpoint("GET", f"/optimize/optimal/{portfolio_id}", expect_status=200, name="Optimal Allocation (Max Sharpe)")

    # Risk parity
    check_endpoint("GET", f"/optimize/risk-parity/{portfolio_id}", expect_status=200, name="Risk Parity Allocation")

    # Monte Carlo simulation
    check_endpoint("GET", f"/optimize/monte-carlo/{portfolio_id}?days=252&num_simulations=1000", expect_status=200, name="Monte Carlo Simulation")


def test_csv_operations(portfolio_id: int = 1):
    """Test CSV import/export endpoints"""
    print_header("CSV Import/Export (CSV Routes)")

    # Export holdings
    check_endpoint("GET", f"/csv/export/holdings/{portfolio_id}", expect_status=200, name="Export Holdings CSV")

    # Export transactions
    check_endpoint("GET", f"/csv/export/transactions/{portfolio_id}", expect_status=200, name="Export Transactions CSV")

    # Export performance
    check_endpoint("GET", f"/csv/export/performance/{portfolio_id}", expect_status=200, name="Export Performance CSV")


def print_summary():
    """Print test summary"""
    print_header("Test Summary")

    passed = sum(1 for r in TEST_RESULTS if r["success"])
    failed = sum(1 for r in TEST_RESULTS if not r["success"])
    total = len(TEST_RESULTS)

    print(f"\n{BOLD}Results:{RESET}")
    print(f"  {GREEN}Passed: {passed}{RESET}")
    print(f"  {RED}Failed: {failed}{RESET}")
    print(f"  {BOLD}Total: {total}{RESET}\n")

    if failed > 0:
        print(f"{YELLOW}Failed Tests:{RESET}")
        for result in TEST_RESULTS:
            if not result["success"]:
                print(f"  - {result['test']}")
                if result["details"]:
                    print(f"    Details: {result['details']}")

    success_rate = (passed / total * 100) if total > 0 else 0
    status_color = GREEN if success_rate >= 80 else YELLOW if success_rate >= 50 else RED
    print(f"\n{status_color}{BOLD}Success Rate: {success_rate:.1f}%{RESET}\n")

    return passed == total


def main():
    """Run all tests"""
    print(f"\n{BOLD}{BLUE}Portfolio Manager E2E Test Suite{RESET}")
    print(f"Target: {API_BASE}\n")

    # Run tests in order
    test_health()
    test_auth()
    portfolio_id = test_portfolios()
    test_assets()
    test_prices()

    if portfolio_id:
        test_transactions(portfolio_id)
        test_performance(portfolio_id)
        test_recommendations(portfolio_id)
        test_risk_analytics(portfolio_id)
        test_optimization(portfolio_id)

    test_asset_types()
    test_ml_predictions()
    if portfolio_id:
        test_csv_operations(portfolio_id)

    # Print summary
    all_passed = print_summary()

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
