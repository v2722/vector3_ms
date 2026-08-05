import asyncio
import random
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.price_service import get_price_history

router = APIRouter(tags=["Realtime"])

BASE_PRICES = {
    "AAPL": 210.5,
    "MSFT": 435.2,
    "GOOGL": 175.4,
    "AMZN": 185.9,
    "TSLA": 248.7,
    "NVDA": 122.8,
    "META": 495.1,
    "NFLX": 655.3,
    "AMD": 162.4,
    "INTC": 34.2,
}


def _seed_price(ticker: str):
    if ticker in BASE_PRICES:
        return BASE_PRICES[ticker]
    return round(10 + (abs(hash(ticker)) % 9000) / 10, 2)


def _last_close(ticker: str):
    try:
        rows = get_price_history(ticker)
        if rows:
            return float(rows[0]["close"])
    except Exception:
        pass
    return None


@router.websocket("/ws/live")
async def live_prices(websocket: WebSocket):
    await websocket.accept()
    last = {}
    running = True
    try:
        while running:
            message = await websocket.receive_text()
            try:
                payload = json.loads(message)
            except Exception:
                payload = {}
            tickers = payload.get("tickers") or list(BASE_PRICES.keys())

            for ticker in tickers:
                if ticker not in last:
                    base = _last_close(ticker) or _seed_price(ticker)
                    last[ticker] = base

                prev = last[ticker]
                drift = 0.0002
                shock = random.gauss(0, 0.004)
                change = prev * (drift + shock)
                price = max(prev + change, 0.01)
                last[ticker] = price

                await websocket.send_json({
                    "ticker": ticker,
                    "price": round(price, 2),
                    "change": round(price - prev, 2),
                    "change_pct": round((price - prev) / prev * 100, 2),
                    "timestamp": int(asyncio.get_event_loop().time() * 1000),
                })
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        running = False
    except Exception:
        try:
            await websocket.close()
        except Exception:
            pass
