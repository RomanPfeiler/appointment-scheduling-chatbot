# KPI Summary — 20260610_221716__weak_nlp_arm3_expansion__8119c12__smoke

**Stage:** weak_nlp_arm3_expansion  **Commit:** `8119c12460118207d25eb8999a6599f22293dbf4`  **Note:** Weak-agent smoke: Arm 3 NLP (pinned flash) + executor expansion under flash-lite agent, thinking off (complementary-vs-redundant at low headroom)

Generated: 2026-06-10T22:25:57.962790Z  ·  14 scenarios  ·  14 records

## Headline KPIs

| KPI | Value |
|-----|-------|
| Booking completion rate | 57.1% |
| Median turns | 6.50 |
| Median efficiency ratio | 2.00 |
| Faithful rate | 92.9% |
| Mean simulated latency (ms) | 9335.3 |
| Mean parse accuracy | 0.58 |
| Dead-end turns total | 20 |
| Mean dead-end turns / conversation | 1.43 |

## Per-Tier Breakdown

| Tier | Records | Booking % | Median turns | Median eff. ratio | Faithful % | Mean parse acc. | Mean dead-ends |
|------|---------|-----------|--------------|-------------------|------------|-----------------|----------------|
| 1 | 2 | 100.0% | 4.50 | 1.00 | 100.0% | 1.00 | 0.00 |
| 2 | 2 | 50.0% | 9.00 | 2.00 | 100.0% | 0.75 | 1.00 |
| 3 | 2 | 100.0% | 6.50 | 1.50 | 50.0% | 1.00 | 1.00 |
| 4 | 2 | 0.0% | 12.00 | 7.25 | 100.0% | 0.50 | 4.50 |
| 5 | 2 | 50.0% | 8.50 | 2.33 | 100.0% | 0.25 | 0.50 |
| 6 | 2 | 100.0% | 7.50 | 4.00 | 100.0% | 0.00 | 2.00 |
| 7 | 2 | 0.0% | 5.00 | — | 100.0% | — | 1.00 |

## Faithfulness

- Faithful conversations: 13/14 (92.9%)
- Total unsupported facts: 4

## Slot Presentation Distribution

- 0 slots (failure): 66 turns
- 1 slot (poor): 9 turns
- 2–3 slots (acceptable): 21 turns
- 3–5 slots (good): 13 turns
- 6+ slots (overwhelming): 5 turns
