import logging
from datetime import datetime, timedelta

import yfinance as yf
import requests
import finnhub

from app.config import ALPHA_VANTAGE_API_KEY, FINNHUB_API_KEY

logger = logging.getLogger(__name__)


def _yf_fetch_prices(ticker: str, period: str, interval: str):
    hist = yf.Ticker(ticker).history(period=period, interval=interval)
    if hist.empty:
        return None
    rows = []
    for idx, row in hist.iterrows():
        rows.append({
            "date": idx.date(),
            "open": row["Open"],
            "high": row["High"],
            "low": row["Low"],
            "close": row["Close"],
            "volume": int(row["Volume"]),
        })
    return rows


def _av_fetch_prices(ticker: str, period: str, interval: str):
    if not ALPHA_VANTAGE_API_KEY:
        return None

    function_map = {
        ("1d", "1d"): "TIME_SERIES_DAILY",
        ("1d", "1wk"): "TIME_SERIES_WEEKLY",
        ("1d", "1mo"): "TIME_SERIES_MONTHLY",
    }
    av_interval = "daily" if interval == "1d" else interval
    function = function_map.get((period, interval), "TIME_SERIES_DAILY")

    url = "https://www.alphavantage.co/query"
    params = {
        "function": function,
        "symbol": ticker,
        "apikey": ALPHA_VANTAGE_API_KEY,
    }
    resp = requests.get(url, params=params, timeout=30)
    data = resp.json()

    if "Error Message" in data or "Note" in data:
        logger.warning("Alpha Vantage error for %s: %s", ticker, data)
        return None

    time_series_key = next(
        (k for k in data if "Time Series" in k or "Monthly" in k or "Weekly" in k),
        None,
    )
    if not time_series_key:
        return None

    time_series = data[time_series_key]
    rows = []
    for date_str, values in time_series.items():
        rows.append({
            "date": datetime.strptime(date_str, "%Y-%m-%d").date(),
            "open": float(values["1. open"]),
            "high": float(values["2. high"]),
            "low": float(values["3. low"]),
            "close": float(values["4. close"]),
            "volume": int(values["5. volume"]),
        })

    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows


def _fh_fetch_prices(ticker: str, period: str, interval: str):
    if not FINNHUB_API_KEY:
        return None

    client = finnhub.Client(api_key=FINNHUB_API_KEY)

    end = datetime.now()
    period_days = {"1y": 365, "2y": 730, "5y": 1825, "max": 3650}
    days = period_days.get(period, 365)
    start = end - timedelta(days=days)

    resolution = {"1d": "D", "1wk": "W", "1mo": "M"}.get(interval, "D")

    res = client.stock_candles(
        ticker, resolution,
        int(start.timestamp()),
        int(end.timestamp()),
    )
    if not res or res.get("s") != "ok":
        return None

    rows = []
    for c in zip(res["t"], res["o"], res["h"], res["l"], res["c"], res["v"]):
        rows.append({
            "date": datetime.fromtimestamp(c[0]).date(),
            "open": c[1],
            "high": c[2],
            "low": c[3],
            "close": c[4],
            "volume": int(c[5]),
        })

    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows


def fetch_price_history(ticker: str, period: str = "1y", interval: str = "1d"):
    providers = [
        ("yfinance", lambda: _yf_fetch_prices(ticker, period, interval)),
        ("alphavantage", lambda: _av_fetch_prices(ticker, period, interval)),
        ("finnhub", lambda: _fh_fetch_prices(ticker, period, interval)),
    ]

    for name, fn in providers:
        try:
            result = fn()
            if result is not None:
                logger.info("Fetched prices for %s via %s", ticker, name)
                return result
        except Exception as e:
            logger.warning("Provider %s failed for %s: %s", name, ticker, e)

    raise RuntimeError(f"All data providers failed for {ticker}")


def _yf_fetch_asset_info(ticker: str):
    info = yf.Ticker(ticker).info
    if not info or info.get("trailingPegRatio") is None and not info.get("shortName"):
        return None
    return {
        "name": info.get("shortName") or info.get("longName", ""),
        "exchange": info.get("exchange", ""),
        "sector": info.get("sector", ""),
        "industry": info.get("industry", ""),
    }


def _fh_fetch_asset_info(ticker: str):
    if not FINNHUB_API_KEY:
        return None

    client = finnhub.Client(api_key=FINNHUB_API_KEY)
    profile = client.company_profile2(symbol=ticker)
    if not profile or not profile.get("name"):
        return None
    return {
        "name": profile.get("name", ""),
        "exchange": profile.get("exchange", ""),
        "sector": profile.get("finnhubIndustry", ""),
        "industry": "",
    }


def fetch_asset_info(ticker: str):
    providers = [
        ("yfinance", lambda: _yf_fetch_asset_info(ticker)),
        ("finnhub", lambda: _fh_fetch_asset_info(ticker)),
    ]

    for name, fn in providers:
        try:
            result = fn()
            if result is not None:
                logger.info("Fetched asset info for %s via %s", ticker, name)
                return result
        except Exception as e:
            logger.warning("Provider %s failed for asset info %s: %s", name, ticker, e)

    return None
