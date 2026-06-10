"""Bidirectional NLP ⟷ agent scope guard — enforced by code, not convention.

The NLP layer and the agent loop keep deliberately separate Gemini access (the
agent loop's ``orchestrator/providers/gemini.py`` vs the NLP-extraction client
``nlp/api_llm.py``), and the local LLM (``nlp/local_llm.py``) is NLP-only
(IMPROVEMENT_PLAN §9). These tests fail loudly if that boundary ever blurs:

- **agent → NLP**: the agent loop / executor / providers must not import ``nlp.*``
  (covers ``nlp.local_llm`` and ``nlp.api_llm`` via the blanket ``nlp.*`` match).
- **NLP client reach**: ``nlp.local_llm`` / ``nlp.api_llm`` are imported only by
  their respective Arm-2 / Arm-3 modules — plus the **evaluation runner**, which
  reads the model *key* accessor (``active_model_key``) to make each record
  self-describing about which GGUF produced it. The runner imports the config
  accessor only, never the runtime (``get_model`` / ``generate``); a focused check
  enforces that, so this exception does not reopen the §9 runtime boundary (the
  agent path remains barred from ``nlp.*`` entirely by the first test).
- **NLP → agent**: the NLP LLM-client helpers must not import the agent provider
  stack or the agent nodes.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

_IMPORTS_NLP = re.compile(r"^\s*(from\s+nlp[\s.]|import\s+nlp\b)", re.MULTILINE)
_IMPORTS_LOCAL_LLM = re.compile(
    r"from\s+nlp\s+import\s+local_llm"
    r"|from\s+nlp\.local_llm\s+import"
    r"|import\s+nlp\.local_llm"
)
_IMPORTS_API_LLM = re.compile(
    r"from\s+nlp\s+import\s+api_llm"
    r"|from\s+nlp\.api_llm\s+import"
    r"|import\s+nlp\.api_llm"
)
# The agent loop's reasoning/provider stack — the NLP client helpers must not
# import any of it (the reverse direction of the §9 boundary).
_IMPORTS_AGENT_STACK = re.compile(
    r"from\s+orchestrator\.providers"
    r"|import\s+orchestrator\.providers"
    r"|from\s+orchestrator\.nodes\.agent\s+import"
    r"|import\s+orchestrator\.nodes\.agent"
)


def test_agent_execute_providers_do_not_import_nlp():
    """The agent loop, executor, and providers never touch ``nlp.*``."""
    targets = [
        REPO / "orchestrator" / "nodes" / "agent.py",
        REPO / "orchestrator" / "nodes" / "execute.py",
    ]
    targets += sorted((REPO / "orchestrator" / "providers").glob("*.py"))
    offenders = [
        str(p.relative_to(REPO))
        for p in targets
        if _IMPORTS_NLP.search(p.read_text(encoding="utf-8"))
    ]
    assert not offenders, (
        f"agent/execute/providers must not import nlp.* (§9 hard scope): {offenders}"
    )


def test_local_llm_imported_only_by_the_two_nlp_arms():
    """``nlp.local_llm`` reaches only the two Arm-2 modules + the eval runner.

    The runner is the evaluation harness (it already builds the arms via
    ``nlp.factory``); it reads the model-key accessor to make records
    self-describing, never the runtime — :func:`test_runner_imports_local_llm_key_accessor_only`
    enforces that.
    """
    allowed = {
        (REPO / "nlp" / "datetime_parsers" / "arm2_local_llm.py").resolve(),
        (REPO / "nlp" / "entity_extractors" / "arm2_local_llm.py").resolve(),
        (REPO / "evaluation" / "runner.py").resolve(),
    }
    self_module = (REPO / "nlp" / "local_llm.py").resolve()
    importers: set[Path] = set()
    for p in REPO.rglob("*.py"):
        rp = p.resolve()
        if "tests" in rp.parts or rp == self_module:
            continue  # tests legitimately import it to test it
        if _IMPORTS_LOCAL_LLM.search(rp.read_text(encoding="utf-8")):
            importers.add(rp)
    assert importers == allowed, (
        "nlp.local_llm must be reachable only from the two NLP arms + the runner; "
        f"unexpected importers: {sorted(str(p) for p in importers - allowed)}"
    )


def test_runner_imports_local_llm_key_accessor_only():
    """The runner reads the config accessor, never the local-LLM *runtime*.

    Keeps the §9 boundary tight: the harness may record which model is configured
    (``active_model_key`` / ``active_model_spec``) but must not pull in the GGUF
    loader or the inference call (``get_model`` / ``generate``).
    """
    src = (REPO / "evaluation" / "runner.py").read_text(encoding="utf-8")
    forbidden = re.findall(r"local_llm\.(get_model|generate)\b", src)
    forbidden += re.findall(
        r"from\s+nlp\.local_llm\s+import\s+[^\n]*\b(get_model|generate)\b", src
    )
    assert not forbidden, (
        "runner.py may use only the local_llm config accessors, "
        f"not the runtime: {forbidden}"
    )


def test_api_llm_imported_only_by_the_two_nlp_arms():
    """``nlp.api_llm`` reaches only the two Arm-3 modules + the eval runner.

    The runner exception mirrors the ``local_llm`` one: it reads the model
    accessor (``active_model``) so api-arm records are self-describing about the
    pinned NLP-extraction model (ARCHITECTURE §8 2026-06-10), never the client
    or the inference call — :func:`test_runner_imports_api_llm_model_accessor_only`
    enforces that.
    """
    allowed = {
        (REPO / "nlp" / "datetime_parsers" / "arm3_api_llm.py").resolve(),
        (REPO / "nlp" / "entity_extractors" / "arm3_api_llm.py").resolve(),
        (REPO / "evaluation" / "runner.py").resolve(),
    }
    self_module = (REPO / "nlp" / "api_llm.py").resolve()
    importers: set[Path] = set()
    for p in REPO.rglob("*.py"):
        rp = p.resolve()
        if "tests" in rp.parts or rp == self_module:
            continue  # tests legitimately import it to test it
        if _IMPORTS_API_LLM.search(rp.read_text(encoding="utf-8")):
            importers.add(rp)
    assert importers == allowed, (
        "nlp.api_llm must be reachable only from the two NLP arms + the runner; "
        f"unexpected importers: {sorted(str(p) for p in importers - allowed)}"
    )


def test_runner_imports_api_llm_model_accessor_only():
    """The runner reads the api_llm config accessor, never the client/runtime.

    Symmetric to :func:`test_runner_imports_local_llm_key_accessor_only`: the
    harness may record which Gemini model the Arm 3 extraction is pinned to
    (``active_model``) but must not pull in the client builder or the inference
    call (``get_client`` / ``generate_json``).
    """
    src = (REPO / "evaluation" / "runner.py").read_text(encoding="utf-8")
    forbidden = re.findall(r"api_llm\.(get_client|generate_json)\b", src)
    forbidden += re.findall(
        r"from\s+nlp\.api_llm\s+import\s+[^\n]*\b(get_client|generate_json)\b", src
    )
    assert not forbidden, (
        "runner.py may use only the api_llm config accessor, "
        f"not the client/runtime: {forbidden}"
    )


def test_nlp_llm_clients_do_not_import_agent_stack():
    """Reverse direction: the NLP LLM-client helpers never import the agent stack."""
    targets = [
        REPO / "nlp" / "api_llm.py",
        REPO / "nlp" / "local_llm.py",
    ]
    offenders = [
        str(p.relative_to(REPO))
        for p in targets
        if _IMPORTS_AGENT_STACK.search(p.read_text(encoding="utf-8"))
    ]
    assert not offenders, (
        "nlp LLM clients must not import the agent provider stack / agent nodes: "
        f"{offenders}"
    )
