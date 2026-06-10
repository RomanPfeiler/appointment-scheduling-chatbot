# KPI Summary — 20260608_221848__nlp_arm3_expansion__4eadd22__representative_reduced

**Stage:** nlp_arm3_expansion  **Commit:** `4eadd224731d6ca2e14bbdba907c056363f2f4ce`  **Note:** Arm 3 NLP (Gemini JSON) + executor expansion vs expansion-only; complementary-vs-redundant

Generated: 2026-06-08T23:56:01.808533Z  ·  60 scenarios  ·  120 records

## Headline KPIs

| KPI | Value |
|-----|-------|
| Booking completion rate | 65.8% |
| Median turns | 4.00 |
| Median efficiency ratio | 2.42 |
| Faithful rate | 94.2% |
| Mean simulated latency (ms) | 12040.7 |
| Mean parse accuracy | 0.46 |
| Dead-end turns total | 153 |
| Mean dead-end turns / conversation | 1.27 |

## Per-Tier Breakdown

| Tier | Records | Booking % | Median turns | Median eff. ratio | Faithful % | Mean parse acc. | Mean dead-ends |
|------|---------|-----------|--------------|-------------------|------------|-----------------|----------------|
| 1 | 10 | 80.0% | 2.00 | 1.00 | 100.0% | 0.50 | 1.30 |
| 2 | 10 | 70.0% | 2.50 | 2.00 | 100.0% | 0.70 | 0.90 |
| 3 | 20 | 65.0% | 4.00 | 2.50 | 95.0% | 0.45 | 2.40 |
| 4 | 20 | 95.0% | 4.00 | 2.00 | 90.0% | 0.40 | 1.05 |
| 5 | 20 | 85.0% | 6.00 | 2.67 | 90.0% | 0.45 | 0.95 |
| 6 | 20 | 75.0% | 4.00 | 3.25 | 90.0% | 0.40 | 1.65 |
| 7 | 20 | 0.0% | 4.50 | — | 100.0% | — | 0.50 |

## Faithfulness

- Faithful conversations: 113/120 (94.2%)
- Total unsupported facts: 33

## Slot Presentation Distribution

- 0 slots (failure): 344 turns
- 1 slot (poor): 47 turns
- 2–3 slots (acceptable): 134 turns
- 3–5 slots (good): 112 turns
- 6+ slots (overwhelming): 49 turns
