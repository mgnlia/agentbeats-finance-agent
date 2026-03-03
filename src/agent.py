import json
from a2a.server.tasks import TaskUpdater
from a2a.types import Message, TaskState, Part, TextPart
from a2a.utils import get_message_text, new_agent_text_message

from messenger import Messenger
from prompts import FINANCE_SYSTEM_PROMPT
from financial_tools import TOOLS_SCHEMA, dispatch_tool
from config import LLM_PROVIDER, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, GROQ_API_KEY, GROQ_MODEL


def _get_llm_client():
    """Return configured LLM client based on provider setting."""
    if LLM_PROVIDER == "groq" and GROQ_API_KEY:
        from groq import Groq
        return "groq", Groq(api_key=GROQ_API_KEY), GROQ_MODEL
    else:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        return "openai", client, OPENAI_MODEL


class Agent:
    def __init__(self):
        self.messenger = Messenger()
        self.provider, self.client, self.model = _get_llm_client()

    async def run(self, message: Message, updater: TaskUpdater) -> None:
        """Run the Finance Agent with CoT reasoning and tool use.

        Args:
            message: Incoming A2A message with financial task
            updater: Report progress and results back to AgentBeats
        """
        input_text = get_message_text(message)

        await updater.update_status(
            TaskState.working,
            new_agent_text_message("Analyzing financial task...")
        )

        messages = [
            {"role": "system", "content": FINANCE_SYSTEM_PROMPT},
            {"role": "user", "content": input_text},
        ]

        # Agentic loop: run until no more tool calls
        max_iterations = 5
        for iteration in range(max_iterations):
            await updater.update_status(
                TaskState.working,
                new_agent_text_message(f"Reasoning step {iteration + 1}...")
            )

            response = self._call_llm(messages)
            response_message = response.choices[0].message

            # Check for tool calls
            if hasattr(response_message, "tool_calls") and response_message.tool_calls:
                # Append assistant message with tool calls
                messages.append({
                    "role": "assistant",
                    "content": response_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                        }
                        for tc in response_message.tool_calls
                    ],
                })

                # Execute each tool call
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        tool_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        tool_args = {}

                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(f"Using tool: {tool_name}")
                    )

                    tool_result = dispatch_tool(tool_name, tool_args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result,
                    })
            else:
                # No tool calls — final answer reached
                final_answer = response_message.content or "No response generated."

                # Try to parse as JSON for structured output
                try:
                    parsed = json.loads(final_answer)
                    output_text = json.dumps(parsed, indent=2)
                except (json.JSONDecodeError, TypeError):
                    output_text = final_answer

                await updater.add_artifact(
                    parts=[Part(root=TextPart(text=output_text))],
                    name="FinanceAnalysis",
                )
                return

        # Max iterations reached — return last response
        last_content = messages[-1].get("content", "Analysis incomplete after max iterations.")
        await updater.add_artifact(
            parts=[Part(root=TextPart(text=str(last_content)))],
            name="FinanceAnalysis",
        )

    def _call_llm(self, messages: list) -> object:
        """Call LLM with tool support."""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "tools": TOOLS_SCHEMA,
            "tool_choice": "auto",
            "temperature": 0.1,  # Low temp for financial precision
        }
        if self.provider == "groq":
            return self.client.chat.completions.create(**kwargs)
        else:
            return self.client.chat.completions.create(**kwargs)
