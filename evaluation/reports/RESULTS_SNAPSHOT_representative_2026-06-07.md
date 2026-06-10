# Pinned Results Snapshot — Representative Evaluation (2026-06-07)

> **Frozen artifact.** The report and defense draw their headline numbers from this
> file, not from a live recompute. Generated from the four reduced-representative
> runs below (commit `e1626fa`), judged, and paired per EVALUATION_FRAMEWORK §10.
> Raw per-run records live under `evaluation/runs/<stage>/…` (gitignored); the paired
> JSON/MD are in `evaluation/reports/paired/`.

## Configuration

- **Profile:** `representative_reduced` — 60 scenarios (T1–2 5/tier, T3–7 10/tier) ×
  reps 2 = **120 conversations/stage**, seed-42-derived `include_ids`, 13
  `booking_reachable=false` cases preserved (T2×1, T3×2, T7×10). Identical selection
  across all four stages (paired).
- **Commit:** `e1626fa` (clock override + next-week-calque fix + runaway guard all in).
- **Runs:**
  - baseline `20260606_205242__baseline__e1626fa__representative_reduced`
  - nlp_arm1 `20260606_222357__nlp_arm1__e1626fa__representative_reduced`
  - nlp_arm3 `20260606_234404__nlp_arm3__e1626fa__representative_reduced`
  - nlp_arm2 `20260607_014848__nlp_arm2__e1626fa__representative_reduced` (`local_llm_model=llama-3.2-3b`)
- **max_turns 12; scenario wall-clock guard** 600s (1200s for Arm 2). Judge: Gemini
  2.5 Flash, T=0.3, reps=1, 120/120 scored per stage, 0 failures.

## Headline KPIs (per stage, n=120)

| Stage | Booked | Median turns | Faithful | Dead-ends (tot / per-conv) | Mean parse (extrinsic) |
|---|---|---|---|---|---|
| **Baseline** (Gemini only) | 62.5% | 5.0 | 95% | 378 / 3.1 | 0.41 |
| **Arm 1** (spaCy + dateparser) | 63.3% | 5.0 | 94% | 375 / 3.1 | 0.43 |
| **Arm 3** (Gemini JSON) | 59.2% | 6.0 | 94% | 387 / 3.2 | 0.46 |
| **Arm 2** (local Llama-3.2-3B) | 54.2% | 6.0 | 96% | 404 / 3.4 | 0.48 |

### Judge means (1–5; Negotiation/CustExp null on Tier 7, Recovery T3–5 only)

| Stage | Temporal | Negotiation | Efficiency | Customer Exp | Recovery |
|---|---|---|---|---|---|
| Baseline | 4.60 | 3.38 | 3.73 | 3.33 | 3.48 |
| Arm 1 | 4.23 | 3.14 | 3.60 | 3.32 | 3.43 |
| Arm 3 | 4.58 | 3.15 | 3.62 | 3.36 | 3.46 |
| Arm 2 | 4.43 | 2.91 | 3.37 | 3.09 | 3.05 |

## Paired statistics — each arm vs corrected baseline (primary, n=120)

`*` p<0.05, `**` p<0.01 (Wilcoxon for continuous/judge; McNemar for booked/faithful).

| Δ vs baseline | Arm 1 | Arm 3 | Arm 2 |
|---|---|---|---|
| Booked | +0.8% (p=1.0) | −3.3% (p=0.52) | −7.6% (p=0.15) |
| Turn count | −0.06 (p=0.99) | +0.28 (p=0.15) | **+0.79 (p=0.017\*)** |
| Efficiency ratio | −0.30 (p=0.71) | +1.73 (p=0.55) | **+4.45 (p=0.016\*)** |
| Parse accuracy | +0.03 (p=0.47) | +0.06 (p=0.14) | +0.06 (p=0.10) |
| Faithful | −0.8% (p=1.0) | −0.8% (p=1.0) | +0.8% (p=1.0) |
| Unsupported facts | −0.28 (p=0.70) | −0.15 (p=0.75) | −0.36 (p=0.28) |
| Judge Temporal | **−0.37 (p=0.002\*\*)** | −0.02 (p=0.80) | −0.18 (p=0.13) |
| Judge Negotiation | −0.20 (p=0.19) | −0.17 (p=0.27) | **−0.45 (p=0.005\*\*)** |
| Judge Efficiency | −0.12 (p=0.25) | −0.11 (p=0.46) | **−0.38 (p=0.007\*\*)** |
| Judge Customer Exp | −0.01 (p=0.91) | +0.03 (p=0.92) | −0.25 (p=0.073) |
| Judge Recovery | −0.04 (p=0.73) | −0.02 (p=0.95) | **−0.42 (p=0.029\*)** |

## Paired statistics — arm vs arm (secondary, n≈120)

- **Arm 3 vs Arm 1 (datetime: API vs classical):** parse +0.04 (p=0.32, n.s.), booked
  −4.2% (p=0.33, n.s.), and **judge Temporal +0.35 [0.13, 0.58], p=0.004\*\***. **Do NOT
  cite this as "Arm 3 dominates Arm 1 on temporal understanding"** — it is the *mirror
  image* of the contaminated Arm-1 −0.37 (same Tier-7 rubric-blindness + judge
  clock-confound + `judge_reps=1` artifacts; see the mechanism follow-up below). The
  trustworthy deterministic parse signal does **not** separate them (Arm 3 0.46 vs Arm 1
  0.43, n.s.). Provisional until the `judge_reps=3` reliability re-run.
- **Arm 2 vs Arm 3 (local vs API):** **parse accuracy identical 0.47 = 0.47 (Δ0.00,
  p=0.96)**, faithful +1.7% (n.s.), fewer unsupported facts — the **local 3B model
  matches Gemini on extraction** — but judge Negotiation −0.29 (p=0.036\*) and
  Efficiency −0.26 (p=0.026\*): the agentic turn-economy cost is the local arm's price,
  not extraction quality.

## What the representative scale confirmed vs the n=14 smoke

- **Held:** faithfulness high everywhere (94–96%); the **Llama Arm 2 is faithful**
  (debunks the Qwen-masquerade "94 unsupported facts"); the **Arm-3 `exact_time`
  defect is resolved** (dead-ends flat, no longer regressing).
- **Did not hold / softened:** the smoke's parse-accuracy "win" is **real intrinsically
  but does not reach significance extrinsically** (Δ+0.03…+0.06, all n.s.); booking does
  not improve for any arm.

## Headline finding (one line)

> **Structured NLP raises datetime-extraction accuracy monotonically (0.41→0.48) but
> does not improve the agent end-to-end at n≈120** — a clean, well-powered null/mixed
> result. Arm 2 *degrades* turn economy and negotiation/recovery (p<0.05); Arm 3 is a
> statistical wash; Arm 1 is a wash on the reliable metrics. Gemini's in-context
> planning already absorbs the structured hints' value.

## Mechanism follow-up (2026-06-07) — what the significant deltas actually mean

- **Arm 1 judge-Temporal −0.37 (p=0.002) is NOT a clean "Arm 1 hurts temporal" finding —
  do not cite it as one.** A mechanism audit (33 drops/70 ties/17 gains) found it is
  substantially *measurement*: **14/33 drops are identical-agent-query-different-judge-score**
  (single-judge inconsistency, `judge_reps=1`); **Tier 7 is the biggest contributor (−0.80)**
  because the datetime hint nudges the agent to *check availability* on out-of-scope recurring
  requests instead of refusing, and the Temporal rubric is **tier-blind on Tier 7**; and a
  **judge clock-confound** (the judge prompt has no date anchor and the transcript header leaks
  the real run date `2026-06-06`, so the judge penalises the agent's pinned-`reference_date`
  June-2 dates as "wrong vs June 9"). The **deterministic parse accuracy — the trustworthy
  temporal signal — is marginally *better* for Arm 1 (0.43 vs 0.41).** Net: Arm 1 is a wash on
  the reliable metrics; the choice of Arm 3 as default-when-enabled rests on "shares the agent's
  Gemini stack / no extra dependency", not on the (confounded) temporal dimension.
- **Arm 2 efficiency-ratio Δ: report +2.82 (p=0.036), not +4.45.** The headline +4.45 (p=0.016)
  is inflated by the 2 timeout-runaway scenarios; excluding them the robust effect is **+2.82**.
  All other Arm 2 significant effects survive exclusion (turns +0.76 p=0.022; judge Negotiation
  −0.45 p=0.006, Efficiency −0.36 p=0.009, Recovery −0.36 p=0.047).
- **Where Arm 2's blowup lives (motivates the expansion policy):** efficiency-ratio and the
  booking dip concentrate in the **negotiation/near-miss tiers** (T2 eff 6.3→18.3, booked
  50→30%; T5 3.0→9.1, 80→65%; T4 3.0→6.2, 90→75%) while Arm 2 *improves* the precise tier
  (T1 5.1→2.2, booked 70→90%). The over-narrow-window → call-blowup mechanism is the
  executor-side expansion policy's exact target.
- **Local-vs-API on-prem cost (Arm 2 vs Arm 3):** extraction *identical* (parse 0.47=0.47,
  p=0.96), but ~0.5 more turns/conv (p=0.08) + significantly worse judge Negotiation (−0.29,
  p=0.036) / Efficiency (−0.26, p=0.026), and **~8 h CPU inference / 120 conv (~20 s/call,
  ~8× the API arm's wall-clock)** — the genuine privacy-arm price, at no extraction-quality loss.
- **Judge reliability:** `judge_reps=1` → no within-record variance estimate exists; the
  judge-dimension deltas (esp. Temporal) should be re-validated with a `judge_reps=3` run on a
  ~20-scenario sample before any judge-dimension claim anchors the report.
- **Measurement gaps (not blocking):** Arm-3 extraction Gemini calls and the judge's own tokens
  are not captured in records (the recorder wraps only the agent provider); Arm-2 per-call local
  inference time is not persisted (`local_llm.timing_summary()` dies with the run process).

## Known caveats carried into Limitations

- **reps=2** (not 3) and a reduced 120-conv profile → wider CIs; lean on per-tier
  patterns, not just CI overlap.
- **Thin easy-tier `booking_reachable=false` coverage** (T1/T4/T5 drew 0; T2×1, T3×2).
- **en_de "next week Tuesday" calque fixtures** were mis-generated (today+7 vs today+8)
  and surgically patched (commit `e1626fa`); the ~2 reduced calque scenarios now align,
  but Arm 1 (which shares dateparser with the generator) could in principle get a
  spurious edge on such cases — immaterial here (Arm 1 showed no booking gain).
- **Single-judge** (Gemini), synthetic scenarios, residual simulator non-determinism,
  extrinsic (behaviour-based) NLP measurement.
- 1 Arm 2 conversation ended as a transient API `error` (excluded from its paired n=119).
</content>
