# Paired comparison — `20260610_215714__weak_nlp_arm3__8119c12__smoke` vs `20260610_183456__weak_baseline__a368480__smoke`

**Pairing:** 14 valid pairs out of 14 matched scenario-runs (excluded 0 pairs where either side had `termination=error` or missing derived metrics). Baseline-only keys: 0, candidate-only: 0.

## Overall (all tiers)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 14 | 8.57 [6.57, 10.36] | 9.00 [7.07, 10.79] | 0.43 [-2.21, 3.07] | 0.8109 |
| efficiency_ratio | 12 | 3.19 [1.94, 4.82] | 3.01 [2.12, 4.04] | -0.18 [-2.35, 1.75] | 0.7987 |
| simulated_latency_ms | 14 | 18269.52 [4871.45, 38413.19] | 9254.46 [4733.95, 15284.43] | -9015.06 [-29113.41, 6124.27] | 0.7536 |
| parse_accuracy | 12 | 0.38 [0.12, 0.62] | 0.62 [0.38, 0.83] | 0.25 [-0.08, 0.58] | 0.1510 |
| dead_end_turns | 14 | 3.43 [1.86, 5.29] | 2.50 [1.21, 3.79] | -0.93 [-3.07, 1.00] | 0.5728 |
| unsupported_facts | 14 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 14 | 4.64 [2.79, 6.64] | 4.64 [3.00, 6.29] | 0.00 [-2.36, 2.14] | 0.8782 |
| ladder_fire_turns | 14 | 0.21 [0.00, 0.57] | 0.14 [0.00, 0.43] | -0.07 [-0.50, 0.36] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 14 | 50.0% [21.4%, 78.6%] | 35.7% [14.3%, 64.3%] | -14.3% [-50.0%, 21.4%] | 5/3 | 0.7266 |
| faithful | 14 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 14 | 14.3% [0.0%, 35.7%] | 14.3% [0.0%, 35.7%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 14 | 3.86 [3.43, 4.29] | 3.29 [2.57, 4.00] | -0.57 [-1.36, 0.21] | 0.2040 |
| negotiation_effectiveness | 10 | 2.70 [2.20, 3.30] | 2.00 [1.60, 2.50] | -0.70 [-1.50, 0.10] | 0.1824 |
| conversational_efficiency | 14 | 2.64 [2.14, 3.21] | 2.14 [1.64, 2.71] | -0.50 [-1.29, 0.29] | 0.1996 |
| customer_experience | 12 | 2.50 [2.00, 3.08] | 2.25 [1.67, 2.92] | -0.25 [-1.08, 0.58] | 0.5650 |
| recovery_quality | 6 | 2.33 [2.00, 3.00] | 1.50 [1.17, 1.83] | -0.83 [-1.33, -0.33] | 0.0890 |

## Tier 1 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 7.50 [3.00, 12.00] | 3.50 [2.00, 5.00] | -4.00 [-10.00, 2.00] | 1.0000 |
| efficiency_ratio | 2 | 6.00 [1.00, 11.00] | 1.00 [1.00, 1.00] | -5.00 [-10.00, 0.00] | 1.0000 |
| simulated_latency_ms | 2 | 33048.90 [2286.82, 63810.97] | 1662.64 [1548.66, 1776.63] | -31386.25 [-62262.31, -510.19] | 0.3711 |
| parse_accuracy | 2 | 0.50 [0.00, 1.00] | 1.00 [1.00, 1.00] | 0.50 [0.00, 1.00] | 1.0000 |
| dead_end_turns | 2 | 5.50 [0.00, 11.00] | 0.00 [0.00, 0.00] | -5.50 [-11.00, 0.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 6.00 [1.00, 11.00] | 1.00 [1.00, 1.00] | -5.00 [-10.00, 0.00] | 1.0000 |
| ladder_fire_turns | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 50.0% [0.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 50.0% [0.0%, 100.0%] | 0/1 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 4.50 [4.00, 5.00] | 5.00 [5.00, 5.00] | 0.50 [0.00, 1.00] | 1.0000 |
| negotiation_effectiveness | 0 | — | — | — | — |
| conversational_efficiency | 2 | 3.50 [2.00, 5.00] | 4.00 [3.00, 5.00] | 0.50 [-2.00, 3.00] | 1.0000 |
| customer_experience | 2 | 3.50 [2.00, 5.00] | 4.00 [3.00, 5.00] | 0.50 [-2.00, 3.00] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 2 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 7.50 [3.00, 12.00] | 8.50 [5.00, 12.00] | 1.00 [-7.00, 9.00] | 1.0000 |
| efficiency_ratio | 2 | 2.50 [1.00, 4.00] | 4.50 [2.00, 7.00] | 2.00 [-2.00, 6.00] | 1.0000 |
| simulated_latency_ms | 2 | 4161.43 [3512.29, 4810.56] | 4805.50 [2971.88, 6639.12] | 644.08 [-1838.68, 3126.84] | 1.0000 |
| parse_accuracy | 2 | 0.50 [0.00, 1.00] | 0.75 [0.50, 1.00] | 0.25 [-0.50, 1.00] | 1.0000 |
| dead_end_turns | 2 | 2.00 [0.00, 4.00] | 0.00 [0.00, 0.00] | -2.00 [-4.00, 0.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 2.50 [1.00, 4.00] | 4.50 [2.00, 7.00] | 2.00 [-2.00, 6.00] | 1.0000 |
| ladder_fire_turns | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 50.0% [0.0%, 100.0%] | 50.0% [0.0%, 100.0%] | 0.0% [-100.0%, 100.0%] | 1/1 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 3.50 [3.00, 4.00] | 3.50 [3.00, 4.00] | 0.00 [-1.00, 1.00] | 0.6374 |
| negotiation_effectiveness | 2 | 3.00 [2.00, 4.00] | 3.00 [2.00, 4.00] | 0.00 [-2.00, 2.00] | 0.6374 |
| conversational_efficiency | 2 | 3.00 [2.00, 4.00] | 2.50 [2.00, 3.00] | -0.50 [-2.00, 1.00] | 1.0000 |
| customer_experience | 2 | 3.00 [2.00, 4.00] | 3.00 [2.00, 4.00] | 0.00 [-2.00, 2.00] | 0.6374 |
| recovery_quality | 0 | — | — | — | — |

## Tier 3 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 9.50 [7.00, 12.00] | 12.00 [12.00, 12.00] | 2.50 [0.00, 5.00] | 1.0000 |
| efficiency_ratio | 2 | 1.75 [1.00, 2.50] | 4.50 [4.00, 5.00] | 2.75 [2.50, 3.00] | 0.3711 |
| simulated_latency_ms | 2 | 4532.58 [3969.14, 5096.02] | 28383.95 [16322.60, 40445.31] | 23851.37 [12353.46, 35349.29] | 0.3711 |
| parse_accuracy | 2 | 0.75 [0.50, 1.00] | 0.75 [0.50, 1.00] | 0.00 [-0.50, 0.50] | 0.6374 |
| dead_end_turns | 2 | 2.00 [1.00, 3.00] | 6.00 [6.00, 6.00] | 4.00 [3.00, 5.00] | 0.3711 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 3.50 [2.00, 5.00] | 9.00 [8.00, 10.00] | 5.50 [5.00, 6.00] | 0.3711 |
| ladder_fire_turns | 2 | 0.00 [0.00, 0.00] | 1.00 [0.00, 2.00] | 1.00 [0.00, 2.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | -100.0% [-100.0%, -100.0%] | 2/0 | 0.5000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 3.00 [3.00, 3.00] | 4.50 [4.00, 5.00] | 1.50 [1.00, 2.00] | 0.3711 |
| negotiation_effectiveness | 2 | 3.00 [2.00, 4.00] | 2.00 [2.00, 2.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 2.00 [2.00, 2.00] | 2.50 [2.00, 3.00] | 0.50 [0.00, 1.00] | 1.0000 |
| customer_experience | 2 | 2.50 [2.00, 3.00] | 2.00 [2.00, 2.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| recovery_quality | 2 | 3.00 [2.00, 4.00] | 2.00 [2.00, 2.00] | -1.00 [-2.00, 0.00] | 1.0000 |

## Tier 4 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 11.00 [10.00, 12.00] | 12.00 [12.00, 12.00] | 1.00 [0.00, 2.00] | 1.0000 |
| efficiency_ratio | 2 | 3.75 [3.50, 4.00] | 3.50 [3.00, 4.00] | -0.25 [-1.00, 0.50] | 1.0000 |
| simulated_latency_ms | 2 | 13662.74 [7061.44, 20264.03] | 15076.28 [14426.28, 15726.28] | 1413.54 [-4537.75, 7364.84] | 1.0000 |
| parse_accuracy | 2 | 0.00 [0.00, 0.00] | 0.50 [0.00, 1.00] | 0.50 [0.00, 1.00] | 1.0000 |
| dead_end_turns | 2 | 6.00 [5.00, 7.00] | 4.50 [3.00, 6.00] | -1.50 [-4.00, 1.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 7.50 [7.00, 8.00] | 7.00 [6.00, 8.00] | -0.50 [-2.00, 1.00] | 1.0000 |
| ladder_fire_turns | 2 | 1.00 [0.00, 2.00] | 0.00 [0.00, 0.00] | -1.00 [-2.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 50.0% [0.0%, 100.0%] | 0.0% [0.0%, 0.0%] | -50.0% [-100.0%, 0.0%] | 1/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 4.00 [3.00, 5.00] | 1.50 [1.00, 2.00] | -2.50 [-3.00, -2.00] | 0.3711 |
| negotiation_effectiveness | 2 | 2.50 [2.00, 3.00] | 1.50 [1.00, 2.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 2.50 [2.00, 3.00] | 1.00 [1.00, 1.00] | -1.50 [-2.00, -1.00] | 0.3711 |
| customer_experience | 2 | 2.00 [2.00, 2.00] | 1.00 [1.00, 1.00] | -1.00 [-1.00, -1.00] | 0.3458 |
| recovery_quality | 2 | 2.00 [2.00, 2.00] | 1.00 [1.00, 1.00] | -1.00 [-1.00, -1.00] | 0.3458 |

## Tier 5 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 12.00 [12.00, 12.00] | 12.00 [12.00, 12.00] | 0.00 [0.00, 0.00] | 1.0000 |
| efficiency_ratio | 2 | 2.67 [1.67, 3.67] | 1.83 [1.67, 2.00] | -0.83 [-1.67, 0.00] | 1.0000 |
| simulated_latency_ms | 2 | 63703.23 [5709.76, 121696.69] | 6266.91 [4920.97, 7612.86] | -57436.31 [-114083.84, -788.79] | 0.3711 |
| parse_accuracy | 2 | 0.50 [0.00, 1.00] | 0.75 [0.50, 1.00] | 0.25 [-0.50, 1.00] | 1.0000 |
| dead_end_turns | 2 | 5.00 [3.00, 7.00] | 3.00 [2.00, 4.00] | -2.00 [-3.00, -1.00] | 0.3711 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 8.00 [5.00, 11.00] | 5.50 [5.00, 6.00] | -2.50 [-5.00, 0.00] | 1.0000 |
| ladder_fire_turns | 2 | 0.50 [0.00, 1.00] | 0.00 [0.00, 0.00] | -0.50 [-1.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 0.0% [0.0%, 0.0%] | 50.0% [0.0%, 100.0%] | 50.0% [0.0%, 100.0%] | 0/1 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 4.00 [3.00, 5.00] | 2.50 [2.00, 3.00] | -1.50 [-2.00, -1.00] | 0.3711 |
| negotiation_effectiveness | 2 | 3.00 [2.00, 4.00] | 1.50 [1.00, 2.00] | -1.50 [-2.00, -1.00] | 0.3711 |
| conversational_efficiency | 2 | 1.50 [1.00, 2.00] | 1.50 [1.00, 2.00] | 0.00 [-1.00, 1.00] | 0.6374 |
| customer_experience | 2 | 1.50 [1.00, 2.00] | 1.50 [1.00, 2.00] | 0.00 [-1.00, 1.00] | 0.6374 |
| recovery_quality | 2 | 2.00 [2.00, 2.00] | 1.50 [1.00, 2.00] | -0.50 [-1.00, 0.00] | 1.0000 |

## Tier 6 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 6.00 [3.00, 9.00] | 9.50 [7.00, 12.00] | 3.50 [-2.00, 9.00] | 1.0000 |
| efficiency_ratio | 2 | 2.50 [1.00, 4.00] | 2.75 [2.50, 3.00] | 0.25 [-1.50, 2.00] | 1.0000 |
| simulated_latency_ms | 2 | 7511.05 [6127.86, 8894.23] | 7817.25 [5627.53, 10006.98] | 306.20 [-3266.70, 3879.11] | 1.0000 |
| parse_accuracy | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| dead_end_turns | 2 | 3.50 [1.00, 6.00] | 4.00 [3.00, 5.00] | 0.50 [-3.00, 4.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 5.00 [2.00, 8.00] | 5.50 [5.00, 6.00] | 0.50 [-3.00, 4.00] | 1.0000 |
| ladder_fire_turns | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 100.0% [100.0%, 100.0%] | 50.0% [0.0%, 100.0%] | -50.0% [-100.0%, 0.0%] | 1/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 3.50 [3.00, 4.00] | 3.00 [3.00, 3.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| negotiation_effectiveness | 2 | 2.00 [2.00, 2.00] | 2.00 [2.00, 2.00] | 0.00 [0.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 3.50 [3.00, 4.00] | 2.00 [2.00, 2.00] | -1.50 [-2.00, -1.00] | 0.3711 |
| customer_experience | 2 | 2.50 [2.00, 3.00] | 2.00 [2.00, 2.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 7 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 6.50 [5.00, 8.00] | 5.50 [5.00, 6.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| efficiency_ratio | 0 | — | — | — | — |
| simulated_latency_ms | 2 | 1266.73 [1162.02, 1371.45] | 768.65 [728.90, 808.40] | -498.09 [-563.05, -433.12] | 0.3711 |
| parse_accuracy | 0 | — | — | — | — |
| dead_end_turns | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| ladder_fire_turns | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 4.50 [4.00, 5.00] | 3.00 [1.00, 5.00] | -1.50 [-3.00, 0.00] | 1.0000 |
| negotiation_effectiveness | 0 | — | — | — | — |
| conversational_efficiency | 2 | 2.50 [2.00, 3.00] | 1.50 [1.00, 2.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| customer_experience | 0 | — | — | — | — |
| recovery_quality | 0 | — | — | — | — |
