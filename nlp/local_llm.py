"""Local-LLM scaffolding for the Arm 2 NLP components (IMPROVEMENT_PLAN §9).

**Model-agnostic.** The active model is one configured GGUF (repo + revision +
filename), chosen by the ``LOCAL_LLM_MODEL`` env var, so swapping models — for
the Step-0a two-model pilot or a later swap — is one env change, no code edit.

**Hard scope rule (§9): this module is used ONLY by the two NLP components**
(datetime parser Arm 2, entity extractor Arm 2). It is never imported by the
agent loop or the renderer. ``tests/unit/test_local_llm_scope_guard.py``
enforces this structurally.

Design notes:
- ``llama_cpp`` and ``huggingface_hub`` are imported **lazily** (inside
  functions) so this module imports cleanly even when ``llama-cpp-python`` is
  not installed — the deterministic-parser unit tests mock :func:`generate`
  and never touch the native library.
- **Lazy load + process-lifetime singleton:** the GGUF is pulled once via
  ``hf_hub_download`` and the ``Llama`` instance is cached per model key. Never
  loaded at import.
- **GBNF-constrained, tag-shaped generation:** the grammar guarantees the
  output *structure* is valid; the caller parses the tags deterministically and
  normalises to the common contract (so the inline-tag format never leaks into
  the cross-arm comparison — see ARCHITECTURE Decision Log).
- Every :func:`generate` call records **real wall-clock ms** (distinct from the
  *simulated* latency KPI in EVALUATION_FRAMEWORK §9) so the pilot can report
  per-call CPU cost — the demo-viability data point.
"""

from __future__ import annotations

import os
import statistics
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:  # import only for type checkers; never at runtime import
    from llama_cpp import Llama, LlamaGrammar


@dataclass(frozen=True)
class ModelSpec:
    """A pinned GGUF model. ``revision`` pins the exact HF commit for repro.

    ``chat_format=None`` means "use the chat template embedded in the GGUF
    metadata" — the correct path for both Qwen2.5 and Llama-3.2 GGUFs, which
    ship their template. Set a string only to override.
    """

    key: str
    repo_id: str
    filename: str
    revision: str
    license: str
    chat_format: str | None = None


# Pilot models (IMPROVEMENT_PLAN §9 + Step 0a). Both Q4_K_M (~2 GB each).
# Revisions verified against the HF API at plan time.
MODELS: Final[dict[str, ModelSpec]] = {
    "qwen2.5-3b": ModelSpec(
        key="qwen2.5-3b",
        repo_id="Qwen/Qwen2.5-3B-Instruct-GGUF",
        filename="qwen2.5-3b-instruct-q4_k_m.gguf",
        revision="7dabda4d13d513e3e842b20f0d435c732f172cbe",
        license="Apache-2.0",
    ),
    "llama-3.2-3b": ModelSpec(
        key="llama-3.2-3b",
        repo_id="bartowski/Llama-3.2-3B-Instruct-GGUF",
        filename="Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        revision="5ab33fa94d1d04e903623ae72c95d1696f09f9e8",
        license="Llama-3.2-Community",
    ),
}

# The two-model pilot (2026-06-03) chose **Llama-3.2-3B** over Qwen2.5-3B — it
# breaks the Swiss-vague en_de wall and does not false-fire on hard negatives the
# way Qwen does (see ARCHITECTURE Decision Log + report §4.3e). The default is the
# chosen model so a plain ``nlp_arm2`` run reproduces the shipped Arm 2; Qwen
# remains selectable via ``LOCAL_LLM_MODEL=qwen2.5-3b`` for the pilot comparison.
DEFAULT_MODEL_KEY: Final[str] = "llama-3.2-3b"

# Deterministic extraction defaults.
_N_CTX: Final[int] = 4096
_SEED: Final[int] = 0
_TEMPERATURE: Final[float] = 0.0

# Process-lifetime caches.
_INSTANCES: dict[str, "Llama"] = {}
_GRAMMARS: dict[str, "LlamaGrammar"] = {}
_CALL_TIMINGS_MS: list[float] = []


def active_model_key() -> str:
    """Return the configured model key (``LOCAL_LLM_MODEL`` env, else default)."""
    key = os.environ.get("LOCAL_LLM_MODEL", DEFAULT_MODEL_KEY).strip()
    if key not in MODELS:
        raise ValueError(
            f"unknown LOCAL_LLM_MODEL: {key!r}. Legal values: {sorted(MODELS)}."
        )
    return key


def active_model_spec() -> ModelSpec:
    """Return the :class:`ModelSpec` for the configured active model."""
    return MODELS[active_model_key()]


def _model_path(spec: ModelSpec) -> str:
    """Download (cached) the GGUF and return its local path. Never commits it."""
    from huggingface_hub import hf_hub_download

    return hf_hub_download(
        repo_id=spec.repo_id,
        filename=spec.filename,
        revision=spec.revision,
    )


def get_model(key: str | None = None) -> "Llama":
    """Return the process-lifetime ``Llama`` singleton for ``key`` (lazy load).

    The GGUF is pulled once via ``hf_hub_download`` and the model is loaded on
    first use — never at import. CPU-only by default (matches the deployment
    story); inference is on the order of seconds per call.
    """
    key = key or active_model_key()
    if key not in MODELS:
        raise ValueError(f"unknown model key: {key!r}. Legal values: {sorted(MODELS)}.")
    if key not in _INSTANCES:
        from llama_cpp import Llama

        spec = MODELS[key]
        _INSTANCES[key] = Llama(
            model_path=_model_path(spec),
            n_ctx=_N_CTX,
            n_threads=os.cpu_count(),
            seed=_SEED,
            chat_format=spec.chat_format,
            verbose=False,
        )
    return _INSTANCES[key]


def compile_grammar(gbnf: str) -> "LlamaGrammar":
    """Compile a GBNF grammar string into a ``LlamaGrammar`` (needs llama_cpp)."""
    from llama_cpp import LlamaGrammar

    return LlamaGrammar.from_string(gbnf, verbose=False)


def _grammar(gbnf: str) -> "LlamaGrammar":
    """Compile-and-cache a grammar by its source string."""
    if gbnf not in _GRAMMARS:
        _GRAMMARS[gbnf] = compile_grammar(gbnf)
    return _GRAMMARS[gbnf]


def generate(
    prompt: str,
    gbnf: str,
    *,
    max_tokens: int = 256,
    system: str | None = None,
    key: str | None = None,
) -> str:
    """Grammar-constrained chat completion → decoded text.

    ``gbnf`` is the grammar *source* (compiled and cached internally), so the
    NLP arms call ``generate(prompt, GBNF_STRING, ...)`` and the unit tests mock
    exactly this one function. Deterministic (temperature 0). Records real
    wall-clock ms in the module timing buffer (see :func:`timing_summary`).
    """
    model = get_model(key)
    grammar = _grammar(gbnf)

    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    start = time.perf_counter()
    result = model.create_chat_completion(
        messages=messages,
        grammar=grammar,
        max_tokens=max_tokens,
        temperature=_TEMPERATURE,
    )
    _CALL_TIMINGS_MS.append((time.perf_counter() - start) * 1000.0)

    return result["choices"][0]["message"].get("content") or ""


def reset_timings() -> None:
    """Clear the per-call timing buffer (call before a measured eval run)."""
    _CALL_TIMINGS_MS.clear()


def timing_summary() -> dict[str, float]:
    """Mean/median/total/count of real wall-clock per-call inference time (ms).

    This is the *real* CPU cost — distinct from the simulated latency KPI in
    EVALUATION_FRAMEWORK §9. The pilot reports it as the demo-viability /
    cost-of-privacy data point; it must never feed model selection.
    """
    if not _CALL_TIMINGS_MS:
        return {"count": 0.0, "mean_ms": 0.0, "median_ms": 0.0, "total_ms": 0.0}
    return {
        "count": float(len(_CALL_TIMINGS_MS)),
        "mean_ms": statistics.fmean(_CALL_TIMINGS_MS),
        "median_ms": statistics.median(_CALL_TIMINGS_MS),
        "total_ms": float(sum(_CALL_TIMINGS_MS)),
    }
