# Paired comparison — `20260610_192943__weak_nlp_arm1__e4073f5__smoke` vs `20260610_183456__weak_baseline__a368480__smoke`

**Pairing:** 14 valid pairs out of 14 matched scenario-runs (excluded 0 pairs where either side had `termination=error` or missing derived metrics). Baseline-only keys: 0, candidate-only: 0.

## Overall (all tiers)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 14 | 8.57 [6.57, 10.36] | 7.93 [5.79, 9.93] | -0.64 [-2.86, 1.57] | 0.5527 |
| efficiency_ratio | 12 | 3.19 [1.94, 4.82] | 3.36 [1.76, 5.32] | 0.17 [-1.51, 2.39] | 0.6240 |
| simulated_latency_ms | 14 | 18269.52 [4871.45, 38413.19] | 5578.33 [3870.69, 7433.78] | -12691.20 [-32960.04, 446.05] | 0.5302 |
| parse_accuracy | 12 | 0.38 [0.12, 0.62] | 0.46 [0.25, 0.67] | 0.08 [-0.17, 0.38] | 0.5887 |
| dead_end_turns | 14 | 3.43 [1.86, 5.29] | 3.00 [1.43, 4.71] | -0.43 [-2.64, 2.00] | 0.4793 |
| unsupported_facts | 14 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 14 | 4.64 [2.79, 6.64] | 4.29 [2.71, 5.93] | -0.36 [-2.64, 2.00] | 0.7831 |
| ladder_fire_turns | 14 | 0.21 [0.00, 0.57] | 0.14 [0.00, 0.36] | -0.07 [-0.50, 0.29] | 0.8501 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 14 | 50.0% [21.4%, 78.6%] | 42.9% [14.3%, 71.4%] | -7.1% [-28.6%, 14.3%] | 2/1 | 1.0000 |
| faithful | 14 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 14 | 14.3% [0.0%, 35.7%] | 14.3% [0.0%, 35.7%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 14 | 3.86 [3.43, 4.29] | 3.07 [2.29, 3.86] | -0.79 [-1.57, 0.07] | 0.0866 |
| negotiation_effectiveness | 9 | 2.67 [2.22, 3.33] | 1.89 [1.44, 2.33] | -0.78 [-1.22, -0.33] | 0.0263* |
| conversational_efficiency | 14 | 2.64 [2.14, 3.21] | 2.43 [1.64, 3.29] | -0.21 [-1.07, 0.71] | 0.5681 |
| customer_experience | 12 | 2.50 [2.00, 3.08] | 2.42 [1.67, 3.25] | -0.08 [-0.83, 0.75] | 0.8066 |
| recovery_quality | 5 | 2.40 [2.00, 3.20] | 1.80 [1.00, 2.60] | -0.60 [-1.00, 0.20] | 0.2330 |

## Tier 1 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 7.50 [3.00, 12.00] | 7.50 [3.00, 12.00] | 0.00 [0.00, 0.00] | 1.0000 |
| efficiency_ratio | 2 | 6.00 [1.00, 11.00] | 4.50 [1.00, 8.00] | -1.50 [-3.00, 0.00] | 1.0000 |
| simulated_latency_ms | 2 | 33048.90 [2286.82, 63810.97] | 4629.03 [1765.26, 7492.79] | -28419.87 [-56318.18, -521.56] | 0.3711 |
| parse_accuracy | 2 | 0.50 [0.00, 1.00] | 1.00 [1.00, 1.00] | 0.50 [0.00, 1.00] | 1.0000 |
| dead_end_turns | 2 | 5.50 [0.00, 11.00] | 3.50 [0.00, 7.00] | -2.00 [-4.00, 0.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 6.00 [1.00, 11.00] | 4.50 [1.00, 8.00] | -1.50 [-3.00, 0.00] | 1.0000 |
| ladder_fire_turns | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 50.0% [0.0%, 100.0%] | 50.0% [0.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 4.50 [4.00, 5.00] | 3.50 [2.00, 5.00] | -1.00 [-3.00, 1.00] | 1.0000 |
| negotiation_effectiveness | 1 | 2.00 [2.00, 2.00] | 2.00 [2.00, 2.00] | 0.00 [0.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 3.50 [2.00, 5.00] | 3.00 [1.00, 5.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| customer_experience | 2 | 3.50 [2.00, 5.00] | 3.50 [2.00, 5.00] | 0.00 [0.00, 0.00] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 2 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 7.50 [3.00, 12.00] | 12.00 [12.00, 12.00] | 4.50 [0.00, 9.00] | 1.0000 |
| efficiency_ratio | 2 | 2.50 [1.00, 4.00] | 8.00 [5.00, 11.00] | 5.50 [1.00, 10.00] | 0.3711 |
| simulated_latency_ms | 2 | 4161.43 [3512.29, 4810.56] | 7544.33 [5027.81, 10060.86] | 3382.91 [217.25, 6548.57] | 0.3711 |
| parse_accuracy | 2 | 0.50 [0.00, 1.00] | 0.25 [0.00, 0.50] | -0.25 [-0.50, 0.00] | 1.0000 |
| dead_end_turns | 2 | 2.00 [0.00, 4.00] | 8.00 [5.00, 11.00] | 6.00 [1.00, 11.00] | 0.3711 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 2.50 [1.00, 4.00] | 8.00 [5.00, 11.00] | 5.50 [1.00, 10.00] | 0.3711 |
| ladder_fire_turns | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 50.0% [0.0%, 100.0%] | 0.0% [0.0%, 0.0%] | -50.0% [-100.0%, 0.0%] | 1/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 3.50 [3.00, 4.00] | 3.00 [1.00, 5.00] | -0.50 [-2.00, 1.00] | 1.0000 |
| negotiation_effectiveness | 2 | 3.00 [2.00, 4.00] | 1.50 [1.00, 2.00] | -1.50 [-2.00, -1.00] | 0.3711 |
| conversational_efficiency | 2 | 3.00 [2.00, 4.00] | 1.50 [1.00, 2.00] | -1.50 [-2.00, -1.00] | 0.3711 |
| customer_experience | 2 | 3.00 [2.00, 4.00] | 1.50 [1.00, 2.00] | -1.50 [-2.00, -1.00] | 0.3711 |
| recovery_quality | 0 | — | — | — | — |

## Tier 3 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 9.50 [7.00, 12.00] | 9.50 [7.00, 12.00] | 0.00 [0.00, 0.00] | 1.0000 |
| efficiency_ratio | 2 | 1.75 [1.00, 2.50] | 2.75 [2.00, 3.50] | 1.00 [1.00, 1.00] | 0.3458 |
| simulated_latency_ms | 2 | 4532.58 [3969.14, 5096.02] | 6421.97 [5511.81, 7332.13] | 1889.39 [1542.67, 2236.12] | 0.3711 |
| parse_accuracy | 2 | 0.75 [0.50, 1.00] | 0.50 [0.50, 0.50] | -0.25 [-0.50, 0.00] | 1.0000 |
| dead_end_turns | 2 | 2.00 [1.00, 3.00] | 4.50 [3.00, 6.00] | 2.50 [2.00, 3.00] | 0.3711 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 3.50 [2.00, 5.00] | 5.50 [4.00, 7.00] | 2.00 [2.00, 2.00] | 0.3458 |
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
| temporal_understanding | 2 | 3.00 [3.00, 3.00] | 3.00 [2.00, 4.00] | 0.00 [-1.00, 1.00] | 0.6374 |
| negotiation_effectiveness | 2 | 3.00 [2.00, 4.00] | 2.00 [1.00, 3.00] | -1.00 [-1.00, -1.00] | 0.3458 |
| conversational_efficiency | 2 | 2.00 [2.00, 2.00] | 2.00 [1.00, 3.00] | 0.00 [-1.00, 1.00] | 0.6374 |
| customer_experience | 2 | 2.50 [2.00, 3.00] | 2.00 [1.00, 3.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| recovery_quality | 2 | 3.00 [2.00, 4.00] | 2.00 [1.00, 3.00] | -1.00 [-1.00, -1.00] | 0.3458 |

## Tier 4 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 11.00 [10.00, 12.00] | 6.50 [1.00, 12.00] | -4.50 [-9.00, 0.00] | 1.0000 |
| efficiency_ratio | 2 | 3.75 [3.50, 4.00] | 1.50 [0.50, 2.50] | -2.25 [-3.00, -1.50] | 0.3711 |
| simulated_latency_ms | 2 | 13662.74 [7061.44, 20264.03] | 7562.41 [2703.54, 12421.28] | -6100.33 [-7842.75, -4357.90] | 0.3711 |
| parse_accuracy | 2 | 0.00 [0.00, 0.00] | 0.25 [0.00, 0.50] | 0.25 [0.00, 0.50] | 1.0000 |
| dead_end_turns | 2 | 6.00 [5.00, 7.00] | 0.50 [0.00, 1.00] | -5.50 [-6.00, -5.00] | 0.3711 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 7.50 [7.00, 8.00] | 3.00 [1.00, 5.00] | -4.50 [-6.00, -3.00] | 0.3711 |
| ladder_fire_turns | 2 | 1.00 [0.00, 2.00] | 0.00 [0.00, 0.00] | -1.00 [-2.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 50.0% [0.0%, 100.0%] | 50.0% [0.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 4.00 [3.00, 5.00] | 4.00 [3.00, 5.00] | 0.00 [-2.00, 2.00] | 0.6374 |
| negotiation_effectiveness | 1 | 2.00 [2.00, 2.00] | 2.00 [2.00, 2.00] | 0.00 [0.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 2.50 [2.00, 3.00] | 3.00 [1.00, 5.00] | 0.50 [-2.00, 3.00] | 1.0000 |
| customer_experience | 2 | 2.00 [2.00, 2.00] | 3.00 [1.00, 5.00] | 1.00 [-1.00, 3.00] | 1.0000 |
| recovery_quality | 1 | 2.00 [2.00, 2.00] | 1.00 [1.00, 1.00] | -1.00 [-1.00, -1.00] | 1.0000 |

## Tier 5 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 12.00 [12.00, 12.00] | 10.00 [8.00, 12.00] | -2.00 [-4.00, 0.00] | 1.0000 |
| efficiency_ratio | 2 | 2.67 [1.67, 3.67] | 1.67 [1.33, 2.00] | -1.00 [-2.33, 0.33] | 1.0000 |
| simulated_latency_ms | 2 | 63703.23 [5709.76, 121696.69] | 5582.28 [4680.51, 6484.05] | -58120.95 [-117016.19, 774.29] | 1.0000 |
| parse_accuracy | 2 | 0.50 [0.00, 1.00] | 0.75 [0.50, 1.00] | 0.25 [-0.50, 1.00] | 1.0000 |
| dead_end_turns | 2 | 5.00 [3.00, 7.00] | 2.00 [1.00, 3.00] | -3.00 [-4.00, -2.00] | 0.3711 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 8.00 [5.00, 11.00] | 5.00 [4.00, 6.00] | -3.00 [-7.00, 1.00] | 1.0000 |
| ladder_fire_turns | 2 | 0.50 [0.00, 1.00] | 0.50 [0.00, 1.00] | 0.00 [-1.00, 1.00] | 0.6374 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 0.0% [0.0%, 0.0%] | 50.0% [0.0%, 100.0%] | 50.0% [0.0%, 100.0%] | 0/1 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 4.00 [3.00, 5.00] | 2.00 [1.00, 3.00] | -2.00 [-2.00, -2.00] | 0.3458 |
| negotiation_effectiveness | 2 | 3.00 [2.00, 4.00] | 2.00 [1.00, 3.00] | -1.00 [-1.00, -1.00] | 0.3458 |
| conversational_efficiency | 2 | 1.50 [1.00, 2.00] | 1.50 [1.00, 2.00] | 0.00 [-1.00, 1.00] | 0.6374 |
| customer_experience | 2 | 1.50 [1.00, 2.00] | 1.50 [1.00, 2.00] | 0.00 [-1.00, 1.00] | 0.6374 |
| recovery_quality | 2 | 2.00 [2.00, 2.00] | 2.00 [1.00, 3.00] | 0.00 [-1.00, 1.00] | 0.6374 |

## Tier 6 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 6.00 [3.00, 9.00] | 5.00 [3.00, 7.00] | -1.00 [-6.00, 4.00] | 1.0000 |
| efficiency_ratio | 2 | 2.50 [1.00, 4.00] | 1.75 [0.50, 3.00] | -0.75 [-3.50, 2.00] | 1.0000 |
| simulated_latency_ms | 2 | 7511.05 [6127.86, 8894.23] | 5774.57 [1720.49, 9828.65] | -1736.48 [-7173.75, 3700.79] | 1.0000 |
| parse_accuracy | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| dead_end_turns | 2 | 3.50 [1.00, 6.00] | 2.00 [0.00, 4.00] | -1.50 [-6.00, 3.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 5.00 [2.00, 8.00] | 3.50 [1.00, 6.00] | -1.50 [-7.00, 4.00] | 1.0000 |
| ladder_fire_turns | 2 | 0.00 [0.00, 0.00] | 0.50 [0.00, 1.00] | 0.50 [0.00, 1.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 3.50 [3.00, 4.00] | 3.00 [3.00, 3.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| negotiation_effectiveness | 1 | 2.00 [2.00, 2.00] | 2.00 [2.00, 2.00] | 0.00 [0.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 3.50 [3.00, 4.00] | 3.00 [2.00, 4.00] | -0.50 [-2.00, 1.00] | 1.0000 |
| customer_experience | 2 | 2.50 [2.00, 3.00] | 3.00 [2.00, 4.00] | 0.50 [-1.00, 2.00] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 7 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 6.50 [5.00, 8.00] | 5.00 [3.00, 7.00] | -1.50 [-5.00, 2.00] | 1.0000 |
| efficiency_ratio | 0 | — | — | — | — |
| simulated_latency_ms | 2 | 1266.73 [1162.02, 1371.45] | 1533.69 [1153.63, 1913.74] | 266.96 [-8.38, 542.30] | 1.0000 |
| parse_accuracy | 0 | — | — | — | — |
| dead_end_turns | 2 | 0.00 [0.00, 0.00] | 0.50 [0.00, 1.00] | 0.50 [0.00, 1.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 0.00 [0.00, 0.00] | 0.50 [0.00, 1.00] | 0.50 [0.00, 1.00] | 1.0000 |
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
| conversational_efficiency | 2 | 2.50 [2.00, 3.00] | 3.00 [1.00, 5.00] | 0.50 [-2.00, 3.00] | 1.0000 |
| customer_experience | 0 | — | — | — | — |
| recovery_quality | 0 | — | — | — | — |
