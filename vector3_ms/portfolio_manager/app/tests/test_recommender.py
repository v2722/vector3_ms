import datetime

import numpy as np
import pandas as pd
import pytest

from app.services import recommender_service


# ============================================================
# Fixture: in-memory fake DB mirroring the MySQL schema
# ============================================================

ASSETS = [
    {"asset_id": 1, "ticker": "A", "name": "Alpha Corp", "exchange": "NYSE", "sector": "Technology", "industry": "Software"},
    {"asset_id": 2, "ticker": "B", "name": "Beta Inc", "exchange": "NYSE", "sector": "Technology", "industry": "Hardware"},
    {"asset_id": 3, "ticker": "C", "name": "Gamma Bank", "exchange": "NYSE", "sector": "Finance", "industry": "Banking"},
    {"asset_id": 4, "ticker": "D", "name": "Delta Health", "exchange": "NASDAQ", "sector": "Health Care", "industry": "Pharma"},
]

PORTFOLIOS = [
    {"portfolio_id": 1, "name": "Tech Heavy"},
    {"portfolio_id": 2, "name": "Value Mix"},
    {"portfolio_id": 3, "name": "Balanced"},
]

# portfolio_id -> tickers held (net BUY quantity 1)
# p2 overlaps p1 on A,B and adds C; p3 overlaps p1 on B and adds D.
HOLDINGS = {1: ["A", "B"], 2: ["A", "B", "C"], 3: ["B", "D"]}


def _build_prices():
    dates = pd.bdate_range(end=datetime.date.today(), periods=60)
    rows = []
    # A and B share the Technology sector and identical momentum so that
    # content-based profiles keep sector dominance over the small feature space.
    for t, factor in [("A", 1.004), ("B", 1.004), ("C", 1.001), ("D", 0.998)]:
        closes = 100 * factor ** np.arange(60)
        for i, d in enumerate(dates):
            rows.append({"ticker": t, "date": d.date(), "close": float(closes[i])})
    return rows


PRICES = _build_prices()


class FakeCursor:
    def __init__(self, db):
        self.db = db
        self.last_sql = None
        self.params = None

    def execute(self, sql, params=None):
        self.last_sql = sql
        self.params = params or ()

    def fetchall(self):
        sql = self.last_sql

        if "FROM asset" in sql and "price_history" not in sql:
            return ASSETS

        if "ph.close" in sql and "price_history ph" in sql:
            return PRICES

        if "ph.date" in sql and "price_history ph" in sql:
            return PRICES

        if "GROUP BY t.portfolio_id, a.ticker" in sql:
            agg = {}
            for pid, tickers in HOLDINGS.items():
                for t in tickers:
                    agg.setdefault((pid, t), 0.0)
                    agg[(pid, t)] += 1.0
            return [
                {"portfolio_id": pid, "ticker": t, "net": v}
                for (pid, t), v in agg.items()
            ]

        if "FROM transaction t" in sql and "DISTINCT a.ticker" in sql:
            pid = self.params[0]
            return [{"ticker": t} for t in HOLDINGS.get(pid, [])]

        if "FROM portfolio" in sql and "portfolio_id, name" in sql:
            return PORTFOLIOS

        return []

    def fetchone(self):
        rows = self.fetchall()
        return rows[0] if rows else None

    def close(self):
        pass


class FakeDB:
    def cursor(self, dictionary=True):
        return FakeCursor(self)

    def close(self):
        pass


@pytest.fixture(autouse=True)
def fake_db(monkeypatch):
    monkeypatch.setattr(recommender_service, "get_db", lambda: FakeDB())


# ============================================================
# Tests
# ============================================================

def test_content_based_ranks_same_sector_higher():
    result = recommender_service.content_based_recommendations("A", limit=3)
    assert "error" not in result
    tickers = [r["ticker"] for r in result["recommendations"]]
    assert "A" not in tickers
    assert tickers[0] == "B"
    scores = [r["similarity_score"] for r in result["recommendations"]]
    assert scores == sorted(scores, reverse=True)


def test_content_based_unknown_asset():
    result = recommender_service.content_based_recommendations("ZZZZ", limit=3)
    assert result.get("error") == "Asset not found"


def test_collaborative_filtering_excludes_held_and_scores_correctly():
    result = recommender_service.collaborative_filtering(1, limit=5)
    assert "error" not in result
    tickers = [r["ticker"] for r in result["recommendations"]]
    assert "A" not in tickers and "B" not in tickers
    # C is held by both similar portfolios (2 and 3) so it outranks D
    assert tickers[0] == "C"
    assert "D" in tickers


def test_collaborative_filtering_no_holdings():
    result = recommender_service.collaborative_filtering(999, limit=5)
    assert "error" in result


def test_hybrid_recommendations_returns_valid_rows():
    result = recommender_service.hybrid_recommendations(1, limit=5)
    assert "error" not in result
    tickers = [r["ticker"] for r in result["recommendations"]]
    assert "A" not in tickers and "B" not in tickers
    for r in result["recommendations"]:
        assert "content_score" in r and "cf_score" in r and "hybrid_score" in r


def test_correlation_diversification_excludes_held():
    result = recommender_service.correlation_diversification(1, limit=5)
    assert "error" not in result
    held = {"A", "B"}
    for r in result["recommendations"]:
        assert r["ticker"] not in held


def test_trending_recommendations_returns_list():
    result = recommender_service.trending_recommendations(limit=3)
    assert "error" not in result
    assert len(result["recommendations"]) <= 3
    assert all("trend_score" in r for r in result["recommendations"])


def test_gap_completion_targets_missing_sectors():
    result = recommender_service.portfolio_gap_completion(1, limit=5)
    assert "error" not in result
    sectors = {r["sector"] for r in result["recommendations"]}
    # portfolio 1 only holds Technology, so only Finance/Health Care appear
    assert "Technology" not in sectors
    assert {"C", "D"} == {r["ticker"] for r in result["recommendations"]}


def test_similar_portfolios_returns_overlapping_portfolio():
    result = recommender_service.similar_portfolios(1, limit=5)
    assert "error" not in result
    ids = [p["portfolio_id"] for p in result["similar_portfolios"]]
    assert 1 not in ids
    # portfolio 3 shares A with portfolio 1, so it must be present
    assert 3 in ids
