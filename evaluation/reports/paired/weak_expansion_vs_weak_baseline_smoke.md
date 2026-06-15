# Paired comparison — `20260610_220723__weak_expansion__8119c12__smoke` vs `20260610_183456__weak_baseline__a368480__smoke`

**Pairing:** 13 valid pairs out of 14 matched scenario-runs (excluded 1 pairs where either side had `termination=error` or missing derived metrics). Baseline-only keys: 0, candidate-only: 0.

## Overall (all tiers)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 13 | 8.31 [6.31, 10.15] | 7.77 [6.38, 9.23] | -0.54 [-2.92, 2.00] | 0.6882 |
| efficiency_ratio | 11 | 3.12 [1.79, 4.89] | 2.58 [1.35, 4.30] | -0.55 [-2.71, 1.38] | 0.7220 |
| simulated_latency_ms | 13 | 18116.10 [4030.92, 37408.24] | 7563.91 [4862.39, 10700.83] | -10552.18 [-30993.59, 4628.83] | 0.9443 |
| parse_accuracy | 11 | 0.41 [0.14, 0.68] | 0.77 [0.50, 1.00] | 0.36 [0.09, 0.64] | 0.0719 |
| dead_end_turns | 13 | 3.15 [1.54, 5.00] | 1.00 [0.46, 1.77] | -2.15 [-4.15, -0.54] | 0.0316* |
| unsupported_facts | 13 | 0.00 [0.00, 0.00] | 0.15 [0.00, 0.46] | 0.15 [0.00, 0.46] | 1.0000 |
| availability_calls | 13 | 4.38 [2.38, 6.46] | 4.46 [2.92, 6.23] | 0.08 [-2.46, 2.54] | 0.9287 |
| ladder_fire_turns | 13 | 0.23 [0.00, 0.62] | 0.77 [0.38, 1.23] | 0.54 [0.08, 1.08] | 0.0708 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 13 | 53.8% [23.1%, 76.9%] | 76.9% [53.8%, 100.0%] | 23.1% [-7.7%, 53.8%] | 1/4 | 0.3750 |
| faithful | 13 | 100.0% [100.0%, 100.0%] | 92.3% [76.9%, 100.0%] | -7.7% [-23.1%, 0.0%] | 1/0 | 1.0000 |
| refusal_accepted | 13 | 15.4% [0.0%, 38.5%] | 15.4% [0.0%, 38.5%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 13 | 3.77 [3.38, 4.23] | 3.85 [3.31, 4.31] | 0.08 [-0.31, 0.46] | 0.8501 |
| negotiation_effectiveness | 10 | 2.70 [2.20, 3.30] | 3.30 [2.50, 4.10] | 0.60 [-0.40, 1.60] | 0.2864 |
| conversational_efficiency | 13 | 2.62 [2.08, 3.23] | 2.77 [2.31, 3.31] | 0.15 [-0.46, 0.85] | 0.7498 |
| customer_experience | 11 | 2.55 [2.00, 3.18] | 2.82 [2.27, 3.45] | 0.27 [-0.36, 0.91] | 0.5201 |
| recovery_quality | 5 | 2.40 [2.00, 3.20] | 2.60 [2.20, 3.00] | 0.20 [-0.40, 0.80] | 0.7728 |

## Tier 1 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 7.50 [3.00, 12.00] | 9.50 [7.00, 12.00] | 2.00 [-5.00, 9.00] | 1.0000 |
| efficiency_ratio | 2 | 6.00 [1.00, 11.00] | 1.50 [1.00, 2.00] | -4.50 [-9.00, 0.00] | 1.0000 |
| simulated_latency_ms | 2 | 33048.90 [2286.82, 63810.97] | 1917.40 [1222.18, 2612.62] | -31131.50 [-61198.36, -1064.64] | 0.3711 |
| parse_accuracy | 2 | 0.50 [0.00, 1.00] | 1.00 [1.00, 1.00] | 0.50 [0.00, 1.00] | 1.0000 |
| dead_end_turns | 2 | 5.50 [0.00, 11.00] | 0.00 [0.00, 0.00] | -5.50 [-11.00, 0.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 6.00 [1.00, 11.00] | 1.50 [1.00, 2.00] | -4.50 [-9.00, 0.00] | 1.0000 |
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
| temporal_understanding | 2 | 4.50 [4.00, 5.00] | 5.00 [5.00, 5.00] | 0.50 [0.00, 1.00] | 1.0000 |
| negotiation_effectiveness | 1 | 2.00 [2.00, 2.00] | 5.00 [5.00, 5.00] | 3.00 [3.00, 3.00] | 1.0000 |
| conversational_efficiency | 2 | 3.50 [2.00, 5.00] | 3.50 [3.00, 4.00] | 0.00 [-2.00, 2.00] | 0.6374 |
| customer_experience | 2 | 3.50 [2.00, 5.00] | 3.50 [3.00, 4.00] | 0.00 [-2.00, 2.00] | 0.6374 |
| recovery_quality | 0 | — | — | — | — |

## Tier 2 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 7.50 [3.00, 12.00] | 4.00 [3.00, 5.00] | -3.50 [-7.00, 0.00] | 1.0000 |
| efficiency_ratio | 2 | 2.50 [1.00, 4.00] | 5.50 [1.00, 10.00] | 3.00 [0.00, 6.00] | 1.0000 |
| simulated_latency_ms | 2 | 4161.43 [3512.29, 4810.56] | 8469.61 [3429.00, 13510.23] | 4308.19 [-83.29, 8699.66] | 1.0000 |
| parse_accuracy | 2 | 0.50 [0.00, 1.00] | 1.00 [1.00, 1.00] | 0.50 [0.00, 1.00] | 1.0000 |
| dead_end_turns | 2 | 2.00 [0.00, 4.00] | 1.00 [0.00, 2.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 2.50 [1.00, 4.00] | 5.50 [1.00, 10.00] | 3.00 [0.00, 6.00] | 1.0000 |
| ladder_fire_turns | 2 | 0.00 [0.00, 0.00] | 1.50 [0.00, 3.00] | 1.50 [0.00, 3.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 50.0% [0.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 50.0% [0.0%, 100.0%] | 0/1 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 3.50 [3.00, 4.00] | 3.00 [2.00, 4.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| negotiation_effectiveness | 2 | 3.00 [2.00, 4.00] | 2.50 [1.00, 4.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 3.00 [2.00, 4.00] | 3.50 [2.00, 5.00] | 0.50 [0.00, 1.00] | 1.0000 |
| customer_experience | 2 | 3.00 [2.00, 4.00] | 3.50 [2.00, 5.00] | 0.50 [0.00, 1.00] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 3 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 9.50 [7.00, 12.00] | 7.50 [6.00, 9.00] | -2.00 [-6.00, 2.00] | 1.0000 |
| efficiency_ratio | 2 | 1.75 [1.00, 2.50] | 1.50 [1.50, 1.50] | -0.25 [-1.00, 0.50] | 1.0000 |
| simulated_latency_ms | 2 | 4532.58 [3969.14, 5096.02] | 4045.95 [3962.89, 4129.02] | -486.63 [-967.00, -6.25] | 0.3711 |
| parse_accuracy | 2 | 0.75 [0.50, 1.00] | 0.75 [0.50, 1.00] | 0.00 [0.00, 0.00] | 1.0000 |
| dead_end_turns | 2 | 2.00 [1.00, 3.00] | 1.00 [1.00, 1.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 1.00 [0.00, 2.00] | 1.00 [0.00, 2.00] | 1.0000 |
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
| temporal_understanding | 2 | 3.00 [3.00, 3.00] | 3.00 [3.00, 3.00] | 0.00 [0.00, 0.00] | 1.0000 |
| negotiation_effectiveness | 2 | 3.00 [2.00, 4.00] | 3.50 [3.00, 4.00] | 0.50 [-1.00, 2.00] | 1.0000 |
| conversational_efficiency | 2 | 2.00 [2.00, 2.00] | 2.00 [2.00, 2.00] | 0.00 [0.00, 0.00] | 1.0000 |
| customer_experience | 2 | 2.50 [2.00, 3.00] | 2.00 [2.00, 2.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| recovery_quality | 2 | 3.00 [2.00, 4.00] | 3.00 [3.00, 3.00] | 0.00 [-1.00, 1.00] | 0.6374 |

## Tier 4 (n=1)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 1 | 10.00 [10.00, 10.00] | 12.00 [12.00, 12.00] | 2.00 [2.00, 2.00] | 1.0000 |
| efficiency_ratio | 1 | 3.50 [3.50, 3.50] | 5.50 [5.50, 5.50] | 2.00 [2.00, 2.00] | 1.0000 |
| simulated_latency_ms | 1 | 7061.44 [7061.44, 7061.44] | 20716.78 [20716.78, 20716.78] | 13655.34 [13655.34, 13655.34] | 1.0000 |
| parse_accuracy | 1 | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.0000 |
| dead_end_turns | 1 | 5.00 [5.00, 5.00] | 5.00 [5.00, 5.00] | 0.00 [0.00, 0.00] | 1.0000 |
| unsupported_facts | 1 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 1 | 7.00 [7.00, 7.00] | 11.00 [11.00, 11.00] | 4.00 [4.00, 4.00] | 1.0000 |
| ladder_fire_turns | 1 | 2.00 [2.00, 2.00] | 1.00 [1.00, 1.00] | -1.00 [-1.00, -1.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 1 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 1 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 1 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 1 | 3.00 [3.00, 3.00] | 3.00 [3.00, 3.00] | 0.00 [0.00, 0.00] | 1.0000 |
| negotiation_effectiveness | 1 | 3.00 [3.00, 3.00] | 2.00 [2.00, 2.00] | -1.00 [-1.00, -1.00] | 1.0000 |
| conversational_efficiency | 1 | 2.00 [2.00, 2.00] | 2.00 [2.00, 2.00] | 0.00 [0.00, 0.00] | 1.0000 |
| customer_experience | 1 | 2.00 [2.00, 2.00] | 2.00 [2.00, 2.00] | 0.00 [0.00, 0.00] | 1.0000 |
| recovery_quality | 1 | 2.00 [2.00, 2.00] | 2.00 [2.00, 2.00] | 0.00 [0.00, 0.00] | 1.0000 |

## Tier 5 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 12.00 [12.00, 12.00] | 8.00 [5.00, 11.00] | -4.00 [-7.00, -1.00] | 0.3711 |
| efficiency_ratio | 2 | 2.67 [1.67, 3.67] | 1.67 [1.33, 2.00] | -1.00 [-1.67, -0.33] | 0.3711 |
| simulated_latency_ms | 2 | 63703.23 [5709.76, 121696.69] | 7726.41 [4866.99, 10585.83] | -55976.81 [-111110.86, -842.76] | 0.3711 |
| parse_accuracy | 2 | 0.50 [0.00, 1.00] | 0.50 [0.00, 1.00] | 0.00 [0.00, 0.00] | 1.0000 |
| dead_end_turns | 2 | 5.00 [3.00, 7.00] | 1.00 [1.00, 1.00] | -4.00 [-6.00, -2.00] | 0.3711 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 8.00 [5.00, 11.00] | 5.00 [4.00, 6.00] | -3.00 [-5.00, -1.00] | 0.3711 |
| ladder_fire_turns | 2 | 0.50 [0.00, 1.00] | 1.00 [1.00, 1.00] | 0.50 [0.00, 1.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 0.0% [0.0%, 0.0%] | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0/2 | 0.5000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 4.00 [3.00, 5.00] | 4.50 [4.00, 5.00] | 0.50 [-1.00, 2.00] | 1.0000 |
| negotiation_effectiveness | 2 | 3.00 [2.00, 4.00] | 2.50 [2.00, 3.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 1.50 [1.00, 2.00] | 3.00 [2.00, 4.00] | 1.50 [0.00, 3.00] | 1.0000 |
| customer_experience | 2 | 1.50 [1.00, 2.00] | 2.50 [2.00, 3.00] | 1.00 [0.00, 2.00] | 1.0000 |
| recovery_quality | 2 | 2.00 [2.00, 2.00] | 2.50 [2.00, 3.00] | 0.50 [0.00, 1.00] | 1.0000 |

## Tier 6 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 6.00 [3.00, 9.00] | 7.00 [7.00, 7.00] | 1.00 [-2.00, 4.00] | 1.0000 |
| efficiency_ratio | 2 | 2.50 [1.00, 4.00] | 1.25 [1.00, 1.50] | -1.25 [-3.00, 0.50] | 1.0000 |
| simulated_latency_ms | 2 | 7511.05 [6127.86, 8894.23] | 6005.91 [2594.10, 9417.71] | -1505.14 [-6300.14, 3289.85] | 1.0000 |
| parse_accuracy | 2 | 0.00 [0.00, 0.00] | 0.50 [0.00, 1.00] | 0.50 [0.00, 1.00] | 1.0000 |
| dead_end_turns | 2 | 3.50 [1.00, 6.00] | 0.00 [0.00, 0.00] | -3.50 [-6.00, -1.00] | 0.3711 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 5.00 [2.00, 8.00] | 2.50 [2.00, 3.00] | -2.50 [-6.00, 1.00] | 1.0000 |
| ladder_fire_turns | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 3.50 [3.00, 4.00] | 3.50 [3.00, 4.00] | 0.00 [0.00, 0.00] | 1.0000 |
| negotiation_effectiveness | 2 | 2.00 [2.00, 2.00] | 4.50 [4.00, 5.00] | 2.50 [2.00, 3.00] | 0.3711 |
| conversational_efficiency | 2 | 3.50 [3.00, 4.00] | 3.00 [3.00, 3.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| customer_experience | 2 | 2.50 [2.00, 3.00] | 3.00 [3.00, 3.00] | 0.50 [0.00, 1.00] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 7 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 6.50 [5.00, 8.00] | 8.50 [8.00, 9.00] | 2.00 [0.00, 4.00] | 1.0000 |
| efficiency_ratio | 0 | — | — | — | — |
| simulated_latency_ms | 2 | 1266.73 [1162.02, 1371.45] | 10641.77 [10275.76, 11007.79] | 9375.04 [8904.31, 9845.77] | 0.3711 |
| parse_accuracy | 0 | — | — | — | — |
| dead_end_turns | 2 | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.3458 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 0.00 [0.00, 0.00] | 6.00 [6.00, 6.00] | 6.00 [6.00, 6.00] | 0.3458 |
| ladder_fire_turns | 2 | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.3458 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 4.50 [4.00, 5.00] | 4.50 [4.00, 5.00] | 0.00 [0.00, 0.00] | 1.0000 |
| negotiation_effectiveness | 0 | — | — | — | — |
| conversational_efficiency | 2 | 2.50 [2.00, 3.00] | 2.00 [2.00, 2.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| customer_experience | 0 | — | — | — | — |
| recovery_quality | 0 | — | — | — | — |
