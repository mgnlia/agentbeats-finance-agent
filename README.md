# AgentBeats Finance Agent

A2A-protocol compliant Finance Agent for the [AgentX–AgentBeats Sprint 1](https://rdi.berkeley.edu/agentx-agentbeats.html) competition (Berkeley RDI).

**Prize pool**: Lambda $5K/$3K/$1K cash + OpenAI $10K/$5K/$1K credits  
**Deadline**: March 22, 2026

## Capabilities

- Stock valuation analysis (P/E, EV/EBITDA, comparable analysis)
- Portfolio risk assessment (concentration, HHI, diversification score)
- Financial ratio calculation (20+ metrics)
- Financial Q&A with chain-of-thought reasoning
- Tool-augmented reasoning loop (up to 5 iterations)

## Quick Start

```bash
# Install
uv sync

# Configure
cp .env.example .env
# Edit .env: set OPENAI_API_KEY

# Run
uv run src/server.py --host 0.0.0.0 --port 9009
```

## Docker

```bash
docker build -t agentbeats-finance-agent .
docker run -p 9009:9009 -e OPENAI_API_KEY=sk-... agentbeats-finance-agent
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `openai` | `openai` or `groq` |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o` | Model name |
| `OPENAI_BASE_URL` | OpenAI default | Override for local Ollama |
| `GROQ_API_KEY` | — | Groq fallback key |
| `AGENT_PORT` | `9009` | Server port |

## A2A Compliance

Agent card at `/.well-known/agent.json`. Supports streaming. Built on [a2a-sdk](https://github.com/google-a2a/a2a-python).

## Testing

```bash
uv sync --extra test
uv run pytest tests/
```
