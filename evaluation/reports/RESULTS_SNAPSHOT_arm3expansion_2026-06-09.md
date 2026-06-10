# Pinned Results Snapshot — Arm 3 NLP × Executor Expansion (combined, 2026-06-09)

> **Frozen artifact.** The report and defense draw the "does NLP add value on top of
> expansion?" numbers from this file, not from a live recompute. Generated from the
> reduced-representative combined run (commit `4eadd22`), judged, and paired against three
> anchors per EVALUATION_FRAMEWORK §10. Paired JSON/MD:
> `evaluation/reports/paired/arm3expansion_vs_{expansion,arm3,baseline}.{json,md}`.
> Raw per-run records live under `evaluation/runs/nlp_arm3_expansion/…` (gitignored).

## What this is

The **complementary-vs-redundant** experiment. Arm 3 NLP (Gemini JSON-mode datetime +
entity preprocessing, annotate node) and the executor window-expansion policy
(`orchestrator/expansion.py`, execute node) were each validated in isolation; this measures
the **combination**. Question: does better *upfront* datetime parsing make the agent's first
`check_availability` correct more often, so the deterministic widening ladder fires **less**
(complementary) — or does the ladder already rescue over-narrow windows, so the parsing buys
little (redundant)? **The discriminating metric is the ladder-fire rate, not booking** (NLP's
booking effect is a known, well-powered null).

## Configuration

- **Candidate (combined):** `20260608_221848__nlp_arm3_expansion__4eadd22__representative_reduced`
  — `nlp_datetime_enabled=nlp_entity_enabled=True`, `datetime_arm=entity_arm=api_llm`,
  `nlp_llm_backend=api`, **and** `expansion_policy_enabled=True`. New `nlp_arm3_expansion`
  stage (commit `4eadd22`). The two flag families are orthogonal (annotate node vs execute
  node; disjoint keys) — confirmed by unit tests + a clean smoke (Arm 3 annotated 60/61
  user-turns, ladder fired and persisted, no interference).
- **Anchors (all reused; no re-runs):**
  - **Primary** — expansion-only `20260607_164034__expansion__927f9c2__representative_reduced`.
    Validity: expansion code path is **byte-identical** `927f9c2`→`4eadd22` (only reports/CSV
    changed), so the shared expansion behaviour cancels in the pairing.
  - **Secondary A** — nlp_arm3 `20260606_234404__nlp_arm3__e1626fa__representative_reduced`
    (expansion's effect *with NLP on*; valid — adding the combined stage left the Arm 3 path
    unchanged).
  - **Secondary B** — baseline `20260606_205242__baseline__e1626fa__representative_reduced`
    (full stack vs plain baseline; valid — expansion is a proven no-op when its flag is False).
- **Profile:** `representative_reduced` (fixed `include_ids`) — 60 scenarios
  {T1:5, T2:5, T3:10, T4:10, T5:10, T6:10, T7:10} × reps 2 = **120 conversations**,
  13 `booking_reachable=false`. Identical selection across all runs → paired.
- **Knobs (match every anchor):** Gemini 2.5 Flash, temp 0.7, **agent `thinking_budget=-1`
  (thinking ON — the actual standing config; see ARCHITECTURE §8 2026-03-22 correction)**;
  max_turns 12; simulate_latency True (base 400 / per-day 500 / jitter σ 50 ms); pinned clock
  `reference_date=2026-06-01` (`get_current_datetime` returned `2026-06-01T12:00:00+02:00`);
  runaway guard `--scenario-timeout-s 600`. Judge: Gemini 2.5 Flash, T=0.3, judge_reps=1,
  **120/120 scored, 0 failures**.
- **Run health:** 120 records, **0 runaway timeouts, 0 error terminations** (booked 79,
  max_turns 21, refusal_accepted 20). Primary paired n=119 (the 1 excluded pair is the
  expansion anchor's pre-existing transient-API record).

## ⚠ Ladder-fire rate is a PROXY here

The discriminating metric is `ladder_fire_turns` = count of turns with ≥2 recorded
`check_availability` calls (the executor's widening ladder ran after an empty first call),
derived from raw `turns[].tool_calls` so it is computable on **both** the anchor and the
combined run. It is **biased low**: a ladder step served from the per-session availability
cache issues no MCP call, so it leaves no `ToolCallRecord`. The cache confound is **symmetric**
across the two expansion-on arms compared here (Primary), so the *directional difference*
stays informative even though absolute counts are understated. The clean per-turn signal
(`TurnRecord.ladder_steps`) is now persisted **going forward** (this run carries it in 99/120
records) but the expansion anchor predates it and cannot be retrofitted, so the **paired**
metric uses the proxy on both sides. (Roman's call, 2026-06-08 — confirmatory polish, no
anchor re-run.)

## Headline — Primary paired deltas (n=119, **arm3+expansion − expansion-only**)

`*` p<0.05, `**` p<0.01, `***` p<0.001 (Wilcoxon for continuous/judge; McNemar for binary).

| Metric | expansion-only | +Arm 3 | Δ [95% CI] | p |
|---|---:|---:|---:|---:|
| **ladder_fire_turns / conv** *(proxy, the discriminator)* | 1.70 | 1.50 | −0.19 [−0.54, 0.13] | 0.43 |
| Simulated latency (ms) / conv | 12,995 | 11,988 | −1,007 [−7,459, 5,135] | 0.44 |
| Dead-end turns / conv | 1.42 | 1.23 | −0.19 [−0.70, 0.30] | 0.60 |
| Turn count | 5.69 | 5.38 | −0.31 [−0.87, 0.24] | 0.26 |
| Efficiency ratio | 4.88 | 4.81 | −0.07 [−2.12, 2.07] | 0.79 |
| Availability calls / conv | 8.97 | 9.07 | +0.09 [−3.66, 4.10] | 0.62 |
| Extrinsic parse accuracy | 0.45 | 0.46 | +0.01 [−0.06, 0.09] | 0.83 |
| Unsupported facts / conv | 0.46 | 0.28 | −0.18 [−0.60, 0.20] | 0.57 |
| **Booking %** | 65.5 | 66.4 | +0.8pp [−5.0, 6.7] | 1.00 |
| Faithful % | 92.4 | 94.1 | +1.7pp [−4.2, 7.6] | 0.79 |
| Judge: Temporal | 4.44 | 4.36 | −0.08 | 0.46 |
| Judge: Negotiation | 3.76 | 3.73 | −0.02 | 0.78 |
| Judge: Conv-Efficiency | 3.77 | 3.73 | −0.04 | 0.65 |
| Judge: Customer-Experience | 3.73 | 3.68 | −0.05 | 0.61 |
| Judge: Recovery | 3.75 | 3.77 | +0.02 | 0.99 |

**Every metric is n.s. — a clean, well-powered wash.** All point estimates lean *faintly*
complementary (ladder −0.19, latency −1.0 s, dead-ends −0.19, unsupported facts −0.18,
faithful +1.7 pp), but none reach significance. **Verdict: redundancy** — the deterministic
ladder already rescues over-narrow windows, so Arm 3's better upfront parsing does not change
how often it fires.

## The interaction (NLP's marginal effect, with vs without expansion)

| Comparison | dead-ends | turns | Negotiation | CX | ladder-fire | booking |
|---|---|---|---|---|---|---|
| **NLP marginal, expansion ON** (Primary: arm3+exp − exp) | −0.19 n.s. | −0.31 n.s. | −0.02 n.s. | −0.05 n.s. | −0.19 n.s. | +0.8pp n.s. |
| **NLP marginal, expansion OFF** (known: arm3 − baseline) | n.s. | n.s. | n.s. | n.s. | (n/a) | +0.8pp n.s. |
| **Expansion's effect, NLP ON** (Sec A: arm3+exp − arm3) | **−1.95\*\*\*** | **−1.21\*\*\*** | **+0.64\*\*\*** | **+0.30\*** | **+0.75\*\*\*** | +6.7pp (0.13) |
| **Full stack − baseline** (Sec B: arm3+exp − baseline) | **−1.88\*\*\*** | **−0.93\*\*** | **+0.42\*** | **+0.33\*** | **+0.73\*\*\*** | +3.3pp (0.45) |

**Reading:** NLP's marginal effect is a null whether expansion is on or off → **independent /
redundant**. Expansion's significant wins replicate whether NLP is on (Sec A) or off
(expansion-vs-baseline 2026-06-07) → **expansion is the sole active ingredient**; the full
stack vs baseline (Sec B) just reproduces expansion-vs-baseline (dead-ends −1.88\*\*\*,
Negotiation/CX up, latency cost +1.97 s\*, booking n.s.).

## Watch-items — both resolved benign

- **T5 faithfulness (the carried watch-item).** Expansion-alone regressed Tier-5 faithful
  100→80%; **adding Arm 3 on top moves it 80→90%** (n.s., McNemar p=0.69) — Arm 3 does **not**
  worsen multi-round faithfulness and directionally *improves* it (structured slot values give
  the agent real availability to quote instead of fabricating). No new fabrication pathway.
- **The lone whisper of complementarity:** Tier-5 (multi-round) `ladder_fire_turns`
  **−0.70, p=0.064** — the one place better upfront parsing trends toward fewer ladder fires,
  but it does not reach significance. Everything else is flat per-tier.

## Conclusion

**Arm 3 NLP adds no measurable value on top of the executor expansion policy — redundancy,
not complementarity.** The discriminating ladder-fire rate is statistically flat (proxy
1.70→1.50, p=0.43), and every deterministic KPI, booking, faithfulness, and all five judge
dimensions are a clean wash. This extends the project's standing finding: NLP recognition
gains do not convert end-to-end, and **even on the single metric where NLP could plausibly aid
the expansion policy** (a correct first query so the ladder fires less), it does not move the
needle. **Ship stance unchanged: NLP OFF; the expansion policy is the agentic-strategy lever.**
Booking remained directional / n.s. throughout, as the brief predicted.
