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
from config import AGENT_HOST, AGENT_PORT


def main():
    parser = argparse.ArgumentParser(description="AgentBeats Finance Agent — A2A Server")
    parser.add_argument("--host", type=str, default=AGENT_HOST)
    parser.add_argument("--port", type=int, default=AGENT_PORT)
    parser.add_argument("--card-url", type=str, help="Public URL for agent card")
    args = parser.parse_args()

    skill = AgentSkill(
        id="finance-analysis",
        name="Financial Analysis & Reasoning",
        description=(
            "Performs comprehensive financial analysis including stock valuation, "
            "portfolio risk assessment, financial ratio calculation, and financial Q&A. "
            "Uses chain-of-thought reasoning with structured tool calls for precise, "
            "quantitative answers."
        ),
        tags=["finance", "stocks", "portfolio", "risk", "valuation", "analysis"],
        examples=[
            "Analyze the valuation of AAPL given P/E of 28 and industry average of 22",
            "Assess the risk of a portfolio: 40% tech, 30% healthcare, 30% energy",
            "Calculate the Sharpe ratio for a fund with 12% return, 2% risk-free rate, 8% std dev",
            "What does a debt-to-equity ratio of 2.5 mean for a manufacturing company?",
        ],
    )

    agent_card = AgentCard(
        name="AgentBeats Finance Agent",
        description=(
            "A zero-latency financial reasoning agent built for the AgentX–AgentBeats "
            "Sprint 1 Finance track. Combines chain-of-thought LLM reasoning with "
            "structured financial tools (ratio calculator, stock analyzer, portfolio risk). "
            "A2A-protocol compliant, Docker-ready."
        ),
        url=args.card_url or f"http://{args.host}:{args.port}/",
        version="0.1.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=Executor(),
        task_store=InMemoryTaskStore(),
    )
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    print(f"Starting AgentBeats Finance Agent on {args.host}:{args.port}")
    uvicorn.run(server.build(), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
