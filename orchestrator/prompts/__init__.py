"""Prompt loading helper.

Prompts live as `.md` files in this directory so they're easy to A/B, version,
diff in code review, and paste verbatim into the report. Loading is cached per
process — restart Chainlit to pick up edits during iteration.
"""

from functools import lru_cache
from pathlib import Path

_PROMPT_DIR = Path(__file__).parent


@lru_cache(maxsize=None)
def load_prompt(name: str) -> str:
    """Load a prompt file by stem (e.g. ``"appointment_assistant"``).

    Args:
        name: Filename without the ``.md`` extension.

    Returns:
        The prompt body with surrounding whitespace stripped.

    Raises:
        FileNotFoundError: If no matching ``.md`` file exists.
    """
    path = _PROMPT_DIR / f"{name}.md"
    return path.read_text(encoding="utf-8").strip()
