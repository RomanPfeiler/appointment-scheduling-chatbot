# Paired comparison — `20260610_221716__weak_nlp_arm3_expansion__8119c12__smoke` vs `20260610_183456__weak_baseline__a368480__smoke`

**Pairing:** 14 valid pairs out of 14 matched scenario-runs (excluded 0 pairs where either side had `termination=error` or missing derived metrics). Baseline-only keys: 0, candidate-only: 0.

## Overall (all tiers)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 14 | 8.57 [6.57, 10.36] | 7.57 [5.93, 9.21] | -1.00 [-3.00, 0.79] | 0.5382 |
| efficiency_ratio | 12 | 3.19 [1.94, 4.82] | 3.01 [1.86, 4.61] | -0.18 [-2.35, 1.81] | 0.9187 |
| simulated_latency_ms | 14 | 18269.52 [4871.45, 38413.19] | 9335.29 [5578.77, 14076.28] | -8934.23 [-28064.20, 5474.30] | 0.4899 |
| parse_accuracy | 12 | 0.38 [0.12, 0.62] | 0.58 [0.33, 0.83] | 0.21 [-0.08, 0.50] | 0.1983 |
| dead_end_turns | 14 | 3.43 [1.86, 5.29] | 1.43 [0.71, 2.43] | -2.00 [-4.07, -0.21] | 0.0764 |
| unsupported_facts | 14 | 0.00 [0.00, 0.00] | 0.29 [0.00, 0.86] | 0.29 [0.00, 0.86] | 1.0000 |
| availability_calls | 14 | 4.64 [2.79, 6.64] | 6.43 [3.93, 9.57] | 1.79 [-1.36, 5.00] | 0.6071 |
| ladder_fire_turns | 14 | 0.21 [0.00, 0.57] | 1.43 [0.86, 2.07] | 1.21 [0.79, 1.64] | 0.0015** |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 14 | 50.0% [21.4%, 78.6%] | 57.1% [28.6%, 78.6%] | 7.1% [-14.3%, 28.6%] | 1/2 | 1.0000 |
| faithful | 14 | 100.0% [100.0%, 100.0%] | 92.9% [78.6%, 100.0%] | -7.1% [-21.4%, 0.0%] | 1/0 | 1.0000 |
| refusal_accepted | 14 | 14.3% [0.0%, 35.7%] | 14.3% [0.0%, 35.7%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 14 | 3.86 [3.43, 4.29] | 3.64 [3.14, 4.21] | -0.21 [-0.93, 0.43] | 0.6244 |
| negotiation_effectiveness | 10 | 2.70 [2.20, 3.30] | 2.60 [2.00, 3.20] | -0.10 [-0.80, 0.60] | 0.8605 |
| conversational_efficiency | 14 | 2.64 [2.14, 3.21] | 2.43 [2.00, 2.93] | -0.21 [-0.79, 0.43] | 0.5242 |
| customer_experience | 12 | 2.50 [2.00, 3.08] | 2.25 [1.75, 2.75] | -0.25 [-0.83, 0.33] | 0.4374 |
| recovery_quality | 6 | 2.33 [2.00, 3.00] | 2.00 [1.33, 2.83] | -0.33 [-1.17, 0.67] | 0.7103 |

## Tier 1 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 7.50 [3.00, 12.00] | 4.50 [4.00, 5.00] | -3.00 [-8.00, 2.00] | 1.0000 |
| efficiency_ratio | 2 | 6.00 [1.00, 11.00] | 1.00 [1.00, 1.00] | -5.00 [-10.00, 0.00] | 1.0000 |
| simulated_latency_ms | 2 | 33048.90 [2286.82, 63810.97] | 1655.81 [1648.64, 1662.98] | -31393.09 [-62147.99, -638.19] | 0.3711 |
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
| conversational_efficiency | 2 | 3.50 [2.00, 5.00] | 3.00 [3.00, 3.00] | -0.50 [-2.00, 1.00] | 1.0000 |
| customer_experience | 2 | 3.50 [2.00, 5.00] | 3.00 [3.00, 3.00] | -0.50 [-2.00, 1.00] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 2 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 7.50 [3.00, 12.00] | 9.00 [6.00, 12.00] | 1.50 [0.00, 3.00] | 1.0000 |
| efficiency_ratio | 2 | 2.50 [1.00, 4.00] | 2.00 [2.00, 2.00] | -0.50 [-2.00, 1.00] | 1.0000 |
| simulated_latency_ms | 2 | 4161.43 [3512.29, 4810.56] | 3375.01 [2741.66, 4008.37] | -786.41 [-802.20, -770.63] | 0.3711 |
| parse_accuracy | 2 | 0.50 [0.00, 1.00] | 0.75 [0.50, 1.00] | 0.25 [-0.50, 1.00] | 1.0000 |
| dead_end_turns | 2 | 2.00 [0.00, 4.00] | 1.00 [1.00, 1.00] | -1.00 [-3.00, 1.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 2.50 [1.00, 4.00] | 2.00 [2.00, 2.00] | -0.50 [-2.00, 1.00] | 1.0000 |
| ladder_fire_turns | 2 | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.3458 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 50.0% [0.0%, 100.0%] | 50.0% [0.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 3.50 [3.00, 4.00] | 3.00 [2.00, 4.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| negotiation_effectiveness | 2 | 3.00 [2.00, 4.00] | 2.50 [1.00, 4.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 3.00 [2.00, 4.00] | 2.00 [1.00, 3.00] | -1.00 [-1.00, -1.00] | 0.3458 |
| customer_experience | 2 | 3.00 [2.00, 4.00] | 2.00 [1.00, 3.00] | -1.00 [-1.00, -1.00] | 0.3458 |
| recovery_quality | 0 | — | — | — | — |

## Tier 3 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 9.50 [7.00, 12.00] | 6.50 [6.00, 7.00] | -3.00 [-6.00, 0.00] | 1.0000 |
| efficiency_ratio | 2 | 1.75 [1.00, 2.50] | 1.50 [1.50, 1.50] | -0.25 [-1.00, 0.50] | 1.0000 |
| simulated_latency_ms | 2 | 4532.58 [3969.14, 5096.02] | 3997.18 [3992.21, 4002.15] | -535.40 [-1103.80, 33.00] | 1.0000 |
| parse_accuracy | 2 | 0.75 [0.50, 1.00] | 1.00 [1.00, 1.00] | 0.25 [0.00, 0.50] | 1.0000 |
| dead_end_turns | 2 | 2.00 [1.00, 3.00] | 1.00 [1.00, 1.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 2.00 [0.00, 4.00] | 2.00 [0.00, 4.00] | 1.0000 |
| availability_calls | 2 | 3.50 [2.00, 5.00] | 3.00 [3.00, 3.00] | -0.50 [-2.00, 1.00] | 1.0000 |
| ladder_fire_turns | 2 | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.3458 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 50.0% [0.0%, 100.0%] | -50.0% [-100.0%, 0.0%] | 1/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 3.00 [3.00, 3.00] | 4.00 [3.00, 5.00] | 1.00 [0.00, 2.00] | 1.0000 |
| negotiation_effectiveness | 2 | 3.00 [2.00, 4.00] | 3.50 [3.00, 4.00] | 0.50 [-1.00, 2.00] | 1.0000 |
| conversational_efficiency | 2 | 2.00 [2.00, 2.00] | 2.50 [2.00, 3.00] | 0.50 [0.00, 1.00] | 1.0000 |
| customer_experience | 2 | 2.50 [2.00, 3.00] | 2.50 [2.00, 3.00] | 0.00 [-1.00, 1.00] | 0.6374 |
| recovery_quality | 2 | 3.00 [2.00, 4.00] | 3.00 [2.00, 4.00] | 0.00 [-2.00, 2.00] | 0.6374 |

## Tier 4 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 11.00 [10.00, 12.00] | 12.00 [12.00, 12.00] | 1.00 [0.00, 2.00] | 1.0000 |
| efficiency_ratio | 2 | 3.75 [3.50, 4.00] | 7.25 [4.00, 10.50] | 3.50 [0.00, 7.00] | 1.0000 |
| simulated_latency_ms | 2 | 13662.74 [7061.44, 20264.03] | 21811.21 [11136.69, 32485.72] | 8148.47 [-9127.35, 25424.28] | 1.0000 |
| parse_accuracy | 2 | 0.00 [0.00, 0.00] | 0.50 [0.00, 1.00] | 0.50 [0.00, 1.00] | 1.0000 |
| dead_end_turns | 2 | 6.00 [5.00, 7.00] | 4.50 [2.00, 7.00] | -1.50 [-5.00, 2.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 7.50 [7.00, 8.00] | 14.50 [8.00, 21.00] | 7.00 [0.00, 14.00] | 1.0000 |
| ladder_fire_turns | 2 | 1.00 [0.00, 2.00] | 2.50 [1.00, 4.00] | 1.50 [1.00, 2.00] | 0.3711 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 50.0% [0.0%, 100.0%] | 0.0% [0.0%, 0.0%] | -50.0% [-100.0%, 0.0%] | 1/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 4.00 [3.00, 5.00] | 3.00 [3.00, 3.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| negotiation_effectiveness | 2 | 2.50 [2.00, 3.00] | 2.00 [2.00, 2.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 2.50 [2.00, 3.00] | 1.50 [1.00, 2.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| customer_experience | 2 | 2.00 [2.00, 2.00] | 1.50 [1.00, 2.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| recovery_quality | 2 | 2.00 [2.00, 2.00] | 1.50 [1.00, 2.00] | -0.50 [-1.00, 0.00] | 1.0000 |

## Tier 5 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 12.00 [12.00, 12.00] | 8.50 [5.00, 12.00] | -3.50 [-7.00, 0.00] | 1.0000 |
| efficiency_ratio | 2 | 2.67 [1.67, 3.67] | 2.33 [1.33, 3.33] | -0.33 [-0.33, -0.33] | 0.3711 |
| simulated_latency_ms | 2 | 63703.23 [5709.76, 121696.69] | 9888.89 [5027.93, 14749.85] | -53814.34 [-106946.85, -681.83] | 0.3711 |
| parse_accuracy | 2 | 0.50 [0.00, 1.00] | 0.25 [0.00, 0.50] | -0.25 [-0.50, 0.00] | 1.0000 |
| dead_end_turns | 2 | 5.00 [3.00, 7.00] | 0.50 [0.00, 1.00] | -4.50 [-6.00, -3.00] | 0.3711 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 8.00 [5.00, 11.00] | 7.00 [4.00, 10.00] | -1.00 [-1.00, -1.00] | 0.3458 |
| ladder_fire_turns | 2 | 0.50 [0.00, 1.00] | 1.50 [1.00, 2.00] | 1.00 [1.00, 1.00] | 0.3458 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 0.0% [0.0%, 0.0%] | 50.0% [0.0%, 100.0%] | 50.0% [0.0%, 100.0%] | 0/1 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 4.00 [3.00, 5.00] | 3.00 [2.00, 4.00] | -1.00 [-3.00, 1.00] | 1.0000 |
| negotiation_effectiveness | 2 | 3.00 [2.00, 4.00] | 2.00 [2.00, 2.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 1.50 [1.00, 2.00] | 2.00 [2.00, 2.00] | 0.50 [0.00, 1.00] | 1.0000 |
| customer_experience | 2 | 1.50 [1.00, 2.00] | 1.50 [1.00, 2.00] | 0.00 [-1.00, 1.00] | 0.6374 |
| recovery_quality | 2 | 2.00 [2.00, 2.00] | 1.50 [1.00, 2.00] | -0.50 [-1.00, 0.00] | 1.0000 |

## Tier 6 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 6.00 [3.00, 9.00] | 7.50 [5.00, 10.00] | 1.50 [1.00, 2.00] | 0.3711 |
| efficiency_ratio | 2 | 2.50 [1.00, 4.00] | 4.00 [3.50, 4.50] | 1.50 [-0.50, 3.50] | 1.0000 |
| simulated_latency_ms | 2 | 7511.05 [6127.86, 8894.23] | 11119.11 [8505.75, 13732.46] | 3608.06 [-388.49, 7604.60] | 1.0000 |
| parse_accuracy | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| dead_end_turns | 2 | 3.50 [1.00, 6.00] | 2.00 [1.00, 3.00] | -1.50 [-5.00, 2.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 5.00 [2.00, 8.00] | 8.00 [7.00, 9.00] | 3.00 [-1.00, 7.00] | 1.0000 |
| ladder_fire_turns | 2 | 0.00 [0.00, 0.00] | 2.00 [1.00, 3.00] | 2.00 [1.00, 3.00] | 0.3711 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 3.50 [3.00, 4.00] | 3.50 [3.00, 4.00] | 0.00 [-1.00, 1.00] | 0.6374 |
| negotiation_effectiveness | 2 | 2.00 [2.00, 2.00] | 3.00 [3.00, 3.00] | 1.00 [1.00, 1.00] | 0.3458 |
| conversational_efficiency | 2 | 3.50 [3.00, 4.00] | 3.00 [2.00, 4.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| customer_experience | 2 | 2.50 [2.00, 3.00] | 3.00 [2.00, 4.00] | 0.50 [0.00, 1.00] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 7 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 6.50 [5.00, 8.00] | 5.00 [3.00, 7.00] | -1.50 [-5.00, 2.00] | 1.0000 |
| efficiency_ratio | 0 | — | — | — | — |
| simulated_latency_ms | 2 | 1266.73 [1162.02, 1371.45] | 13499.82 [8224.83, 18774.80] | 12233.08 [7062.81, 17403.36] | 0.3711 |
| parse_accuracy | 0 | — | — | — | — |
| dead_end_turns | 2 | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.3458 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 0.00 [0.00, 0.00] | 9.50 [5.00, 14.00] | 9.50 [5.00, 14.00] | 0.3711 |
| ladder_fire_turns | 2 | 0.00 [0.00, 0.00] | 2.00 [1.00, 3.00] | 2.00 [1.00, 3.00] | 0.3711 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 4.50 [4.00, 5.00] | 4.00 [3.00, 5.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| negotiation_effectiveness | 0 | — | — | — | — |
| conversational_efficiency | 2 | 2.50 [2.00, 3.00] | 3.00 [2.00, 4.00] | 0.50 [-1.00, 2.00] | 1.0000 |
| customer_experience | 0 | — | — | — | — |
| recovery_quality | 0 | — | — | — | — |
