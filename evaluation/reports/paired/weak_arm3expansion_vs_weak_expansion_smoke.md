# Paired comparison — `20260610_221716__weak_nlp_arm3_expansion__8119c12__smoke` vs `20260610_220723__weak_expansion__8119c12__smoke`

**Pairing:** 13 valid pairs out of 14 matched scenario-runs (excluded 1 pairs where either side had `termination=error` or missing derived metrics). Baseline-only keys: 0, candidate-only: 0.

## Overall (all tiers)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 13 | 7.77 [6.38, 9.23] | 7.23 [5.62, 8.92] | -0.54 [-2.38, 1.31] | 0.6445 |
| efficiency_ratio | 11 | 2.58 [1.35, 4.30] | 2.92 [1.70, 4.73] | 0.35 [-1.59, 2.03] | 0.3972 |
| simulated_latency_ms | 13 | 7563.91 [4862.39, 10700.83] | 9196.72 [5163.42, 14376.98] | 1632.80 [-1142.05, 4435.08] | 0.3636 |
| parse_accuracy | 11 | 0.77 [0.50, 1.00] | 0.64 [0.36, 0.86] | -0.14 [-0.36, 0.05] | 0.3447 |
| dead_end_turns | 13 | 1.00 [0.46, 1.77] | 1.38 [0.62, 2.54] | 0.38 [-0.15, 1.00] | 0.2809 |
| unsupported_facts | 13 | 0.15 [0.00, 0.46] | 0.31 [0.00, 0.92] | 0.15 [0.00, 0.46] | 1.0000 |
| availability_calls | 13 | 4.46 [2.92, 6.23] | 6.31 [3.54, 9.69] | 1.85 [-0.62, 4.23] | 0.2115 |
| ladder_fire_turns | 13 | 0.77 [0.38, 1.23] | 1.46 [0.85, 2.15] | 0.69 [0.00, 1.46] | 0.1241 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 13 | 76.9% [53.8%, 100.0%] | 61.5% [38.5%, 84.6%] | -15.4% [-46.2%, 15.4%] | 3/1 | 0.6250 |
| faithful | 13 | 92.3% [76.9%, 100.0%] | 92.3% [76.9%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 13 | 15.4% [0.0%, 38.5%] | 15.4% [0.0%, 38.5%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 13 | 3.85 [3.31, 4.31] | 3.69 [3.08, 4.23] | -0.15 [-0.62, 0.38] | 0.6653 |
| negotiation_effectiveness | 9 | 3.11 [2.33, 3.89] | 2.67 [2.11, 3.22] | -0.44 [-0.89, 0.00] | 0.1736 |
| conversational_efficiency | 13 | 2.77 [2.31, 3.31] | 2.54 [2.08, 3.00] | -0.23 [-0.85, 0.38] | 0.5160 |
| customer_experience | 11 | 2.82 [2.27, 3.45] | 2.36 [1.82, 2.91] | -0.45 [-1.00, 0.09] | 0.1521 |
| recovery_quality | 5 | 2.60 [2.20, 3.00] | 2.20 [1.40, 3.20] | -0.40 [-1.00, 0.40] | 0.4237 |

## Tier 1 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 9.50 [7.00, 12.00] | 4.50 [4.00, 5.00] | -5.00 [-7.00, -3.00] | 0.3711 |
| efficiency_ratio | 2 | 1.50 [1.00, 2.00] | 1.00 [1.00, 1.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| simulated_latency_ms | 2 | 1917.40 [1222.18, 2612.62] | 1655.81 [1648.64, 1662.98] | -261.59 [-949.63, 426.45] | 1.0000 |
| parse_accuracy | 2 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 1.0000 |
| dead_end_turns | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 1.50 [1.00, 2.00] | 1.00 [1.00, 1.00] | -0.50 [-1.00, 0.00] | 1.0000 |
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
| temporal_understanding | 2 | 5.00 [5.00, 5.00] | 5.00 [5.00, 5.00] | 0.00 [0.00, 0.00] | 1.0000 |
| negotiation_effectiveness | 0 | — | — | — | — |
| conversational_efficiency | 2 | 3.50 [3.00, 4.00] | 3.00 [3.00, 3.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| customer_experience | 2 | 3.50 [3.00, 4.00] | 3.00 [3.00, 3.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 2 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 4.00 [3.00, 5.00] | 9.00 [6.00, 12.00] | 5.00 [3.00, 7.00] | 0.3711 |
| efficiency_ratio | 2 | 5.50 [1.00, 10.00] | 2.00 [2.00, 2.00] | -3.50 [-8.00, 1.00] | 1.0000 |
| simulated_latency_ms | 2 | 8469.61 [3429.00, 13510.23] | 3375.01 [2741.66, 4008.37] | -5094.60 [-9501.86, -687.34] | 0.3711 |
| parse_accuracy | 2 | 1.00 [1.00, 1.00] | 0.75 [0.50, 1.00] | -0.25 [-0.50, 0.00] | 1.0000 |
| dead_end_turns | 2 | 1.00 [0.00, 2.00] | 1.00 [1.00, 1.00] | 0.00 [-1.00, 1.00] | 0.6374 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 5.50 [1.00, 10.00] | 2.00 [2.00, 2.00] | -3.50 [-8.00, 1.00] | 1.0000 |
| ladder_fire_turns | 2 | 1.50 [0.00, 3.00] | 1.00 [1.00, 1.00] | -0.50 [-2.00, 1.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 100.0% [100.0%, 100.0%] | 50.0% [0.0%, 100.0%] | -50.0% [-100.0%, 0.0%] | 1/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 3.00 [2.00, 4.00] | 3.00 [2.00, 4.00] | 0.00 [0.00, 0.00] | 1.0000 |
| negotiation_effectiveness | 2 | 2.50 [1.00, 4.00] | 2.50 [1.00, 4.00] | 0.00 [0.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 3.50 [2.00, 5.00] | 2.00 [1.00, 3.00] | -1.50 [-2.00, -1.00] | 0.3711 |
| customer_experience | 2 | 3.50 [2.00, 5.00] | 2.00 [1.00, 3.00] | -1.50 [-2.00, -1.00] | 0.3711 |
| recovery_quality | 0 | — | — | — | — |

## Tier 3 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 7.50 [6.00, 9.00] | 6.50 [6.00, 7.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| efficiency_ratio | 2 | 1.50 [1.50, 1.50] | 1.50 [1.50, 1.50] | 0.00 [0.00, 0.00] | 1.0000 |
| simulated_latency_ms | 2 | 4045.95 [3962.89, 4129.02] | 3997.18 [3992.21, 4002.15] | -48.77 [-136.80, 39.26] | 1.0000 |
| parse_accuracy | 2 | 0.75 [0.50, 1.00] | 1.00 [1.00, 1.00] | 0.25 [0.00, 0.50] | 1.0000 |
| dead_end_turns | 2 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 1.0000 |
| unsupported_facts | 2 | 1.00 [0.00, 2.00] | 2.00 [0.00, 4.00] | 1.00 [0.00, 2.00] | 1.0000 |
| availability_calls | 2 | 3.00 [3.00, 3.00] | 3.00 [3.00, 3.00] | 0.00 [0.00, 0.00] | 1.0000 |
| ladder_fire_turns | 2 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 2 | 50.0% [0.0%, 100.0%] | 50.0% [0.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 3.00 [3.00, 3.00] | 4.00 [3.00, 5.00] | 1.00 [0.00, 2.00] | 1.0000 |
| negotiation_effectiveness | 2 | 3.50 [3.00, 4.00] | 3.50 [3.00, 4.00] | 0.00 [0.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 2.00 [2.00, 2.00] | 2.50 [2.00, 3.00] | 0.50 [0.00, 1.00] | 1.0000 |
| customer_experience | 2 | 2.00 [2.00, 2.00] | 2.50 [2.00, 3.00] | 0.50 [0.00, 1.00] | 1.0000 |
| recovery_quality | 2 | 3.00 [3.00, 3.00] | 3.00 [2.00, 4.00] | 0.00 [-1.00, 1.00] | 0.6374 |

## Tier 4 (n=1)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 1 | 12.00 [12.00, 12.00] | 12.00 [12.00, 12.00] | 0.00 [0.00, 0.00] | 1.0000 |
| efficiency_ratio | 1 | 5.50 [5.50, 5.50] | 10.50 [10.50, 10.50] | 5.00 [5.00, 5.00] | 1.0000 |
| simulated_latency_ms | 1 | 20716.78 [20716.78, 20716.78] | 32485.72 [32485.72, 32485.72] | 11768.95 [11768.95, 11768.95] | 1.0000 |
| parse_accuracy | 1 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 1.0000 |
| dead_end_turns | 1 | 5.00 [5.00, 5.00] | 7.00 [7.00, 7.00] | 2.00 [2.00, 2.00] | 1.0000 |
| unsupported_facts | 1 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 1 | 11.00 [11.00, 11.00] | 21.00 [21.00, 21.00] | 10.00 [10.00, 10.00] | 1.0000 |
| ladder_fire_turns | 1 | 1.00 [1.00, 1.00] | 4.00 [4.00, 4.00] | 3.00 [3.00, 3.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 1 | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | -100.0% [-100.0%, -100.0%] | 1/0 | 1.0000 |
| faithful | 1 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 1 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 1 | 3.00 [3.00, 3.00] | 3.00 [3.00, 3.00] | 0.00 [0.00, 0.00] | 1.0000 |
| negotiation_effectiveness | 1 | 2.00 [2.00, 2.00] | 2.00 [2.00, 2.00] | 0.00 [0.00, 0.00] | 1.0000 |
| conversational_efficiency | 1 | 2.00 [2.00, 2.00] | 2.00 [2.00, 2.00] | 0.00 [0.00, 0.00] | 1.0000 |
| customer_experience | 1 | 2.00 [2.00, 2.00] | 2.00 [2.00, 2.00] | 0.00 [0.00, 0.00] | 1.0000 |
| recovery_quality | 1 | 2.00 [2.00, 2.00] | 2.00 [2.00, 2.00] | 0.00 [0.00, 0.00] | 1.0000 |

## Tier 5 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 8.00 [5.00, 11.00] | 8.50 [5.00, 12.00] | 0.50 [0.00, 1.00] | 1.0000 |
| efficiency_ratio | 2 | 1.67 [1.33, 2.00] | 2.33 [1.33, 3.33] | 0.67 [0.00, 1.33] | 1.0000 |
| simulated_latency_ms | 2 | 7726.41 [4866.99, 10585.83] | 9888.89 [5027.93, 14749.85] | 2162.48 [160.94, 4164.02] | 0.3711 |
| parse_accuracy | 2 | 0.50 [0.00, 1.00] | 0.25 [0.00, 0.50] | -0.25 [-0.50, 0.00] | 1.0000 |
| dead_end_turns | 2 | 1.00 [1.00, 1.00] | 0.50 [0.00, 1.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 5.00 [4.00, 6.00] | 7.00 [4.00, 10.00] | 2.00 [0.00, 4.00] | 1.0000 |
| ladder_fire_turns | 2 | 1.00 [1.00, 1.00] | 1.50 [1.00, 2.00] | 0.50 [0.00, 1.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 100.0% [100.0%, 100.0%] | 50.0% [0.0%, 100.0%] | -50.0% [-100.0%, 0.0%] | 1/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 4.50 [4.00, 5.00] | 3.00 [2.00, 4.00] | -1.50 [-2.00, -1.00] | 0.3711 |
| negotiation_effectiveness | 2 | 2.50 [2.00, 3.00] | 2.00 [2.00, 2.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 3.00 [2.00, 4.00] | 2.00 [2.00, 2.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| customer_experience | 2 | 2.50 [2.00, 3.00] | 1.50 [1.00, 2.00] | -1.00 [-1.00, -1.00] | 0.3458 |
| recovery_quality | 2 | 2.50 [2.00, 3.00] | 1.50 [1.00, 2.00] | -1.00 [-1.00, -1.00] | 0.3458 |

## Tier 6 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 7.00 [7.00, 7.00] | 7.50 [5.00, 10.00] | 0.50 [-2.00, 3.00] | 1.0000 |
| efficiency_ratio | 2 | 1.25 [1.00, 1.50] | 4.00 [3.50, 4.50] | 2.75 [2.50, 3.00] | 0.3711 |
| simulated_latency_ms | 2 | 6005.91 [2594.10, 9417.71] | 11119.11 [8505.75, 13732.46] | 5113.20 [4314.75, 5911.65] | 0.3711 |
| parse_accuracy | 2 | 0.50 [0.00, 1.00] | 0.00 [0.00, 0.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| dead_end_turns | 2 | 0.00 [0.00, 0.00] | 2.00 [1.00, 3.00] | 2.00 [1.00, 3.00] | 0.3711 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 2.50 [2.00, 3.00] | 8.00 [7.00, 9.00] | 5.50 [5.00, 6.00] | 0.3711 |
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
| negotiation_effectiveness | 2 | 4.50 [4.00, 5.00] | 3.00 [3.00, 3.00] | -1.50 [-2.00, -1.00] | 0.3711 |
| conversational_efficiency | 2 | 3.00 [3.00, 3.00] | 3.00 [2.00, 4.00] | 0.00 [-1.00, 1.00] | 0.6374 |
| customer_experience | 2 | 3.00 [3.00, 3.00] | 3.00 [2.00, 4.00] | 0.00 [-1.00, 1.00] | 0.6374 |
| recovery_quality | 0 | — | — | — | — |

## Tier 7 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 8.50 [8.00, 9.00] | 5.00 [3.00, 7.00] | -3.50 [-5.00, -2.00] | 0.3711 |
| efficiency_ratio | 0 | — | — | — | — |
| simulated_latency_ms | 2 | 10641.77 [10275.76, 11007.79] | 13499.82 [8224.83, 18774.80] | 2858.04 [-2782.96, 8499.04] | 1.0000 |
| parse_accuracy | 0 | — | — | — | — |
| dead_end_turns | 2 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 6.00 [6.00, 6.00] | 9.50 [5.00, 14.00] | 3.50 [-1.00, 8.00] | 1.0000 |
| ladder_fire_turns | 2 | 1.00 [1.00, 1.00] | 2.00 [1.00, 3.00] | 1.00 [0.00, 2.00] | 1.0000 |

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
| conversational_efficiency | 2 | 2.00 [2.00, 2.00] | 3.00 [2.00, 4.00] | 1.00 [0.00, 2.00] | 1.0000 |
| customer_experience | 0 | — | — | — | — |
| recovery_quality | 0 | — | — | — | — |
