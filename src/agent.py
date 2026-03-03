"""
AgentBeats Finance Purple Agent — Core Reasoning Engine

Chain-of-thought financial reasoning with structured tool use.
Handles: stock valuation, risk assessment, portfolio optimization,
market research, business process analysis.
"""
import os
import json
import math
from typing import Any

from a2a.server.tasks import TaskUpdater
from a2a.types import Message, TaskState, Part, TextPart
from a2a.utils import get_message_text, new_agent_text_message

from openai import AsyncOpenAI
from tools import FINANCE_TOOLS, execute_tool

# ---------------------------------------------------------------------------
# System prompt — financial domain expert with CoT reasoning
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert financial analyst and portfolio manager with deep expertise in:
- Equity valuation (DCF, comparable companies, precedent transactions)
- Financial statement analysis (income statement, balance sheet, cash flow)
- Risk assessment (VaR, Sharpe ratio, beta, correlation analysis)
- Portfolio optimization (Modern Portfolio Theory, efficient frontier)
- Macroeconomic analysis and sector research
- Options pricing and derivatives
- Fixed income analysis
- M&A transaction analysis
- Business process and operational finance

## Reasoning Protocol
Always use structured chain-of-thought reasoning:
1. **Understand**: Parse the question — what financial concept is being tested?
2. **Identify**: What data/formulas/frameworks are needed?
3. **Calculate**: Show your work step-by-step with explicit formulas
4. **Validate**: Sanity-check results against market norms
5. **Conclude**: Provide a clear, actionable answer

## Tool Use
Use the available tools when you need:
- `calculate`: Any mathematical computation (always use for numbers)
- `search_market_data`: Current market prices, rates, indices
- `financial_ratios`: Standard ratio computations
- `dcf_valuation`: Discounted cash flow models
- `risk_metrics`: VaR, Sharpe, beta calculations
- `portfolio_optimizer`: Mean-variance optimization

## Output Format
- Lead with the direct answer
- Show all calculations explicitly
- Use financial notation (%, $, x for multiples)
- Flag assumptions clearly
- Provide context (industry benchmarks, historical norms)

Be precise, quantitative, and professional. Show your math."""


class FinanceAgent:
    """
    A2A-compliant Finance Purple Agent.
    Uses OpenAI GPT-4o with function calling for structured financial reasoning.
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = os.environ.get("OPENAI_MODEL", "gpt-4o")
        self.conversation_history: list[dict] = []

    async def run(self, message: Message, updater: TaskUpdater) -> None:
        """Main entry point — process a financial query with CoT + tool use."""
        input_text = get_message_text(message)

        await updater.update_status(
            TaskState.working,
            new_agent_text_message("🔍 Analyzing your financial query..."),
        )

        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": input_text})

        # Run the agentic loop with tool use
        response_text = await self._run_agent_loop(updater)

        # Add assistant response to history
        self.conversation_history.append({"role": "assistant", "content": response_text})

        # Emit final artifact
        await updater.add_artifact(
            parts=[Part(root=TextPart(text=response_text))],
            name="financial_analysis",
        )

    async def _run_agent_loop(self, updater: TaskUpdater) -> str:
        """
        Agentic loop: LLM → tool calls → LLM → ... → final answer.
        Max 8 iterations to prevent runaway loops.
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *self.conversation_history,
        ]

        for iteration in range(8):
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=FINANCE_TOOLS,
                tool_choice="auto",
                temperature=0.1,  # Low temp for precise financial calculations
                max_tokens=4096,
            )

            choice = response.choices[0]
            msg = choice.message

            # No tool calls — we have our final answer
            if not msg.tool_calls:
                return msg.content or "Analysis complete."

            # Process tool calls
            messages.append(msg.model_dump(exclude_unset=True))

            tool_results = []
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                try:
                    fn_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    fn_args = {}

                await updater.update_status(
                    TaskState.working,
                    new_agent_text_message(f"⚙️ Running {fn_name}..."),
                )

                result = await execute_tool(fn_name, fn_args)
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": json.dumps(result),
                })

            messages.extend(tool_results)

        # Fallback: ask for final synthesis without tools
        messages.append({
            "role": "user",
            "content": "Please provide your final analysis based on the information gathered.",
        })
        final = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=4096,
        )
        return final.choices[0].message.content or "Analysis complete."
