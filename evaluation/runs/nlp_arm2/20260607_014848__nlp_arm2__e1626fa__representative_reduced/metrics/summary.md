# KPI Summary — 20260607_014848__nlp_arm2__e1626fa__representative_reduced

**Stage:** nlp_arm2  **Commit:** `e1626fa4f1e33c633e84186a822bc2d5c6e78d0a`  **Note:** Arm 2 (local Llama-3.2-3B) reduced representative vs corrected baseline e1626fa

Generated: 2026-06-07T12:06:43.785937Z  ·  60 scenarios  ·  120 records

## Headline KPIs

| KPI | Value |
|-----|-------|
| Booking completion rate | 54.2% |
| Median turns | 6.00 |
| Median efficiency ratio | 2.50 |
| Faithful rate | 95.8% |
| Mean simulated latency (ms) | 23223.3 |
| Mean parse accuracy | 0.48 |
| Dead-end turns total | 404 |
| Mean dead-end turns / conversation | 3.37 |

## Per-Tier Breakdown

| Tier | Records | Booking % | Median turns | Median eff. ratio | Faithful % | Mean parse acc. | Mean dead-ends |
|------|---------|-----------|--------------|-------------------|------------|-----------------|----------------|
| 1 | 10 | 90.0% | 2.00 | 1.00 | 100.0% | 0.50 | 1.00 |
| 2 | 10 | 30.0% | 12.00 | 12.00 | 100.0% | 0.80 | 5.10 |
| 3 | 20 | 55.0% | 9.50 | 2.50 | 95.0% | 0.47 | 4.95 |
| 4 | 20 | 75.0% | 6.00 | 2.00 | 100.0% | 0.45 | 4.00 |
| 5 | 20 | 65.0% | 9.00 | 3.33 | 95.0% | 0.38 | 3.75 |
| 6 | 20 | 70.0% | 6.00 | 2.50 | 90.0% | 0.45 | 3.65 |
| 7 | 20 | 0.0% | 5.00 | — | 95.0% | — | 0.80 |

## Faithfulness

- Faithful conversations: 115/120 (95.8%)
- Total unsupported facts: 27

## Slot Presentation Distribution

- 0 slots (failure): 546 turns
- 1 slot (poor): 88 turns
- 2–3 slots (acceptable): 201 turns
- 3–5 slots (good): 34 turns
- 6+ slots (overwhelming): 6 turns
