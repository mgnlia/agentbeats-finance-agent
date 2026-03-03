import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from financial_tools import calculate_financial_ratio, analyze_stock, assess_portfolio_risk

def test_pe_ratio():
    result = calculate_financial_ratio("pe_ratio", {"price": 150, "eps": 10})
    assert result["value"] == 15.0

def test_analyze_stock_buy():
    result = analyze_stock("TEST", {"price": 50, "eps": 5})
    assert result["recommendation"] == "buy"
    assert result["ratios"]["pe_ratio"] == 10.0

def test_portfolio_risk_high_concentration():
    holdings = [
        {"ticker": "AAPL", "weight": 0.5, "sector": "tech"},
        {"ticker": "MSFT", "weight": 0.3, "sector": "tech"},
        {"ticker": "JNJ", "weight": 0.2, "sector": "healthcare"},
    ]
    result = assess_portfolio_risk(holdings)
    assert result["concentration_risk"] == "high"
    assert result["sector_weights"]["tech"] == pytest.approx(0.8)

def test_portfolio_risk_diversified():
    holdings = [{"ticker": f"T{i}", "weight": 0.1, "sector": f"sector{i}"} for i in range(10)]
    result = assess_portfolio_risk(holdings)
    assert result["concentration_risk"] == "low"
