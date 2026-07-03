

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load .env from project root
load_dotenv()


def get_chat_model(temperature: float = 0, model: str | None = None) -> ChatOpenAI:
    """Return a configured ``ChatOpenAI`` instance.

    Automatically detects whether to use OpenAI directly or via
    OpenRouter based on available environment variables.

    Args:
        temperature: Sampling temperature (0 = deterministic).
        model: Model identifier override.

    Returns:
        A ready-to-use ``ChatOpenAI`` instance.
    """
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if openrouter_key:
        # Use OpenRouter as the LLM provider
        return ChatOpenAI(
            temperature=temperature,
            model=model or "openai/gpt-4o-mini",
            openai_api_key=openrouter_key,
            openai_api_base="https://openrouter.ai/api/v1",
        )
    elif openai_key:
        # Use OpenAI directly
        return ChatOpenAI(
            temperature=temperature,
            model=model or "gpt-4o-mini",
            openai_api_key=openai_key,
        )
    else:
        raise RuntimeError(
            "No LLM API key found. Set OPENROUTER_API_KEY or OPENAI_API_KEY "
            "in your .env file."
        )
