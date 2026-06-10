# Pinned Results Snapshot — Executor Expansion Policy (2026-06-07)

> **Frozen artifact.** The report and defense draw the expansion-axis numbers from this
> file, not from a live recompute. Generated from the representative-reduced expansion run
> (commit `927f9c2`), judged, and paired against the corrected baseline anchor per
> EVALUATION_FRAMEWORK §10. Paired JSON/MD: `evaluation/reports/paired/expansion_vs_baseline.{json,md}`.
> Raw per-run records live under `evaluation/runs/expansion/…` (gitignored).

## What this is

The **third experiment axis**: not an NLP arm but a deterministic **executor-side
window-expansion policy** (`orchestrator/expansion.py`, behind `expansion_policy_enabled`),
tested with **NLP OFF** so the comparison `baseline vs baseline+expansion` isolates
*agentic-strategy gain* from *NLP gain*. Motivated by the NLP null: structured datetime
extraction climbed 0.41→0.48 intrinsically but gave no E2E gain; the mechanism audit
located the agent's real loss in the **negotiation tiers** (over-narrow `check_availability`
→ empty → unbounded LLM retry / call-blowup, e.g. Arm 2 T2 efficiency 6.3→18.3).

## Configuration

- **Candidate:** `20260607_164034__expansion__927f9c2__representative_reduced` —
  `expansion_policy_enabled=True`, all NLP flags OFF.
- **Baseline anchor (reused):** `20260606_205242__baseline__e1626fa__representative_reduced`.
  **Validity:** the executor is a proven no-op when the flag is off (flag-off byte-identical
  unit test), and `e1626fa`→`927f9c2` adds only the gated expansion code (+1 doc commit), so
  baseline behaviour is unchanged → the existing anchor is a valid paired control (no baseline
  re-run needed).
- **Profile:** `representative_reduced` (fixed `include_ids`) — 60 scenarios
  {T1:5, T2:5, T3:10, T4:10, T5:10, T6:10, T7:10} × reps 2 = **120 conversations**,
  13 `booking_reachable=false` retained (T2×1, T3×2, T7×10). Identical selection → paired.
- **Knobs (match the four arm runs):** Gemini 2.5 Flash, temp 0.7, thinking on; max_turns 12;
  simulate_latency True (base 400 / per-day 500 / jitter σ 50 ms); pinned clock
  `reference_date=2026-06-01`; runaway guard `--scenario-timeout-s 600`. Judge: Gemini 2.5
  Flash, T=0.3, judge_reps=1, 120/120 scored, 0 failures.
- **Run health:** 120 records, 0 failed, **0 runaway timeouts** (the cache + horizon clamp
  held at scale), 1 transient-API record excluded from the paired n=119.

## Headline — paired deltas (n=119, expansion − baseline)

`*` p<0.05, `**` p<0.01, `***` p<0.001 (Wilcoxon for continuous/judge; McNemar for binary).

| Metric | Baseline | Expansion | Δ [95% CI] | p |
|---|---|---|---|---|
| **Dead-end turns / conv** | 3.08 | **1.42** | **−1.66 [−2.30, −1.00]** | **<0.0001\*\*\*** |
| Turn count | 6.32 | 5.69 | −0.63 [−1.20, −0.06] | **0.012\*** |
| Booked | 63.0% | 65.5% | +2.5% [−4.2, 9.2] | 0.63 (**directional, n.s.**) |
| Efficiency ratio (mean) | 4.61 | 4.92 | +0.31 [−1.83, 2.51] | 0.16 (flat) |
| Simulated latency / conv | 10.0 s | 13.0 s | +2.95 s | **0.0001\*\*\*** (the cost) |
| Faithful | 95.0% | 92.4% | −2.5% | 0.61 (n.s.; see T5 watch-item) |
| Parse accuracy | 0.42 | 0.45 | +0.03 | 0.35 (n.s.; step-0 preserves agent window) |

### Judge dimensions (1–5; Negotiation/CX null on Tier 7; Recovery T3–5)

| Dim | Baseline | Expansion | Δ | p |
|---|---|---|---|---|
| **Negotiation effectiveness** | 3.36 | 3.78 | **+0.43** | **0.008\*\*** |
| **Customer experience** | 3.34 | 3.73 | **+0.38** | **0.008\*\*** |
| Recovery quality | 3.45 | 3.75 | +0.30 | 0.19 |
| Conversational efficiency | 3.74 | 3.77 | +0.03 | 0.82 |
| Temporal understanding | 4.60 | 4.44 | −0.16 | 0.15 (clock-confound caveat) |

## Per-tier (where the payoff concentrates — the negotiation tiers)

| Tier | Booking (b→c) | Efficiency (b→c) | Dead-ends/conv (b→c, p) | Faithful (b→c) |
|---|---|---|---|---|
| T1 direct | 70→80% | 5.10→3.20 | 2.5→1.3 (n.s.) | 90→100% |
| T2 near-miss | 50→40% | 6.30→8.20 | 5.3→2.9 (p=0.082) | 100→100% |
| **T3 day-shift** | **65→80%** | **8.65→3.62** | **3.95→1.35 (p=0.005\*\*)** | 100→90% |
| T4 broad | 90→85% | 2.95→4.26 | 3.35→1.45 (p=0.044\*) | 85→90% |
| **T5 multi-round** | 80→85% | 3.03→4.60 (p=0.014\*) | **4.55→1.75 (p=0.0015\*\*)** | **100→80% ⚠** |
| T6 other | 84→84% | 2.53→6.47 | 2.05→0.79 (p=0.027\*) | 89.5→100% |
| T7 refusal (guard) | **0→0% ✓** | — | 0.6→1.05 (n.s.) | 100→95% |

T3 (Negotiation +0.80 p=0.025, CX +0.75 p=0.020, Recovery +0.60 p=0.059) carries the judge win.

## Headline finding (one line)

> **The executor expansion policy is the first intervention in this project to move
> end-to-end agent quality significantly** — dead-end turns −54% (p<0.0001), turns −0.63
> (p=0.012), judge Negotiation +0.43 and Customer Experience +0.38 (both p=0.008),
> concentrated in the negotiation tiers — at a real, measured latency cost (+2.95 s/conv,
> p=0.0001) and a flat efficiency mean. **Booking is directional only (+2.5pp, n.s.).** A
> clean contrast to the NLP axis (recognition up, E2E null): moving one agentic decision
> (window/retry) into deterministic code moves the E2E UX metrics that NLP could not.

## Watch-items carried forward

1. **PRIMARY — Tier-5 faithfulness dip (100%→80%).** Overall faithful −2.5pp is n.s., but it
   concentrates in multi-round T5: the multi-day slot *surfacing* tempts the agent to
   extrapolate a fabricated availability grid (the real booking is still made; grounding
   catches the fabricated extras). The policy only ever returns real MCP slots — this is an
   agent-prompt / verifier guard to add before any wider rollout. **Must fix before default.**
2. **Tier-7 stray ladder.** The booking guard holds (0%→0%, zero fabrication; 0 timeouts), but
   on out-of-scope requests the agent's stray availability checks fire a harmless ladder →
   judge Conversational-Efficiency −0.70 (p=0.0155) and +8.5 s latency on T7. Needs an
   out-of-scope suppression signal that does **not** leak scenario ground-truth.
3. **Efficiency is a wash on the mean** — the policy tames the pathological tail (T3
   8.65→3.62) but adds calls on already-cheap tiers (T5 +1.57, p=0.014). Report it as
   "variance/tail reduction + latency cost," not an efficiency win.

## Caveats (carried into Limitations)

- reps=2, reduced 120-conv profile → wider CIs; lean on per-tier patterns over CI overlap.
- Single judge (Gemini), judge_reps=1 → no within-record variance; the Temporal dim carries
  the known clock-confound (real run-date leaks in the transcript header vs the pinned
  `reference_date`), so judge dims are **corroboration only** — the verdict rests on the
  deterministic dead-end/turn metrics.
- Synthetic scenarios, residual simulator non-determinism, extrinsic (behaviour-based)
  measurement; expansion tested with NLP OFF (orthogonal axis, not yet combined with an arm).

## Net stance

Ship behind the flag (off by default). **Fix the T5 surfacing-faithfulness and the Tier-7
stray ladder before considering it the default executor behaviour.** Combining expansion with
an NLP arm (e.g. Arm 3 datetime hints feeding a better first window) is the obvious next axis.
