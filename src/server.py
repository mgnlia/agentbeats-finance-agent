"""
AgentBeats Finance Purple Agent — A2A Server
Exposes a fully A2A-compliant endpoint for the Finance Agent track.
"""
import argparse
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

from executor import Executor


def main():
    parser = argparse.ArgumentParser(description="AgentBeats Finance Purple Agent")
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9009)
    parser.add_argument("--card-url", type=str, help="Public URL for agent card")
    args = parser.parse_args()

    skills = [
        AgentSkill(
            id="financial_analysis",
            name="Financial Analysis",
            description=(
                "Analyze stocks, compute financial ratios (P/E, EV/EBITDA, DCF), "
                "assess company fundamentals, and provide investment insights."
            ),
            tags=["finance", "stocks", "valuation", "ratios", "analysis"],
            examples=[
                "What is the P/E ratio of Apple?",
                "Perform a DCF valuation for a company with $10M FCF growing at 15%.",
                "Analyze the financial health of Tesla based on these metrics.",
            ],
        ),
        AgentSkill(
            id="risk_assessment",
            name="Risk Assessment",
            description=(
                "Evaluate portfolio risk, compute VaR, Sharpe ratio, beta, "
                "and provide risk-adjusted return analysis."
            ),
            tags=["risk", "portfolio", "var", "sharpe", "beta"],
            examples=[
                "Calculate the Sharpe ratio for a portfolio with 12% return and 8% volatility.",
                "What is the Value at Risk for a $100K portfolio at 95% confidence?",
                "Assess the risk profile of a 60/40 stock/bond portfolio.",
            ],
        ),
        AgentSkill(
            id="market_data",
            name="Market Data & Research",
            description=(
                "Retrieve and analyze market data, economic indicators, "
                "sector trends, and macroeconomic context."
            ),
            tags=["market", "data", "research", "macro", "sectors"],
            examples=[
                "What are the current trends in the semiconductor sector?",
                "How does inflation affect bond prices?",
                "Compare the performance of growth vs value stocks in 2024.",
            ],
        ),
        AgentSkill(
            id="portfolio_optimization",
            name="Portfolio Optimization",
            description=(
                "Optimize portfolio allocation using Modern Portfolio Theory, "
                "efficient frontier analysis, and rebalancing strategies."
            ),
            tags=["portfolio", "optimization", "allocation", "mpt", "rebalancing"],
            examples=[
                "Optimize a portfolio of AAPL, MSFT, GOOGL for maximum Sharpe ratio.",
                "What is the efficient frontier for these 5 assets?",
                "How should I rebalance a portfolio that has drifted from 60/40?",
            ],
        ),
        AgentSkill(
            id="business_process",
            name="Business Process & Transaction Analysis",
            description=(
                "Analyze business transactions, financial statements, "
                "cash flow modeling, and process optimization."
            ),
            tags=["business", "transactions", "cash-flow", "statements", "process"],
            examples=[
                "Analyze this income statement and identify key concerns.",
                "Model the cash flow impact of a $5M equipment purchase.",
                "What are the financial implications of this M&A transaction?",
            ],
        ),
    ]

    agent_card = AgentCard(
        name="Finance Purple Agent",
        description=(
            "A zero-latency financial reasoning engine for the AgentBeats Finance track. "
            "Combines chain-of-thought financial analysis with structured tool use for "
            "stock valuation, risk assessment, portfolio optimization, and market research. "
            "Built by mgnlia for the Berkeley RDI AgentX competition."
        ),
        url=args.card_url or f"http://{args.host}:{args.port}/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=skills,
    )

    request_handler = DefaultRequestHandler(
        agent_executor=Executor(),
        task_store=InMemoryTaskStore(),
    )
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    uvicorn.run(server.build(), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
