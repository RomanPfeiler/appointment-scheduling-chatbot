# KPI Summary — 20260606_234404__nlp_arm3__e1626fa__representative_reduced

**Stage:** nlp_arm3  **Commit:** `e1626fa4f1e33c633e84186a822bc2d5c6e78d0a`  **Note:** Arm 3 (Gemini JSON, exact_time guard) reduced representative vs corrected baseline e1626fa

Generated: 2026-06-07T01:46:50.051974Z  ·  60 scenarios  ·  120 records

## Headline KPIs

| KPI | Value |
|-----|-------|
| Booking completion rate | 59.2% |
| Median turns | 6.00 |
| Median efficiency ratio | 2.67 |
| Faithful rate | 94.2% |
| Mean simulated latency (ms) | 15887.6 |
| Mean parse accuracy | 0.46 |
| Dead-end turns total | 387 |
| Mean dead-end turns / conversation | 3.23 |

## Per-Tier Breakdown

| Tier | Records | Booking % | Median turns | Median eff. ratio | Faithful % | Mean parse acc. | Mean dead-ends |
|------|---------|-----------|--------------|-------------------|------------|-----------------|----------------|
| 1 | 10 | 80.0% | 2.00 | 1.00 | 100.0% | 0.55 | 2.20 |
| 2 | 10 | 50.0% | 10.50 | 3.00 | 90.0% | 0.56 | 2.50 |
| 3 | 20 | 75.0% | 5.00 | 2.50 | 95.0% | 0.45 | 3.90 |
| 4 | 20 | 70.0% | 6.50 | 2.75 | 90.0% | 0.47 | 4.00 |
| 5 | 20 | 75.0% | 7.00 | 2.67 | 90.0% | 0.47 | 3.30 |
| 6 | 20 | 70.0% | 7.00 | 3.25 | 100.0% | 0.38 | 5.00 |
| 7 | 20 | 0.0% | 4.00 | — | 95.0% | — | 0.80 |

## Faithfulness

- Faithful conversations: 113/120 (94.2%)
- Total unsupported facts: 52

## Slot Presentation Distribution

- 0 slots (failure): 510 turns
- 1 slot (poor): 85 turns
- 2–3 slots (acceptable): 169 turns
- 3–5 slots (good): 25 turns
- 6+ slots (overwhelming): 5 turns
