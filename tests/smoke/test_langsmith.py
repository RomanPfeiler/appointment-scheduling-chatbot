"""Quick smoke test: is LangSmith configured and reachable?"""
import os

from dotenv import load_dotenv

load_dotenv()


def _get_either(primary: str, legacy: str) -> str:
    """Return the LANGSMITH_* value, falling back to the legacy LANGCHAIN_* name.

    The project convention is the ``LANGSMITH_*`` names (EU instance) — see
    CLAUDE.md and .env.example. The langsmith SDK itself accepts both name
    families, so the smoke test does too rather than failing a working setup.
    """
    return os.getenv(primary) or os.getenv(legacy) or ""


def test_langsmith_env_vars():
    """Check that the required env vars are set (LANGSMITH_* convention)."""
    tracing = _get_either("LANGSMITH_TRACING", "LANGCHAIN_TRACING_V2")
    assert tracing == "true", "LANGSMITH_TRACING (or legacy LANGCHAIN_TRACING_V2) not set"
    api_key = _get_either("LANGSMITH_API_KEY", "LANGCHAIN_API_KEY")
    assert api_key.startswith("lsv2_"), f"LangSmith API key doesn't look right: {api_key[:10]}..."
    project = _get_either("LANGSMITH_PROJECT", "LANGCHAIN_PROJECT")
    assert project == "appointment-chatbot", "LANGSMITH_PROJECT not set"
    assert os.getenv("LANGSMITH_ENDPOINT", "").startswith(
        "https://eu."
    ), "LANGSMITH_ENDPOINT should point at the EU instance"
    print("✅ All LangSmith env vars configured correctly")


def test_langsmith_connection():
    """Verify we can reach LangSmith API."""
    from langsmith import Client

    client = Client()
    # list_projects is a lightweight call — raises if key is invalid or network is down
    projects = list(client.list_projects(limit=1))
    print(f"✅ LangSmith connected. Found {len(projects)} project(s).")


if __name__ == "__main__":
    test_langsmith_env_vars()
    test_langsmith_connection()
