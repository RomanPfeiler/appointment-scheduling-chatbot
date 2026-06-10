"""Provider abstraction package.

Re-exports the public surface so callers can `from orchestrator.providers
import LLMResult, call_gemini, gemini_messages_to_claude` without knowing the
internal layout.

``call_claude`` is intentionally NOT re-exported here: the Claude provider is
retained as code (report's provider-independent design + the evaluation used
it) but is no longer user-facing, and it pulls in the ``anthropic`` SDK. Keeping
its import lazy means the deployed Gemini-only app (and its module-load import
graph) never imports ``anthropic``. Import it at the call site when needed:
``from orchestrator.providers.claude import call_claude``.

Adding a new provider: create providers/<name>.py exposing a `call_<name>()`
that returns LLMResult, then add it to the imports + __all__ below.
"""

from orchestrator.providers.base import LLMResult
from orchestrator.providers.gemini import call_gemini
from orchestrator.providers.message_convert import gemini_messages_to_claude

__all__ = ["LLMResult", "call_gemini", "gemini_messages_to_claude"]
