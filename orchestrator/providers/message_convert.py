"""Message-format conversion between Gemini Content objects and Claude messages.

The orchestrator stores history in Gemini's Content format as the canonical
representation. When the active provider is Claude, this module converts on
the fly so the rest of the pipeline doesn't need to know two formats.

Known limitation: Gemini has no tool_use_id concept, so we synthesise
deterministic ids from the function name and a counter. Multiple parallel
tool calls in the same turn may misalign — see Decision Log 2026-03-22.
"""

import json


def gemini_messages_to_claude(messages: list) -> list[dict]:
    """Convert Gemini Content objects to Claude message format.

    Handles:
    - User text messages       -> {"role": "user", "content": "text"}
    - Model text responses     -> {"role": "assistant", "content": "text"}
    - Function calls           -> {"role": "assistant", "content": [{"type": "tool_use", ...}]}
    - Function results         -> {"role": "user", "content": [{"type": "tool_result", ...}]}
    """
    claude_messages: list[dict] = []
    # Track tool_use_ids: Claude needs matching IDs between tool_use and tool_result.
    # Gemini doesn't have IDs, so we generate deterministic ones from the function name
    # and a counter.
    _tool_id_counter = 0

    for msg in messages:
        if not hasattr(msg, "role") or not hasattr(msg, "parts"):
            continue  # skip non-Content objects

        if msg.role == "user":
            text_parts: list[str] = []
            tool_results: list[dict] = []
            for part in msg.parts:
                if hasattr(part, "function_response") and part.function_response:
                    fn_name = part.function_response.name
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": f"tool_{fn_name}_{_tool_id_counter}",
                        "content": json.dumps(part.function_response.response, default=str),
                    })
                    _tool_id_counter += 1
                elif hasattr(part, "text") and part.text:
                    text_parts.append(part.text)

            if tool_results:
                claude_messages.append({"role": "user", "content": tool_results})
            elif text_parts:
                claude_messages.append({"role": "user", "content": "\n".join(text_parts)})

        elif msg.role == "model":
            content_blocks: list[dict] = []
            for part in msg.parts:
                if hasattr(part, "function_call") and part.function_call:
                    fn_name = part.function_call.name
                    content_blocks.append({
                        "type": "tool_use",
                        "id": f"tool_{fn_name}_{_tool_id_counter}",
                        "name": fn_name,
                        "input": dict(part.function_call.args) if part.function_call.args else {},
                    })
                elif hasattr(part, "text") and part.text and not getattr(part, "thought", False):
                    content_blocks.append({"type": "text", "text": part.text})
            if content_blocks:
                claude_messages.append({"role": "assistant", "content": content_blocks})

    return claude_messages
