import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from app.database.connection import get_db


# ============================================================
# Internal helpers
# ============================================================

def _resolve_db(db):
    """Return (db, own_connection) so callers can close only what they opened."""
    if db is not None:
        return db, False
    return get_db(), True


def _close(db, own):
    if own:
        try:
            db.close()
        except Exception:
            pass


def _load_asset_rows(db):
    """Load all assets with their descriptive metadata."""
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT asset_id, ticker, name, exchange, sector, industry FROM asset"
    )
    rows = cursor.fetchall()
    cursor.close()
    return rows


def _load_price_stats(db, limit=504):
    """
    Compute per-ticker statistics from price_history.
    Returns dict: ticker -> {volatility, momentum_20, momentum_60, last_close}
    """
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT a.ticker, ph.close FROM price_history ph "
        "JOIN asset a ON ph.asset_id = a.asset_id "
        "ORDER BY a.ticker, ph.date ASC"
    )
    rows = cursor.fetchall()
    cursor.close()

    stats = {}
    grouped = {}
    for row in rows:
        grouped.setdefault(row["ticker"], []).append(float(row["close"]))

    for ticker, closes in grouped.items():
        closes = closes[-limit:]
        if len(closes) < 21:
            stats[ticker] = {
                "volatility": 0.15,
                "momentum_20": 0.0,
                "momentum_60": 0.0,
                "last_close": closes[-1] if closes else 0.0,
            }
            continue

        prices = np.array(closes)
        returns = np.diff(prices) / prices[:-1]
        volatility = float(np.std(returns) * np.sqrt(252))
        mom20 = float(prices[-1] / prices[-21] - 1) if len(prices) >= 21 else 0.0
        mom60 = float(prices[-1] / prices[-61] - 1) if len(prices) >= 61 else mom20

        stats[ticker] = {
            "volatility": volatility,
            "momentum_20": mom20,
            "momentum_60": mom60,
            "last_close": float(prices[-1]),
        }
    return stats


def _build_feature_matrix(db, stats, asset_rows, max_industries=40):
    """
    Build a numeric feature matrix from asset metadata + price statistics.
    Features: one-hot sector, one-hot industry (top N), plus normalized
    volatility, momentum_20, momentum_60.
    Returns (features, tickers, feature_names).
    """
    sector_counter = {}
    industry_counter = {}
    for a in asset_rows:
        sector_counter[a.get("sector") or "Unknown"] = sector_counter.get(a.get("sector") or "Unknown", 0) + 1
        industry_counter[a.get("industry") or "Unknown"] = industry_counter.get(a.get("industry") or "Unknown", 0) + 1

    sectors = sorted(sector_counter, key=sector_counter.get, reverse=True)
    industries = sorted(industry_counter, key=industry_counter.get, reverse=True)[:max_industries]

    vectors = []
    tickers = []
    cont_values = []  # collect continuous features for min-max normalization

    for a in asset_rows:
        ticker = a["ticker"]
        stat = stats.get(ticker, {
            "volatility": 0.15, "momentum_20": 0.0, "momentum_60": 0.0
        })
        vec_len = len(sectors) + len(industries) + 3
        vec = np.zeros(vec_len)

        sector = a.get("sector") or "Unknown"
        if sector in sectors:
            vec[sectors.index(sector)] = 1
        industry = a.get("industry") or "Unknown"
        if industry in industries:
            vec[len(sectors) + industries.index(industry)] = 1
        vec[len(sectors) + len(industries)] = stat["volatility"]
        vec[len(sectors) + len(industries) + 1] = stat["momentum_20"]
        vec[len(sectors) + len(industries) + 2] = stat["momentum_60"]

        vectors.append(vec)
        tickers.append(ticker)
        cont_values.append([stat["volatility"], stat["momentum_20"], stat["momentum_60"]])

    features = np.array(vectors, dtype=np.float64)
    if len(features):
        cont = np.array(cont_values, dtype=np.float64)
        mins = cont.min(axis=0)
        maxs = cont.max(axis=0)
        ranges = (maxs - mins)
        ranges[ranges == 0] = 1.0
        norm = (cont - mins) / ranges
        features[:, -3:] = norm

    feature_names = sectors + industries + ["volatility", "momentum_20", "momentum_60"]
    return features, tickers, feature_names


def _load_interactions(db):
    """
    Build a portfolio x asset interaction table from transactions.
    Returns dict: portfolio_id -> {ticker: net_quantity}
    """
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT t.portfolio_id, a.ticker, "
        "SUM(CASE WHEN t.type = 'BUY' THEN t.quantity ELSE -t.quantity END) AS net "
        "FROM transaction t JOIN asset a ON t.asset_id = a.asset_id "
        "GROUP BY t.portfolio_id, a.ticker"
    )
    rows = cursor.fetchall()
    cursor.close()

    interactions = {}
    for row in rows:
        net = float(row["net"])
        if net < 0:
            net = 0.0
        if not net:
            continue
        interactions.setdefault(row["portfolio_id"], {})[row["ticker"]] = net
    return interactions


def _portfolio_tickers(portfolio_id, db):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT DISTINCT a.ticker FROM transaction t "
        "JOIN asset a ON t.asset_id = a.asset_id WHERE t.portfolio_id = %s",
        (portfolio_id,),
    )
    rows = cursor.fetchall()
    cursor.close()
    return [row["ticker"] for row in rows]


def _returns_series(db, limit=252):
    """
    Build aligned daily return series for all tickers.
    Returns DataFrame indexed by ticker (columns are dates).
    """
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT a.ticker, ph.date, ph.close FROM price_history ph "
        "JOIN asset a ON ph.asset_id = a.asset_id ORDER BY a.ticker, ph.date ASC"
    )
    rows = cursor.fetchall()
    cursor.close()

    grouped = {}
    for row in rows:
        grouped.setdefault(row["ticker"], {}).setdefault(
            row["date"].isoformat() if hasattr(row["date"], "isoformat") else str(row["date"]),
            float(row["close"]),
        )

    frame = pd.DataFrame(grouped)
    frame = frame.tail(limit)
    returns = frame.pct_change().dropna(how="all")
    return returns


def _raw_similarity(db, ticker, limit):
    """Content-based cosine similarity of one asset vs. all others."""
    asset_rows = _load_asset_rows(db)
    tickers = [a["ticker"] for a in asset_rows]
    if ticker not in tickers:
        return None

    stats = _load_price_stats(db)
    features, feat_tickers, _ = _build_feature_matrix(db, stats, asset_rows)
    idx = feat_tickers.index(ticker)
    target = features[idx]
    sims = cosine_similarity(target.reshape(1, -1), features)[0]
    ranked = sorted(
        [(feat_tickers[i], float(sims[i])) for i in range(len(feat_tickers)) if i != idx],
        key=lambda x: x[1],
        reverse=True,
    )
    return ranked[:limit]


# ============================================================
# CONTENT-BASED RECOMMENDATIONS (VECTORIZED)
# ============================================================

def content_based_recommendations(ticker: str, limit: int = 5, db=None) -> dict:
    """Recommend assets similar to a given asset using cosine similarity
    over sector, industry, volatility and momentum features."""
    db, own = _resolve_db(db)
    try:
        asset_rows = _load_asset_rows(db)
        stats = _load_price_stats(db)
        features, feat_tickers, feature_names = _build_feature_matrix(db, stats, asset_rows)

        if ticker not in feat_tickers:
            return {"error": "Asset not found"}

        idx = feat_tickers.index(ticker)
        target = features[idx]
        sims = cosine_similarity(target.reshape(1, -1), features)[0]
        order = np.argsort(sims)[::-1]

        # Top matching feature (for a human-readable reason)
        target_named = {feature_names[k]: target[k] for k in range(len(feature_names))}
        top_features = sorted(
            [(feature_names[k], float(target[k])) for k in range(len(feature_names))],
            key=lambda x: x[1],
            reverse=True,
        )[:2]

        recommendations = []
        name_by_ticker = {a["ticker"]: a.get("name") for a in asset_rows}
        sector_by_ticker = {a["ticker"]: a.get("sector") for a in asset_rows}
        for i in order:
            if len(recommendations) >= limit:
                break
            t = feat_tickers[i]
            if t == ticker:
                continue
            sim = float(sims[i])
            recommendations.append({
                "ticker": t,
                "name": name_by_ticker.get(t),
                "similarity_score": round(sim, 4),
                "reason": f"Shared profile: {top_features[0][0]}, {top_features[1][0]} "
                          f"(similar to {ticker}, sector {sector_by_ticker.get(t)})",
            })
        return {
            "input_asset": ticker,
            "method": "content_based_cosine",
            "recommendations": recommendations,
        }
    finally:
        _close(db, own)


# ============================================================
# COLLABORATIVE FILTERING (USER/PORTFOLIO-BASED)
# ============================================================

def collaborative_filtering(portfolio_id: int, limit: int = 5, db=None) -> dict:
    """
    True item-based collaborative filtering over portfolios.
    Builds a portfolio x asset interaction matrix, finds portfolios most
    similar to the target, then recommends assets held by them but not
    yet held by the target portfolio.
    """
    db, own = _resolve_db(db)
    try:
        interactions = _load_interactions(db)
        if portfolio_id not in interactions or not interactions[portfolio_id]:
            return {"error": "Portfolio has no holdings to base recommendations on"}

        portfolios = sorted(interactions.keys())
        all_tickers = sorted({t for p in portfolios for t in interactions[p]})

        t_idx = {p: i for i, p in enumerate(portfolios)}
        a_idx = {t: i for i, t in enumerate(all_tickers)}

        matrix = np.zeros((len(portfolios), len(all_tickers)))
        for p, held in interactions.items():
            for t, val in held.items():
                matrix[t_idx[p], a_idx[t]] = val

        target = matrix[t_idx[portfolio_id]]
        sims = cosine_similarity(target.reshape(1, -1), matrix)[0]

        similar_others = [
            (portfolios[i], float(sims[i])) for i in range(len(portfolios))
            if i != t_idx[portfolio_id] and sims[i] > 0
        ]

        held = set(interactions[portfolio_id].keys())
        scores = {}
        contributors = {}
        for other, sim in similar_others:
            for t in interactions[other]:
                if t in held:
                    continue
                scores[t] = scores.get(t, 0.0) + sim * interactions[other][t]
                contributors.setdefault(t, 0)
                contributors[t] += 1

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]

        name_by_ticker = {a["ticker"]: a.get("name") for a in _load_asset_rows(db)}
        recommendations = []
        for t, score in ranked:
            recommendations.append({
                "ticker": t,
                "name": name_by_ticker.get(t),
                "cf_score": round(score, 4),
                "similar_investors": contributors.get(t, 0),
                "reason": f"Held by {contributors.get(t, 0)} similar portfolio(s)",
            })

        top_similar = sorted(similar_others, key=lambda x: x[1], reverse=True)[:3]
        return {
            "portfolio_id": portfolio_id,
            "method": "collaborative_filtering",
            "similar_portfolios": [
                {"portfolio_id": p, "similarity": round(s, 4)} for p, s in top_similar
            ],
            "recommendations": recommendations,
        }
    finally:
        _close(db, own)


# ============================================================
# HYBRID (CONTENT + COLLABORATIVE)
# ============================================================

def hybrid_recommendations(portfolio_id: int, limit: int = 5, content_weight: float = 0.5, db=None) -> dict:
    """Blend content similarity to current holdings with collaborative scores."""
    db, own = _resolve_db(db)
    try:
        held = _portfolio_tickers(portfolio_id, db)
        if not held:
            return {"error": "Portfolio has no holdings"}

        cf = collaborative_filtering(portfolio_id, limit=50, db=db)
        cf_score = {r["ticker"]: r["cf_score"] for r in cf.get("recommendations", [])}

        stats = _load_price_stats(db)
        asset_rows = _load_asset_rows(db)
        features, feat_tickers, _ = _build_feature_matrix(db, stats, asset_rows)

        held_idx = [feat_tickers.index(t) for t in held if t in feat_tickers]
        if not held_idx:
            return {"error": "Holdings have no feature data"}

        held_vec = features[held_idx].mean(axis=0).reshape(1, -1)
        sims = cosine_similarity(held_vec, features)[0]

        content_score = {feat_tickers[i]: float(sims[i]) for i in range(len(feat_tickers))}

        candidates = set(content_score.keys()) & set(cf_score.keys())
        candidates = {c for c in candidates if c not in held}

        results = []
        for c in candidates:
            hybrid = content_weight * content_score[c] + (1 - content_weight) * cf_score[c]
            results.append({
                "ticker": c,
                "content_score": round(content_score[c], 4),
                "cf_score": round(cf_score[c], 4),
                "hybrid_score": round(hybrid, 4),
            })

        results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        results = results[:limit]

        name_by_ticker = {a["ticker"]: a.get("name") for a in asset_rows}
        for r in results:
            r["name"] = name_by_ticker.get(r["ticker"])

        return {
            "portfolio_id": portfolio_id,
            "method": "hybrid_weighted",
            "content_weight": content_weight,
            "recommendations": results,
        }
    finally:
        _close(db, own)


# ============================================================
# CORRELATION-BASED DIVERSIFICATION
# ============================================================

def diversification_recommendations(portfolio_id: int, limit: int = 5, db=None) -> dict:
    return correlation_diversification(portfolio_id, limit, db=db)


def correlation_diversification(portfolio_id: int, limit: int = 5, db=None) -> dict:
    """
    Recommend assets least correlated with the current portfolio to
    genuinely reduce concentration risk.
    """
    db, own = _resolve_db(db)
    try:
        held = _portfolio_tickers(portfolio_id, db)
        if not held:
            return {"error": "Portfolio has no holdings"}

        returns = _returns_series(db)
        available = [t for t in returns.columns if t not in held]

        held_data = [returns.loc[:, t].dropna() for t in held if t in returns.columns]
        if not held_data:
            return {"error": "Insufficient price data for held assets"}

        portfolio_ret = pd.concat(held_data, axis=1).mean(axis=1)

        rows = []
        for t in available:
            series = returns[t].dropna()
            common = portfolio_ret.index.intersection(series.index)
            if len(common) < 20:
                continue
            corr = portfolio_ret.loc[common].corr(series.loc[common])
            if np.isnan(corr):
                continue
            rows.append({"ticker": t, "correlation": float(corr)})

        rows.sort(key=lambda x: x["correlation"])
        rows = rows[:limit]

        name_by_ticker = {a["ticker"]: a.get("name") for a in _load_asset_rows(db)}
        sector_by_ticker = {a["ticker"]: a.get("sector") for a in _load_asset_rows(db)}
        for r in rows:
            r["name"] = name_by_ticker.get(r["ticker"])
            r["sector"] = sector_by_ticker.get(r["ticker"])
            r["reason"] = f"Correlation {r['correlation']:.3f} with current portfolio (low = good for diversification)"

        held_sectors = [
            (a.get("sector") or "Unknown") for a in _load_asset_rows(db) if a["ticker"] in held
        ]
        return {
            "portfolio_id": portfolio_id,
            "method": "correlation_diversification",
            "held_assets": held,
            "held_sectors": held_sectors,
            "recommendations": rows,
        }
    finally:
        _close(db, own)


# ============================================================
# TRENDING / MOMENTUM
# ============================================================

def trending_recommendations(limit: int = 5, db=None) -> dict:
    """Rank assets by recent momentum combined with investor popularity."""
    db, own = _resolve_db(db)
    try:
        stats = _load_price_stats(db)
        interactions = _load_interactions(db)

        popularity = {}
        for held in interactions.values():
            for t in held:
                popularity[t] = popularity.get(t, 0) + 1

        rows = []
        for t, s in stats.items():
            mom = 0.5 * s["momentum_60"] + 0.5 * s["momentum_20"]
            pop = popularity.get(t, 0)
            # normalize momentum rank and popularity rank into a combined score
            rows.append({"ticker": t, "momentum": mom, "popularity": pop})

        if not rows:
            return {"recommendations": []}

        rows = sorted(rows, key=lambda x: x["momentum"], reverse=True)
        mom_rank = {r["ticker"]: i for i, r in enumerate(rows)}
        total = max(len(rows), 1)
        for r in rows:
            r["momentum_score"] = round(1 - mom_rank[r["ticker"]] / total, 4)
            r["popularity_score"] = round(r["popularity"] / (total or 1), 4)
            r["trend_score"] = round(r["momentum_score"] + r["popularity_score"], 4)

        rows = sorted(rows, key=lambda x: x["trend_score"], reverse=True)[:limit]

        name_by_ticker = {a["ticker"]: a.get("name") for a in _load_asset_rows(db)}
        sector_by_ticker = {a["ticker"]: a.get("sector") for a in _load_asset_rows(db)}
        for r in rows:
            r["name"] = name_by_ticker.get(r["ticker"])
            r["sector"] = sector_by_ticker.get(r["ticker"])

        return {
            "method": "trending_momentum",
            "recommendations": rows,
        }
    finally:
        _close(db, own)


# ============================================================
# PORTFOLIO GAP COMPLETION
# ============================================================

def portfolio_gap_completion(portfolio_id: int, limit: int = 5, db=None) -> dict:
    """Suggest assets from sectors the portfolio does not yet cover."""
    db, own = _resolve_db(db)
    try:
        held = _portfolio_tickers(portfolio_id, db)
        asset_rows = _load_asset_rows(db)
        sector_by_ticker = {a["ticker"]: a.get("sector") for a in asset_rows}
        name_by_ticker = {a["ticker"]: a.get("name") for a in asset_rows}

        held_sectors = {sector_by_ticker.get(t) for t in held if sector_by_ticker.get(t)}
        stats = _load_price_stats(db)

        rows = []
        for a in asset_rows:
            t = a["ticker"]
            if t in held:
                continue
            sector = a.get("sector")
            if not sector or sector in held_sectors:
                continue
            rows.append({
                "ticker": t,
                "name": a.get("name"),
                "sector": sector,
                "momentum": stats.get(t, {}).get("momentum_60", 0.0),
            })

        # pick the strongest momentum asset in each unrepresented sector
        by_sector = {}
        for r in rows:
            by_sector.setdefault(r["sector"], []).append(r)

        picks = []
        for sector, candidates in by_sector.items():
            candidates.sort(key=lambda x: x["momentum"], reverse=True)
            picks.append(candidates[0])
        picks.sort(key=lambda x: x["momentum"], reverse=True)
        picks = picks[:limit]

        for p in picks:
            p["reason"] = f"Adds exposure to {p['sector']}, a sector not currently in held set"

        return {
            "portfolio_id": portfolio_id,
            "method": "portfolio_gap_completion",
            "current_sectors": sorted(held_sectors - {None}),
            "missing_sectors": sorted(by_sector.keys()),
            "recommendations": picks,
        }
    finally:
        _close(db, own)


# ============================================================
# SIMILAR PORTFOLIOS
# ============================================================

def similar_portfolios(portfolio_id: int, limit: int = 5, db=None) -> dict:
    """Return portfolios most similar to the target by holding overlap."""
    db, own = _resolve_db(db)
    try:
        interactions = _load_interactions(db)
        if portfolio_id not in interactions or not interactions[portfolio_id]:
            return {"error": "Portfolio has no holdings"}

        portfolios = sorted(interactions.keys())
        all_tickers = sorted({t for p in portfolios for t in interactions[p]})

        p_idx = {p: i for i, p in enumerate(portfolios)}
        a_idx = {t: i for i, t in enumerate(all_tickers)}

        matrix = np.zeros((len(portfolios), len(all_tickers)))
        for p, held in interactions.items():
            for t, val in held.items():
                matrix[p_idx[p], a_idx[t]] = val

        target = matrix[p_idx[portfolio_id]]
        sims = cosine_similarity(target.reshape(1, -1), matrix)[0]

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT portfolio_id, name FROM portfolio")
        names = {r["portfolio_id"]: r.get("name") for r in cursor.fetchall()}
        cursor.close()

        results = []
        for i in range(len(portfolios)):
            if i == p_idx[portfolio_id]:
                continue
            sim = float(sims[i])
            overlap = set(interactions[portfolio_id]) & set(interactions[portfolios[i]])
            results.append({
                "portfolio_id": portfolios[i],
                "name": names.get(portfolios[i]),
                "similarity": round(sim, 4),
                "overlap_tickers": sorted(overlap),
            })
        results.sort(key=lambda x: x["similarity"], reverse=True)
        results = results[:limit]

        return {
            "portfolio_id": portfolio_id,
            "method": "similar_portfolios",
            "similar_portfolios": results,
        }
    finally:
        _close(db, own)