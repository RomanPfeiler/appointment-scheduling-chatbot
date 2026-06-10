import json
import logging
import os
import traceback

import chainlit as cl
from chainlit.input_widget import Select, Slider, Switch
from dotenv import load_dotenv
from google import genai
from google.genai import types

# NOTE: evaluation.adhoc is imported lazily inside on_chat_start (local dev only).
# The always-on ad-hoc recorder is disabled on HF Spaces (ephemeral filesystem),
# so the deployed app never imports the evaluation/ package — keeping it off the
# public Space and out of the deployed image.
from orchestrator.expansion import AvailabilityCache
from orchestrator.graph import appointment_graph
from orchestrator.mcp_bridge import MCPBridge

load_dotenv(override=True)

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"

# Single source of truth for deployed-vs-local behaviour. ``SPACE_ID`` is set
# automatically on every Hugging Face Space at runtime; it is unset for local
# dev. This is the ONLY gate for HF-specific behaviour — reference this flag,
# never scatter os.getenv("SPACE_ID") checks. On HF we: suppress the local-LLM
# (Arm 2) NLP arm in the UI and server-side, and enforce a per-session message
# cap (the Space is public). Local dev keeps the full arm set and is uncapped.
IS_HF_SPACE = bool(os.getenv("SPACE_ID"))

# Public-demo per-session message cap (HF only). Protects the Gemini free quota.
DEMO_MESSAGE_CAP = 50

# Legacy disabled-option label. It is no longer offered in the Select widgets
# (2026-06-10 settings redesign — Chainlit cannot truly disable an option, so a
# selectable fake was confusing), but it is kept in _LOCAL_ARM_SELECTIONS so a
# stale session that still carries it is coerced safely server-side.
LOCAL_ARM_DISABLED_LABEL = "Local model (not available on hosted demo)"

# Datetime / entity arm options, environment-aware. Locally the full set is
# offered (Arm 2 stays demoable on your own machine); on HF the local_llm arm
# is dropped — the Select description explains why it is absent.
if IS_HF_SPACE:
    DATETIME_ARM_VALUES = ["dateparser", "api_llm"]
    ENTITY_ARM_VALUES = ["spacy", "api_llm"]
else:
    DATETIME_ARM_VALUES = ["dateparser", "local_llm", "api_llm"]
    ENTITY_ARM_VALUES = ["spacy", "local_llm", "api_llm"]

# Step-display verbosity (replaces the former binary Show_Debug_Steps switch).
# Level semantics: 0 = nothing; 1 = tool calls + smart availability search as
# one-line summaries; 2 = + truncated input/output payloads; 3 = + LLM
# decisions and NLP annotations. HF visitors default to the short summary;
# local dev defaults to full debug.
STEP_VERBOSITY_VALUES = ["Off", "Activity summary", "Tool calls", "Full debug"]
_VERBOSITY_LEVELS = {name: i for i, name in enumerate(STEP_VERBOSITY_VALUES)}
STEP_VERBOSITY_INITIAL_INDEX = 1 if IS_HF_SPACE else 3

# Selections that require the local GGUF model (the real value or its disabled
# UI label). On HF these are coerced to a safe non-local arm before any
# parser/extractor is built — the local model is never loaded on the Space.
_LOCAL_ARM_SELECTIONS = ("local_llm", LOCAL_ARM_DISABLED_LABEL)


def _wants_local_arm(settings: dict) -> bool:
    """True if either NLP arm setting points at the local-LLM (Arm 2) model.

    Used on HF to surface a one-line override notice in on_settings_update; the
    actual coercion happens in on_message before any parser/extractor is built.
    """
    return (
        settings.get("Datetime_Arm") in _LOCAL_ARM_SELECTIONS
        or settings.get("Entity_Arm") in _LOCAL_ARM_SELECTIONS
    )


def _safe_arm(arm: str | None, default: str) -> str:
    """Resolve a requested NLP arm to one allowed in the current environment.

    On HF, any local-LLM selection (the real value or the disabled UI label) is
    coerced to the safe non-local default so ``nlp.local_llm.get_model()`` is
    never reached and the GGUF is never pulled on the Space — defense in depth,
    independent of what the UI offered. Locally the requested arm is returned
    unchanged (Arm 2 stays demoable on your own machine).
    """
    if not arm:
        return default
    if IS_HF_SPACE and arm in _LOCAL_ARM_SELECTIONS:
        return default
    return arm

# The authoritative system prompt lives in orchestrator/prompts/appointment_assistant.md
# and is loaded by orchestrator/nodes/agent.py.

# TODO (post-deadline): word-by-word response streaming. It requires switching
# call_gemini to generate_content_stream and relaying token deltas through the
# graph — see reviews/UI_SETTINGS_PROPOSAL_2026-06-10.md §b. The settings
# toggle that promised it was removed 2026-06-10; the full agent->execute loop
# runs to completion before responding, then this turn's steps are rendered.


def _verbosity_level(settings: dict) -> int:
    """Map the Step_Verbosity setting to a numeric level (0=Off … 3=Full debug)."""
    return _VERBOSITY_LEVELS.get(settings.get("Step_Verbosity", "Off"), 0)


# Payload truncation for step display — slot lists can be large; the full data
# stays in debug_log, LangSmith, and the ad-hoc records.
_MAX_SLOTS_SHOWN = 8
_MAX_PAYLOAD_CHARS = 1500


def _truncate_payload(payload) -> str:
    """JSON-dump a tool payload, truncating long lists and oversized blobs."""
    if isinstance(payload, list) and len(payload) > _MAX_SLOTS_SHOWN:
        text = json.dumps(payload[:_MAX_SLOTS_SHOWN], indent=2, default=str)
        return f"{text}\n… and {len(payload) - _MAX_SLOTS_SHOWN} more"
    text = json.dumps(payload, indent=2, default=str)
    if len(text) > _MAX_PAYLOAD_CHARS:
        return text[:_MAX_PAYLOAD_CHARS] + "\n… (truncated)"
    return text


def _summarize_params(parameters: dict) -> str:
    """One-line ``key=value`` summary of tool parameters."""
    if not parameters:
        return "(no parameters)"
    return ", ".join(f"{k}={v}" for k, v in parameters.items())


def _summarize_tool_result(response) -> str:
    """One-line summary of a tool response (count, status, or error)."""
    if isinstance(response, list):
        return f"{len(response)} result(s)"
    if isinstance(response, dict):
        if response.get("status") == "error":
            return f"error: {str(response.get('message', ''))[:120]}"
        if "status" in response:
            return f"status: {response['status']}"
    return "ok"


def _ladder_step_line(step: dict) -> str:
    """Human-readable one-liner for one widening-ladder step."""
    if step.get("error"):
        return f"aborted: tool error after {step.get('mcp_calls', 0)} call(s)"
    window = step.get("window") or []
    span = f"{window[0][:10]} → {window[1][:10]}" if len(window) == 2 else "?"
    calls = step.get("mcp_calls", 0)
    source = "served from session cache, no API call" if calls == 0 else f"{calls} API call(s)"
    return f"{span}: {source}, {step.get('found', 0)} slot(s) found"


async def _render_debug_steps(records: list, level: int) -> None:
    """Render this turn's debug_log records as cl.Step blocks.

    Handles all four record vocabularies the graph emits: ``mcp_tool_call``,
    ``mcp_tool_call_expanded`` (the expansion policy — rendered as a parent
    step with one nested child per widening-ladder step), ``gemini_call``,
    and ``nlp_annotation``. Steps must be created BEFORE the final cl.Message
    so Chainlit nests them under the incoming user message.
    """
    if level <= 0:
        return
    for record in records:
        action = record.get("action", "unknown")
        details = record.get("details", {})

        if action == "mcp_tool_call":
            tool_name = details.get("tool_name", "unknown_tool")
            async with cl.Step(name=f"MCP: {tool_name}", type="tool") as step:
                if level >= 2:
                    step.input = _truncate_payload(details.get("parameters", {}))
                    step.output = _truncate_payload(details.get("response", {}))
                else:
                    step.input = _summarize_params(details.get("parameters", {}))
                    step.output = _summarize_tool_result(details.get("response"))

        elif action == "mcp_tool_call_expanded":
            # The expansion policy's check_availability — the showcase feature.
            # Render the widening ladder as nested child steps so the search
            # strategy is legible instead of an undifferentiated JSON dump.
            params = details.get("parameters", {})
            step0 = details.get("step0", {})
            ladder = details.get("ladder_steps") or []
            count = details.get("result_count")
            async with cl.Step(
                name="Smart availability search: check_availability", type="tool"
            ) as parent:
                parent.input = (
                    _truncate_payload(params) if level >= 2 else _summarize_params(params)
                )
                if isinstance(count, int):
                    if ladder:
                        parent.output = (
                            f"0 slots in the requested window — widened the "
                            f"search and found {count} slot(s) nearby"
                        )
                    elif step0.get("served_from_cache"):
                        parent.output = (
                            f"{count} slot(s) (served from session cache, no API call)"
                        )
                    else:
                        parent.output = f"{count} slot(s) in the requested window"
                else:
                    parent.output = "tool error"
                for ladder_step in ladder:
                    idx = ladder_step.get("step", "?")
                    async with cl.Step(name=f"Widening step {idx}", type="tool") as child:
                        child.output = _ladder_step_line(ladder_step)

        elif action == "gemini_call" and level >= 3:
            response_type = details.get("response_type", "unknown")
            step_name = f"Gemini -> {response_type}"
            if details.get("function_name"):
                step_name += f" ({details['function_name']})"
            async with cl.Step(name=step_name, type="llm") as step:
                step.input = f"Messages in context: {details.get('prompt_message_count', '?')}"
                step.output = _truncate_payload(
                    {k: v for k, v in details.items() if k != "prompt_message_count"}
                )

        elif action == "nlp_annotation" and level >= 3:
            async with cl.Step(name="NLP annotation", type="tool") as step:
                step.output = (
                    f"topic={details.get('topic')}, "
                    f"contact_medium={details.get('contact_medium')}, "
                    f"datetime ranges={details.get('n_ranges', 0)}"
                    + (" (compound)" if details.get("compound") else "")
                    + f" — arms: datetime={details.get('datetime_arm')}, "
                    f"entity={details.get('entity_arm')}"
                )


@cl.on_chat_start
async def on_chat_start():
    # 1. Settings panel — grouped: demo features, NLP experiment, developer.
    # (Redesigned 2026-06-10: dead widgets removed — Max_Output_Tokens and
    # System_Prompt_Mode were never wired to the graph, Streaming was a no-op —
    # and the binary Show_Debug_Steps switch became the Step_Verbosity select.)
    settings = await cl.ChatSettings(
        [
            # ── Demo features ──────────────────────────────────────────
            # Customer-facing toggle that drives the existing
            # `expansion_policy_enabled` flag (read in on_message, forwarded
            # via config["configurable"]). Internal flag name unchanged.
            # Default ON in production; the flag-off path stays available.
            Switch(
                id="Expansion_Policy",
                label="Smart availability search",
                initial=True,
                description=(
                    "When your requested time is fully booked, automatically "
                    "search nearby days and offer the closest alternatives "
                    "instead of replying 'nothing available'."
                ),
            ),
            Select(
                id="Step_Verbosity",
                label="Show agent activity",
                values=STEP_VERBOSITY_VALUES,
                initial_index=STEP_VERBOSITY_INITIAL_INDEX,
                description=(
                    "How much of the agent's inner working to show as "
                    "expandable steps: a short summary of tool calls and the "
                    "smart availability search, truncated payloads, or full "
                    "debug detail (LLM decisions + NLP annotations)."
                ),
            ),
            # ── NLP experiment (research toggles; IMPROVEMENT_PLAN §5) ──
            Switch(
                id="NLP_Datetime",
                label="NLP: datetime parser",
                initial=False,
                description=(
                    "Run the NLP datetime parser on each user message and "
                    "inject specificity hints into the agent prompt. Off = "
                    "baseline (Gemini handles datetime parsing alone)."
                ),
            ),
            Switch(
                id="NLP_Entity",
                label="NLP: entity extractor",
                initial=False,
                description=(
                    "Run the NLP entity extractor (topic + contact_medium). "
                    "Off = baseline."
                ),
            ),
            Select(
                id="Datetime_Arm",
                label="Datetime arm",
                values=DATETIME_ARM_VALUES,
                initial_index=0,
                description=(
                    "Which datetime arm to use when NLP: datetime is on. "
                    + (
                        "The local model (Arm 2) is not available on this hosted demo."
                        if IS_HF_SPACE
                        else "local_llm (Arm 2) runs a CPU GGUF model locally."
                    )
                ),
            ),
            Select(
                id="Entity_Arm",
                label="Entity arm",
                values=ENTITY_ARM_VALUES,
                initial_index=0,
                description=(
                    "Which entity arm to use when NLP: entity is on. "
                    + (
                        "The local model (Arm 2) is not available on this hosted demo."
                        if IS_HF_SPACE
                        else "local_llm (Arm 2) runs a CPU GGUF model locally."
                    )
                ),
            ),
            # ── Developer ──────────────────────────────────────────────
            Slider(
                id="Temperature",
                label="Temperature",
                initial=0.7,
                min=0,
                max=1,
                step=0.1,
                description=(
                    "Agent sampling temperature. 0.7 is the evaluated "
                    "configuration; lower = more deterministic."
                ),
            ),
        ]
    ).send()
    cl.user_session.set("settings", settings)

    # 2. Create Gemini client inside on_chat_start so HF Spaces secrets are available.
    # Gemini is the only user-facing LLM. The Claude provider is retained as code
    # (orchestrator/providers/claude.py) for the report's provider-independent design
    # and the evaluation, but it is no longer constructed or selectable here.
    gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    cl.user_session.set("gemini_client", gemini_client)

    # 3. Per-session message counter for the public-demo cap (HF only).
    cl.user_session.set("msg_count", 0)

    # 4. Create and connect the MCP bridge (one persistent connection per session).
    mcp_bridge = MCPBridge(server_script_path="mcp_server/server.py")
    await mcp_bridge.connect()
    cl.user_session.set("mcp_bridge", mcp_bridge)

    # 5. Initialise conversation state.
    initial_state = {
        "messages": [],
        "phase": "intent",
        "topic_id": None,
        "topic_name": None,
        "contact_medium_id": None,
        "contact_medium_name": None,
        "pending_tool_call": None,
        "tool_result": None,
        "turn_count": 0,
        "debug_log": [],
        "last_annotation": None,
    }
    cl.user_session.set("state", initial_state)

    # 5a. NLP layer caches — populated lazily in on_message when the
    # corresponding switch turns on. Avoids paying spaCy's model-load cost
    # for sessions that never enable the NLP layer.
    cl.user_session.set("_dt_parser_cache", None)
    cl.user_session.set("_dt_parser_arm", None)
    cl.user_session.set("_ent_extractor_cache", None)
    cl.user_session.set("_ent_extractor_arm", None)

    # 5a-bis. Per-session availability cache for the executor expansion policy.
    # Created once per chat so it persists across turns; only consulted when the
    # policy flag is on (default ON; turning it off restores the baseline path).
    cl.user_session.set("availability_cache", AvailabilityCache())

    # 5b. Always-on ad-hoc recorder — LOCAL DEV ONLY. Every local chat session
    # writes a JSON record + markdown transcript under evaluation/runs/adhoc/<run_id>/
    # (see architecture/EVALUATION_FRAMEWORK.md §7 and evaluation/README.md).
    # Disabled on HF Spaces: the Space filesystem is ephemeral (records would be
    # lost on every restart) AND importing evaluation.adhoc would force shipping
    # the whole evaluation/ package to the public Space. The lazy, gated import
    # keeps evaluation/ off the deployed boot path entirely. All recorder call
    # sites already guard for ``recorder is None``.
    recorder = None
    if not IS_HF_SPACE:
        try:
            from evaluation.adhoc import make_session_recorder

            recorder = make_session_recorder(
                session_id=cl.user_session.get("id") or "",
                provider="gemini",
                model=MODEL,
                temperature=settings.get("Temperature", 0.7),
            )
        except Exception as exc:  # pragma: no cover — recording must never break the chat
            logger.warning("Could not create ad-hoc recorder: %s", exc)
            recorder = None
    cl.user_session.set("recorder", recorder)

    # 6. Welcome message
    await cl.Message(
        content="Welcome to the Appointment Scheduler! How can I help you today?"
    ).send()


@cl.on_settings_update
async def on_settings_update(settings: dict):
    cl.user_session.set("settings", settings)
    # Settings are read from cl.user_session in on_message and forwarded via config.
    # No need to recreate any client or graph — they are stateless w.r.t. settings.
    expansion_on = settings.get("Expansion_Policy", True)
    verbosity = settings.get("Step_Verbosity", "Off")
    temp = settings.get("Temperature", 0.7)
    nlp_dt_label = (
        f"On ({settings.get('Datetime_Arm', 'dateparser')})"
        if settings.get("NLP_Datetime", False)
        else "Off"
    )
    nlp_ent_label = (
        f"On ({settings.get('Entity_Arm', 'spacy')})"
        if settings.get("NLP_Entity", False)
        else "Off"
    )

    # On the hosted demo, warn if a local-LLM arm was selected — it is overridden
    # server-side in on_message (the local model is never loaded on the Space).
    local_override_note = ""
    if IS_HF_SPACE and _wants_local_arm(settings):
        local_override_note = (
            "\n\n_Note: the local model is not available on this hosted demo — "
            "that arm is automatically overridden with the hosted default._"
        )

    await cl.Message(
        content=(
            f"Settings updated:\n"
            f"- **Smart availability search**: {'On' if expansion_on else 'Off'}\n"
            f"- **Show agent activity**: {verbosity}\n"
            f"- **NLP datetime parser**: {nlp_dt_label}\n"
            f"- **NLP entity extractor**: {nlp_ent_label}\n"
            f"- **Temperature**: {temp}"
            + local_override_note
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    state = cl.user_session.get("state")
    gemini_client = cl.user_session.get("gemini_client")
    mcp_bridge = cl.user_session.get("mcp_bridge")
    settings = cl.user_session.get("settings") or {}

    if state is None or gemini_client is None or mcp_bridge is None:
        await cl.Message(
            content="Session not ready. Please refresh the page and try again."
        ).send()
        return

    # Public-demo per-session message cap (HF only; local dev is uncapped).
    # Checked BEFORE any Gemini call so a capped session can't drain the free
    # quota further. The limit message itself is not counted.
    if IS_HF_SPACE:
        msg_count = cl.user_session.get("msg_count") or 0
        if msg_count >= DEMO_MESSAGE_CAP:
            await cl.Message(
                content=(
                    f"You've reached the demo limit for this session "
                    f"({DEMO_MESSAGE_CAP} messages). Thanks for trying the "
                    f"Appointment Scheduler!"
                )
            ).send()
            return
        cl.user_session.set("msg_count", msg_count + 1)

    try:
        # Gemini is the only user-facing provider (Claude retained as code only).
        provider = "gemini"

        # debug_log is an operator.add channel that accumulates across the whole
        # session (the full prior state is passed back into ainvoke below), so
        # only records beyond this index belong to the current turn. Without
        # this, every turn would re-display all previous turns' steps.
        prev_debug_len = len(state.get("debug_log", []))

        # Wrap the user's text as a Gemini Content object.
        user_content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=message.content)],
        )

        # operator.add only fires when a *node* returns an update dict — it does
        # NOT apply to the initial state passed to ainvoke().  So we must
        # manually prepend the full history here; passing just [user_content]
        # would throw away every prior message.
        graph_input = {**state, "messages": state["messages"] + [user_content]}

        recorder = cl.user_session.get("recorder")
        if recorder is not None:
            recorder.begin_turn(user_message=message.content)

        # NLP feature flags from settings panel. On HF, _safe_arm coerces any
        # local-LLM selection to a non-local default so the GGUF is never loaded
        # on the Space (defense in depth — independent of the UI options).
        nlp_dt_on = bool(settings.get("NLP_Datetime", False))
        nlp_ent_on = bool(settings.get("NLP_Entity", False))
        dt_arm = _safe_arm(settings.get("Datetime_Arm"), "dateparser")
        ent_arm = _safe_arm(settings.get("Entity_Arm"), "spacy")

        # Lazy-build parser/extractor on first use; rebuild when the arm
        # selection changes mid-session. Both are stashed in the session
        # so the spaCy model load (≈0.5–1 s) only happens once per arm.
        dt_parser = cl.user_session.get("_dt_parser_cache")
        if nlp_dt_on and (dt_parser is None or cl.user_session.get("_dt_parser_arm") != dt_arm):
            from nlp.factory import build_datetime_parser
            dt_parser = build_datetime_parser(dt_arm)
            cl.user_session.set("_dt_parser_cache", dt_parser)
            cl.user_session.set("_dt_parser_arm", dt_arm)

        ent_extractor = cl.user_session.get("_ent_extractor_cache")
        if nlp_ent_on and (ent_extractor is None or cl.user_session.get("_ent_extractor_arm") != ent_arm):
            from nlp.factory import build_entity_extractor
            ent_extractor = build_entity_extractor(ent_arm)
            cl.user_session.set("_ent_extractor_cache", ent_extractor)
            cl.user_session.set("_ent_extractor_arm", ent_arm)

        config = {
            "configurable": {
                "gemini_client": gemini_client,
                "mcp_bridge": mcp_bridge,
                "model": MODEL,
                "temperature": settings.get("Temperature", 0.7),
                "llm_provider": provider,
                "recorder": recorder,
                "nlp_datetime_enabled": nlp_dt_on,
                "nlp_entity_enabled": nlp_ent_on,
                "datetime_arm": dt_arm if nlp_dt_on else None,
                "entity_arm": ent_arm if nlp_ent_on else None,
                "_dt_parser": dt_parser if nlp_dt_on else None,
                "_ent_extractor": ent_extractor if nlp_ent_on else None,
                # Executor-side window-expansion policy — user-exposed via the
                # "Smart availability search" settings toggle, ON by default
                # (the representative-validated showcase feature). The per-session
                # cache is always provided; execute_node only consults it when on.
                "expansion_policy_enabled": bool(settings.get("Expansion_Policy", True)),
                "availability_cache": cl.user_session.get("availability_cache"),
            }
        }

        # Run the full agent->execute loop to completion.
        result_state = await appointment_graph.ainvoke(graph_input, config=config)

        # Persist updated state for the next turn.
        cl.user_session.set("state", result_state)

        # --- Observability: cl.Step display ---
        # Only THIS turn's records (the accumulated channel is sliced — see
        # prev_debug_len above). Steps must be created BEFORE the final
        # cl.Message so Chainlit nests them under the incoming user message.
        turn_debug_log = result_state.get("debug_log", [])[prev_debug_len:]
        await _render_debug_steps(turn_debug_log, _verbosity_level(settings))

        # --- Console debug dump (gated by DEBUG_LOG env var) ---
        if os.getenv("DEBUG_LOG", "false").lower() == "true":
            print("\n" + "=" * 60)
            print(f"DEBUG LOG — {len(turn_debug_log)} record(s) this turn")
            print("=" * 60)
            for i, rec in enumerate(turn_debug_log):
                print(f"\n[{i + 1}] {rec['node']} / {rec['action']} @ {rec['timestamp']}")
                print(json.dumps(rec["details"], indent=2, default=str))
            print("=" * 60 + "\n")

        # Extract the last model text response from the message history.
        agent_text = ""
        for content in reversed(result_state["messages"]):
            if hasattr(content, "role") and content.role == "model":
                for part in content.parts:
                    if hasattr(part, "text") and part.text and not getattr(part, "thought", False):
                        agent_text = part.text
                        break
            if agent_text:
                break

        if agent_text:
            await cl.Message(content=agent_text).send()
        else:
            # Graph ran to completion via ainvoke(), so an empty agent_text means
            # the final message has no usable text part (e.g. ended on a function_call).
            # Surface this loudly — it signals a prompt regression.
            last_msg = result_state["messages"][-1] if result_state["messages"] else None
            logger.warning(
                "Empty agent_text after graph completion — final state had no model text part. "
                "Last message role=%s parts=%s",
                getattr(last_msg, "role", None),
                [type(p).__name__ for p in getattr(last_msg, "parts", [])],
            )
            await cl.Message(content="I'm processing your request...").send()

        if recorder is not None:
            # Snapshot the state (recorder strips bulky ``messages`` itself).
            state_snapshot = {k: v for k, v in result_state.items() if k != "debug_log"}
            recorder.end_turn(agent_response=agent_text or None, state_snapshot=state_snapshot)

    except Exception as e:
        traceback.print_exc()
        recorder = cl.user_session.get("recorder")
        if recorder is not None:
            try:
                recorder.end_turn(agent_response=None, state_snapshot=None)
            except Exception:
                pass
        await cl.Message(
            content=(
                "Sorry, something went wrong while processing your request. "
                f"Please try again.\n\n*(Error: {e})*"
            )
        ).send()


@cl.on_chat_end
async def on_chat_end():
    """Clean up the MCP bridge and finalize the ad-hoc recorder."""
    recorder = cl.user_session.get("recorder")
    if recorder is not None:
        try:
            final_messages = []
            state = cl.user_session.get("state") or {}
            for msg in state.get("messages", []):
                if hasattr(msg, "model_dump"):
                    final_messages.append(msg.model_dump())
                elif hasattr(msg, "to_json_dict"):
                    final_messages.append(msg.to_json_dict())
                else:
                    final_messages.append({"role": getattr(msg, "role", None), "repr": repr(msg)})
            recorder.finalize(termination_reason="session_end", final_messages=final_messages)
        except Exception as exc:
            logger.warning("Recorder finalize failed: %s", exc)

    mcp_bridge = cl.user_session.get("mcp_bridge")
    if mcp_bridge and mcp_bridge.is_connected:
        await mcp_bridge.disconnect()
