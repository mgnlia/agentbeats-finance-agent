import os
from dotenv import load_dotenv

load_dotenv()

# LLM provider: "openai" (default) or "groq"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# OpenAI / OpenAI-compatible (e.g. local Ollama)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Groq fallback
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Server
AGENT_HOST = os.getenv("AGENT_HOST", "127.0.0.1")
AGENT_PORT = int(os.getenv("AGENT_PORT", "9009"))
