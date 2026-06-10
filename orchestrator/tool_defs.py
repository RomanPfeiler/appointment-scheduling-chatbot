"""LLM tool declarations mirroring the MCP tool contract.

Contains both Gemini FunctionDeclaration objects and Claude-format tool dicts.
"""

from google.genai import types


# ---------------------------------------------------------------------------
# Claude tool definitions (JSON Schema format)
# ---------------------------------------------------------------------------

CLAUDE_TOOLS: list[dict] = [
    {
        "name": "get_appointment_topics",
        "description": (
            "Get the list of available appointment topics "
            "(e.g., Investing, Mortgage, Pension)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_appointment_contact_medium",
        "description": (
            "Get available contact media (e.g., Branch Meeting, Online Meeting, Phone) "
            "for a given topic. Some media may not be available for all topics."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic_id": {
                    "type": "string",
                    "description": "The topic identifier (e.g. 'investing', 'mortgage', 'pension').",
                }
            },
            "required": ["topic_id"],
        },
    },
    {
        "name": "check_availability",
        "description": (
            "Check available appointment slots within a date range. "
            "Returns all free slots. Maximum range is 3 days per call. "
            "All datetimes must include timezone (default: Europe/Zurich)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic_id": {
                    "type": "string",
                    "description": "The topic identifier.",
                },
                "contact_medium_id": {
                    "type": "string",
                    "description": "The contact medium identifier (e.g. 'branch', 'online', 'phone').",
                },
                "start_datetime": {
                    "type": "string",
                    "description": (
                        "Start of the search window in ISO 8601 format with timezone "
                        "(e.g. '2026-03-20T08:00:00+01:00')."
                    ),
                },
                "end_datetime": {
                    "type": "string",
                    "description": (
                        "End of the search window in ISO 8601 format with timezone. "
                        "Must be within 3 days of start_datetime."
                    ),
                },
            },
            "required": ["topic_id", "contact_medium_id", "start_datetime", "end_datetime"],
        },
    },
    {
        "name": "book_appointment",
        "description": (
            "Book an appointment for the specified topic, contact medium, and time slot. "
            "Only book slots that were confirmed available via check_availability."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic_id": {
                    "type": "string",
                    "description": "The topic identifier.",
                },
                "contact_medium_id": {
                    "type": "string",
                    "description": "The contact medium identifier.",
                },
                "datetime_start": {
                    "type": "string",
                    "description": "Appointment start time in ISO 8601 format.",
                },
                "datetime_end": {
                    "type": "string",
                    "description": "Appointment end time in ISO 8601 format.",
                },
            },
            "required": ["topic_id", "contact_medium_id", "datetime_start", "datetime_end"],
        },
    },
]


# ---------------------------------------------------------------------------
# Gemini tool declarations
# ---------------------------------------------------------------------------


def get_tool_declarations() -> types.Tool:
    """Return a ``types.Tool`` containing all 4 bookable appointment tools.

    ``reset_bookings`` is intentionally excluded — it is for testing only.
    The declarations mirror the MCP Tool Contract in ARCHITECTURE.md Section 5.
    """
    return types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="get_appointment_topics",
                description=(
                    "Get the list of available appointment topics "
                    "(e.g., Investing, Mortgage, Pension)."
                ),
                parameters={},
            ),
            types.FunctionDeclaration(
                name="get_appointment_contact_medium",
                description=(
                    "Get available contact media (e.g., Branch Meeting, Online Meeting, Phone) "
                    "for a given topic. Some media may not be available for all topics."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "topic_id": {
                            "type": "string",
                            "description": "The topic identifier (e.g. 'investing', 'mortgage', 'pension').",
                        }
                    },
                    "required": ["topic_id"],
                },
            ),
            types.FunctionDeclaration(
                name="check_availability",
                description=(
                    "Check available appointment slots within a date range. "
                    "Returns all free slots. Maximum range is 3 days per call. "
                    "All datetimes must include timezone (default: Europe/Zurich)."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "topic_id": {
                            "type": "string",
                            "description": "The topic identifier.",
                        },
                        "contact_medium_id": {
                            "type": "string",
                            "description": "The contact medium identifier (e.g. 'branch', 'online', 'phone').",
                        },
                        "start_datetime": {
                            "type": "string",
                            "description": (
                                "Start of the search window in ISO 8601 format with timezone "
                                "(e.g. '2026-03-20T08:00:00+01:00')."
                            ),
                        },
                        "end_datetime": {
                            "type": "string",
                            "description": (
                                "End of the search window in ISO 8601 format with timezone. "
                                "Must be within 3 days of start_datetime."
                            ),
                        },
                    },
                    "required": ["topic_id", "contact_medium_id", "start_datetime", "end_datetime"],
                },
            ),
            types.FunctionDeclaration(
                name="book_appointment",
                description=(
                    "Book an appointment for the specified topic, contact medium, and time slot. "
                    "Only book slots that were confirmed available via check_availability."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "topic_id": {
                            "type": "string",
                            "description": "The topic identifier.",
                        },
                        "contact_medium_id": {
                            "type": "string",
                            "description": "The contact medium identifier.",
                        },
                        "datetime_start": {
                            "type": "string",
                            "description": "Start of the appointment slot in ISO 8601 format.",
                        },
                        "datetime_end": {
                            "type": "string",
                            "description": "End of the appointment slot in ISO 8601 format.",
                        },
                    },
                    "required": ["topic_id", "contact_medium_id", "datetime_start", "datetime_end"],
                },
            ),
        ]
    )
