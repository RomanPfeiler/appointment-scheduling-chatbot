"""Smoke test: is the Gemini API key valid and the model reachable?"""
import os

import pytest
from dotenv import load_dotenv

load_dotenv()


def test_gemini_api_key_set():
    """GEMINI_API_KEY must be present and non-empty."""
    key = os.getenv("GEMINI_API_KEY", "")
    assert key, "GEMINI_API_KEY is not set — check your .env file"
    assert len(key) > 20, f"GEMINI_API_KEY looks too short: {key[:6]}..."
    print(f"[OK] GEMINI_API_KEY is set ({key[:6]}...)")


def test_gemini_connection():
    """Send a minimal request to Gemini and verify a non-empty text response."""
    from google import genai
    from google.genai import types

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)
    # thinking_budget=0: gemini-2.5-flash thinks by default, and a tiny
    # max_output_tokens budget can be consumed entirely by thought parts,
    # leaving content.parts empty (the documented empty-parts failure mode).
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Reply with exactly the word: OK",
        config=types.GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=50,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )

    # Project rule: never assume parts[0] — scan all parts, skip thought parts.
    parts = response.candidates[0].content.parts or []
    text = next(
        (p.text for p in parts if getattr(p, "text", None) and not getattr(p, "thought", False)),
        "",
    ).strip()
    assert text, "Gemini returned an empty response"
    print(f"[OK] Gemini responded: {text!r}")


if __name__ == "__main__":
    test_gemini_api_key_set()
    test_gemini_connection()
    print("All checks passed.")
