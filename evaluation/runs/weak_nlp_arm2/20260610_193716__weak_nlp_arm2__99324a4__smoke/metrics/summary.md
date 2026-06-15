# KPI Summary — 20260610_193716__weak_nlp_arm2__99324a4__smoke

**Stage:** weak_nlp_arm2  **Commit:** `99324a4f93c55dd415e70f28f0e4ab1e2c32285e`  **Note:** Weak-agent smoke: Arm 2 NLP (local Llama-3.2-3B) hints into flash-lite agent, thinking off

Generated: 2026-06-10T21:03:16.462321Z  ·  14 scenarios  ·  14 records

## Headline KPIs

| KPI | Value |
|-----|-------|
| Booking completion rate | 35.7% |
| Median turns | 11.50 |
| Median efficiency ratio | 3.25 |
| Faithful rate | 100.0% |
| Mean simulated latency (ms) | 8589.6 |
| Mean parse accuracy | 0.62 |
| Dead-end turns total | 67 |
| Mean dead-end turns / conversation | 4.79 |

## Per-Tier Breakdown

| Tier | Records | Booking % | Median turns | Median eff. ratio | Faithful % | Mean parse acc. | Mean dead-ends |
|------|---------|-----------|--------------|-------------------|------------|-----------------|----------------|
| 1 | 2 | 50.0% | 8.50 | 6.00 | 100.0% | 1.00 | 2.00 |
| 2 | 2 | 0.0% | 12.00 | 11.00 | 100.0% | 0.75 | 11.00 |
| 3 | 2 | 100.0% | 8.50 | 3.00 | 100.0% | 0.75 | 3.50 |
| 4 | 2 | 0.0% | 12.00 | 3.25 | 100.0% | 0.50 | 5.50 |
| 5 | 2 | 0.0% | 12.00 | 3.33 | 100.0% | 0.75 | 9.00 |
| 6 | 2 | 100.0% | 8.50 | 2.25 | 100.0% | 0.00 | 2.50 |
| 7 | 2 | 0.0% | 4.00 | — | 100.0% | — | 0.00 |

## Faithfulness

- Faithful conversations: 14/14 (100.0%)
- Total unsupported facts: 0

## Slot Presentation Distribution

- 0 slots (failure): 111 turns
- 1 slot (poor): 9 turns
- 2–3 slots (acceptable): 9 turns
- 3–5 slots (good): 2 turns
- 6+ slots (overwhelming): 0 turns
