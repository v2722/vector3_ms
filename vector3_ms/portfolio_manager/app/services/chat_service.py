import re

from app.database.connection import get_db
from app.services.portfolio_service import list_portfolios
from app.services.asset_service import list_assets
from app.services.transaction_service import list_transactions
from app.services.risk_service import (
    calculate_sharpe_ratio,
    calculate_var,
    calculate_max_drawdown,
    calculate_volatility,
)
from app.services.recommender_service import portfolio_gap_completion
from app.services.performance_service import list_performance


def _default_portfolio_id():
    portfolios = list_portfolios()
    if portfolios:
        return int(portfolios[0]["portfolio_id"])
    return None


def _portfolio_id_from_message(message, portfolios):
    m = re.search(r"portfolio\s*[#:]?\s*(\d+)", message.lower())
    if m:
        requested = int(m.group(1))
        for p in portfolios:
            if int(p["portfolio_id"]) == requested:
                return requested
    return None


def _format_currency(value):
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return "n/a"


def _handle_help():
    return (
        "I can help you understand your portfolio. Try asking:\n"
        "\u2022 \"List my portfolios\"\n"
        "\u2022 \"What assets/holdings do I have?\"\n"
        "\u2022 \"Risk summary for portfolio 1\"\n"
        "\u2022 \"Sharpe ratio\" or \"VaR\"\n"
        "\u2022 \"Recommendations for portfolio 1\"\n"
        "\u2022 \"Transactions in portfolio 1\"\n"
        "\u2022 \"Performance of portfolio 1\"\n"
        "\u2022 \"Price of AAPL\"\n"
    )


def _handle_portfolios():
    portfolios = list_portfolios()
    if not portfolios:
        return "There are no portfolios stored yet."
    lines = ["You have the following portfolios:"]
    for p in portfolios:
        desc = p.get("description") or "No description"
        lines.append(f"- Portfolio {p['portfolio_id']}: {p['name']} ({desc})")
    return "\n".join(lines)


def _handle_assets():
    assets = list_assets()
    if not assets:
        return "There are no assets in the database yet."
    lines = [f"You are tracking {len(assets)} assets:"]
    for a in assets:
        sector = a.get("sector") or "n/a"
        lines.append(f"- {a['ticker']} — {a.get('name') or 'n/a'} ({sector})")
    return "\n".join(lines)


def _handle_risk(portfolio_id):
    sharpe = calculate_sharpe_ratio(portfolio_id)
    var = calculate_var(portfolio_id)
    drawdown = calculate_max_drawdown(portfolio_id)

    lines = [f"Risk summary for portfolio {portfolio_id}:"]
    if "sharpe_ratio" in sharpe:
        lines.append(
            f"- Sharpe ratio: {sharpe['sharpe_ratio']:.2f} "
            f"(annual return {sharpe['annual_return']*100:.1f}%, "
            f"volatility {sharpe['annual_volatility']*100:.1f}%)"
        )
    else:
        lines.append("- Sharpe ratio: insufficient data")
    if "var_amount" in var:
        lines.append(f"- VaR (95%): {var['interpretation']}")
    else:
        lines.append("- VaR: insufficient data")
    if "max_drawdown_percent" in drawdown:
        lines.append(f"- Max drawdown: {abs(drawdown['max_drawdown_percent']):.2f}%")
    else:
        lines.append("- Max drawdown: insufficient data")
    return "\n".join(lines)


def _handle_recommendations(portfolio_id):
    recs = portfolio_gap_completion(portfolio_id, limit=5)
    suggestions = recs.get("recommendations") or []
    if not suggestions:
        return f"No recommendations available for portfolio {portfolio_id}."
    lines = [f"Top recommendations for portfolio {portfolio_id}:"]
    for r in suggestions:
        score = r.get("similarity_score")
        momentum = r.get("momentum")
        score_txt = f"{float(score):.2f}" if score is not None else None
        if score_txt is None and momentum is not None:
            score_txt = f"momentum {float(momentum):.2f}"
        if score_txt is None:
            score_txt = "n/a"
        name = r.get("name") or ""
        reason = r.get("reason") or "Strong alignment with your current basket"
        if momentum is not None and score_txt.startswith("momentum"):
            lines.append(f"- {r.get('ticker')}{(' — ' + name) if name else ''} ({score_txt}): {reason}")
        else:
            lines.append(f"- {r.get('ticker')}{(' — ' + name) if name else ''} (score {score_txt}): {reason}")
    return "\n".join(lines)


def _handle_transactions(portfolio_id):
    txns = list_transactions(portfolio_id)
    if not txns:
        return f"No transactions found for portfolio {portfolio_id}."
    assets = {a["asset_id"]: a.get("ticker", "?") for a in list_assets()}
    lines = [f"Transactions in portfolio {portfolio_id}:"]
    for t in txns[:10]:
        ticker = assets.get(t.get("asset_id"))
        qty = t.get("quantity") or 0
        price = t.get("price") or 0
        ttype = t.get("type") or t.get("transaction_type") or "?"
        ts = t.get("timestamp")
        lines.append(f"- {ttype} {qty} x {ticker} @ {_format_currency(price)} ({ts})")
    return "\n".join(lines)


def _handle_performance(portfolio_id):
    rows = list_performance(portfolio_id)
    if not rows:
        return f"No performance records for portfolio {portfolio_id}."
    lines = [f"Performance snapshot for portfolio {portfolio_id}:"]
    for r in rows[:5]:
        lines.append(
            f"- {r.get('date')}: total value {_format_currency(r.get('total_value'))}"
        )
    return "\n".join(lines)


def _handle_price(ticker):
    from app.services.price_service import get_price_history

    rows = get_price_history(ticker)
    if not rows:
        return f"No price history available for {ticker}."
    latest = rows[0]
    return (
        f"Latest price for {ticker} on {latest.get('date')}: "
        f"{_format_currency(latest.get('close'))}"
    )


_STOPWORDS = {
    "WHAT", "THE", "AND", "FOR", "HOW", "MUCH", "PRICE", "STOCK", "WHICH",
    "WITH", "YOU", "YOUR", "CAN", "WILL", "ALL", "ANY", "SOME", "THIS",
    "THAT", "THERE", "ABOUT", "THEN", "NAME", "HOLDINGS", "ASSETS", "SECTOR",
}


def _extract_ticker(message):
    known_assets = list_assets()
    known = {a.get("ticker") for a in known_assets if a.get("ticker")}
    up = message.upper()
    for token in re.findall(r"[A-Z]{1,5}", up):
        if token in known:
            return token
    for token in re.findall(r"\b[A-Z]{1,5}\b", up):
        if token not in _STOPWORDS:
            return token
    return None


def _handle_transaction_value(portfolio_id):
    txns = list_transactions(portfolio_id)
    if not txns:
        return f"No holdings information for portfolio {portfolio_id}."
    assets = {a["asset_id"]: a for a in list_assets()}
    total = 0.0
    lines = [f"Holdings for portfolio {portfolio_id}:"]
    for t in txns:
        asset = assets.get(t.get("asset_id"))
        sign = 1 if (t.get("type") == "BUY") else -1
        total += sign * float(t.get("quantity") or 0) * float(t.get("price") or 0)
    for t in txns:
        asset = assets.get(t.get("asset_id"))
        ticker = asset.get("ticker") if asset else "?"
        lines.append(
            f"- {ticker}: {t.get('type')} {t.get('quantity')} @ {_format_currency(t.get('price'))}"
        )
    lines.append(f"Net invested: {_format_currency(total)}")
    return "\n".join(lines)


def answer_question(message: str, portfolio_id=None):
    if not message or not message.strip():
        return "Please ask me something about your portfolio."

    text = message.strip().lower()

    if any(word in text for word in ["hi", "hello", "hey", "help", "what can you", "?"]) and len(text) < 30:
        return _handle_help()

    portfolios = list_portfolios()
    if portfolio_id is None:
        portfolio_id = _portfolio_id_from_message(message, portfolios)
    if portfolio_id is None:
        portfolio_id = _default_portfolio_id()

    if any(word in text for word in ["portfolio", "list", "how many"]):
        if any(word in text for word in ["list", "how many", "show me", "all"]):
            return _handle_portfolios()

    if any(word in text for word in ["asset", "holdings", "holding", "stock", "stocks", "ticker", "tracked"]):
        ticker = _extract_ticker(message)
        if ticker and any(word in text for word in ["price", "cost", "value", "how much", "latest"]):
            return _handle_price(ticker)
        return _handle_assets()

    if any(word in text for word in ["price", "quote", "cost of", "value of"]):
        ticker = _extract_ticker(message)
        if ticker:
            return _handle_price(ticker)

    if any(word in text for word in ["risk", "volatility", "volatile", "var", "drawdown", "sharpe"]):
        return _handle_risk(portfolio_id)

    if any(word in text for word in ["recommend", "suggest", "opportunit", "buy", "gap"]):
        return _handle_recommendations(portfolio_id)

    if any(word in text for word in ["transaction", "trade", "buy", "sell", "purchas"]):
        if any(word in text for word in ["invested", "value", "worth", "net", "position"]):
            return _handle_transaction_value(portfolio_id)
        return _handle_transactions(portfolio_id)

    if any(word in text for word in ["performance", "return", "trend", "growth", "snapshot"]):
        return _handle_performance(portfolio_id)

    return (
        "I'm not sure I understood. I can tell you about your portfolios, assets, "
        "risk metrics, recommendations, transactions, and performance. Type \"help\" "
        "to see what I can do."
    )
