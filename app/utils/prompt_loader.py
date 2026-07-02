"""Utility for loading agent prompt templates from markdown files."""

import functools
from pathlib import Path

# Resolve the project root (two levels up from this file: utils/ → app/ → project root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


@functools.lru_cache(maxsize=None)
def load_prompt(agent_name: str) -> str:
    """Load and return the prompt content for the given agent.

    Prompts are stored as Markdown files under ``app/prompts/{agent_name}.md``.
    Loaded prompts are cached so repeated calls for the same agent are free.

    Args:
        agent_name: Name of the agent whose prompt to load (e.g. ``"admission"``).

    Returns:
        The raw string content of the prompt file.

    Raises:
        FileNotFoundError: If the prompt file does not exist.
    """
    prompt_path = _PROJECT_ROOT / "app" / "prompts" / f"{agent_name}.md"
    return prompt_path.read_text(encoding="utf-8")
