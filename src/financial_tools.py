"""
Financial tools for the AgentBeats Finance Agent.
These are callable by the LLM as function/tool calls.
"""
from typing import Any
import json


TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "calculate_financial_ratio",
            "description": "Calculate a financial ratio given a metric name and required values.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric": {
                        "type": "string",
                        "description": "Ratio to calculate: pe_ratio, pb_ratio, ev_ebitda, debt_equity, current_ratio, roe, roa, gross_margin, net_margin, sharpe_ratio",
                    },
                    "values": {
                        "type": "object",
                        "description": "Key-value pairs of financial inputs required for the ratio (e.g. {price: 100, eps: 5})",
                    },
                },
                "required": ["metric", "values"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_stock",
            "description": "Analyze a stock given ticker and available financial data. Returns valuation, trend, and recommendation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol (e.g. AAPL)"},
                    "data": {
                        "type": "object",
                        "description": "Available financial data: price, eps, revenue, ebitda, debt, equity, etc.",
                    },
                },
                "required": ["ticker", "data"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "assess_portfolio_risk",
            "description": "Assess risk of a portfolio given its holdings.",
            "parameters": {
                "type": "object",
                "properties": {
                    "holdings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "ticker": {"type": "string"},
                                "weight": {"type": "number"},
                                "sector": {"type": "string"},
                            },
                        },
                        "description": "List of holdings with ticker, weight (0-1), and sector",
                    }
                },
                "required": ["holdings"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_market_data",
            "description": "Search for market data, news, or financial information for a given query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for market data or financial news"},
                },
                "required": ["query"],
            },
        },
    },
]


def calculate_financial_ratio(metric: str, values: dict[str, Any]) -> dict:
    """Execute financial ratio calculations."""
    try:
        result = None
        if metric == "pe_ratio":
            result = values["price"] / values["eps"]
        elif metric == "pb_ratio":
            result = values["price"] / values["book_value_per_share"]
        elif metric == "ev_ebitda":
            result = values["enterprise_value"] / values["ebitda"]
        elif metric == "debt_equity":
            result = values["total_debt"] / values["total_equity"]
        elif metric == "current_ratio":
            result = values["current_assets"] / values["current_liabilities"]
        elif metric == "roe":
            result = values["net_income"] / values["shareholders_equity"]
        elif metric == "roa":
            result = values["net_income"] / values["total_assets"]
        elif metric == "gross_margin":
            result = (values["revenue"] - values["cogs"]) / values["revenue"]
        elif metric == "net_margin":
            result = values["net_income"] / values["revenue"]
        elif metric == "sharpe_ratio":
            result = (values["portfolio_return"] - values["risk_free_rate"]) / values["std_deviation"]
        else:
            return {"error": f"Unknown metric: {metric}"}
        return {"metric": metric, "value": round(result, 4), "inputs": values}
    except (KeyError, ZeroDivisionError) as e:
        return {"error": str(e), "metric": metric}


def analyze_stock(ticker: str, data: dict[str, Any]) -> dict:
    """Analyze a stock and return structured assessment."""
    ratios = {}
    if "price" in data and "eps" in data and data["eps"] != 0:
        ratios["pe_ratio"] = round(data["price"] / data["eps"], 2)
    if "net_income" in data and "revenue" in data and data["revenue"] != 0:
        ratios["net_margin"] = round(data["net_income"] / data["revenue"], 4)
    if "total_debt" in data and "total_equity" in data and data["total_equity"] != 0:
        ratios["debt_equity"] = round(data["total_debt"] / data["total_equity"], 2)

    pe = ratios.get("pe_ratio", 0)
    recommendation = "hold"
    if pe > 0 and pe < 15:
        recommendation = "buy"
    elif pe > 30:
        recommendation = "sell"

    return {
        "ticker": ticker,
        "ratios": ratios,
        "valuation": "undervalued" if recommendation == "buy" else ("overvalued" if recommendation == "sell" else "fairly_valued"),
        "recommendation": recommendation,
        "data_completeness": f"{len(data)} fields provided",
    }


def assess_portfolio_risk(holdings: list[dict]) -> dict:
    """Assess portfolio risk from holdings list."""
    if not holdings:
        return {"error": "No holdings provided"}

    sector_weights: dict[str, float] = {}
    for h in holdings:
        sector = h.get("sector", "unknown")
        sector_weights[sector] = sector_weights.get(sector, 0) + h.get("weight", 0)

    max_sector_weight = max(sector_weights.values()) if sector_weights else 0
    num_holdings = len(holdings)
    concentration_risk = "high" if max_sector_weight > 0.4 else ("medium" if max_sector_weight > 0.25 else "low")

    hhi = sum(w ** 2 for w in [h.get("weight", 0) for h in holdings])
    diversification_score = round(1 - hhi, 3)

    suggestions = []
    if concentration_risk == "high":
        top_sector = max(sector_weights, key=sector_weights.get)
        suggestions.append(f"Reduce {top_sector} concentration ({sector_weights[top_sector]:.0%} of portfolio)")
    if num_holdings < 10:
        suggestions.append("Consider adding more holdings to improve diversification")

    return {
        "num_holdings": num_holdings,
        "sector_weights": {k: round(v, 3) for k, v in sector_weights.items()},
        "concentration_risk": concentration_risk,
        "diversification_score": diversification_score,
        "hhi": round(hhi, 4),
        "suggestions": suggestions,
    }


def search_market_data(query: str) -> dict:
    """Stub for market data search — returns structured placeholder."""
    return {
        "query": query,
        "note": "Live market data search requires API key configuration (ALPHA_VANTAGE_KEY or FINNHUB_KEY env var)",
        "suggestion": f"For '{query}', consider: Yahoo Finance, Alpha Vantage, or Finnhub APIs",
    }


TOOL_DISPATCH = {
    "calculate_financial_ratio": calculate_financial_ratio,
    "analyze_stock": analyze_stock,
    "assess_portfolio_risk": assess_portfolio_risk,
    "search_market_data": search_market_data,
}


def dispatch_tool(name: str, arguments: dict) -> str:
    fn = TOOL_DISPATCH.get(name)
    if not fn:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        result = fn(**arguments)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})
