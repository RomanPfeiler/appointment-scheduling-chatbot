# LLM-as-a-Judge: Appointment Scheduling Evaluation

You are evaluating a recorded conversation between a bank customer and an
appointment-scheduling AI agent at a Swiss bank.

## Your Task

Score the **agent's** performance on the dimensions described below. For each
dimension assign an integer score from 1 to 5 and write exactly one sentence
explaining your score. Output **only** a JSON object — no markdown fences, no
preamble, no trailing text.

## Conversation Metadata

- **Scenario ID:** {scenario_id}
- **Tier:** {tier}
- **Persona profile:** {persona_profile}
- **Scenario description:** {scenario_description}

## Conversation Transcript

{transcript}

---

## Scoring Dimensions

### 1. Temporal Understanding (1–5)

Did the agent correctly interpret the user's time preferences throughout the
conversation?

- **5** — Queried exactly the right window on first attempt, acknowledged
  preferences accurately throughout
- **4** — Minor imprecision (e.g. queried slightly wider than needed) but
  demonstrated understanding
- **3** — Needed one clarification to get the time right
- **2** — Misinterpreted the time, required multiple corrections
- **1** — Fundamentally failed to understand the temporal expression

{negotiation_section}

### 3. Conversational Efficiency (1–5)

Did the agent minimise unnecessary turns?

- **5** — Combined information gathering naturally, never asked for information
  the user had already provided, no redundant API queries
- **4** — One unnecessary question or one slightly redundant API call
- **3** — Two unnecessary exchanges
- **2** — Multiple avoidable round-trips, asked for information the user had
  already given
- **1** — Conversation felt stuck in a loop, repeated questions

{customer_experience_section}

{recovery_section}

---

## Output Format

Respond with a JSON object exactly matching this schema. Do **not** include
markdown code fences or any other text outside the JSON.

```
{json_schema_description}
```
