# Paired comparison — `20260607_014848__nlp_arm2__e1626fa__representative_reduced` vs `20260606_234404__nlp_arm3__e1626fa__representative_reduced`

**Pairing:** 119 valid pairs out of 120 matched scenario-runs (excluded 1 pairs where either side had `termination=error` or missing derived metrics). Baseline-only keys: 0, candidate-only: 0.

## Overall (all tiers)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 119 | 6.63 [6.01, 7.28] | 7.14 [6.50, 7.82] | 0.51 [-0.08, 1.13] | 0.0843 |
| efficiency_ratio | 98 | 6.35 [4.04, 9.24] | 8.97 [5.71, 12.78] | 2.62 [-1.82, 7.27] | 0.3054 |
| simulated_latency_ms | 119 | 15958.94 [8968.94, 24672.24] | 23396.45 [13028.80, 36399.09] | 7437.51 [-6084.36, 21956.04] | 0.4981 |
| parse_accuracy | 98 | 0.47 [0.38, 0.56] | 0.47 [0.38, 0.56] | 0.00 [-0.07, 0.07] | 0.9623 |
| dead_end_turns | 119 | 3.20 [2.56, 3.90] | 3.38 [2.73, 4.07] | 0.18 [-0.59, 0.92] | 0.6237 |
| unsupported_facts | 119 | 0.44 [0.10, 0.91] | 0.23 [0.05, 0.45] | -0.21 [-0.72, 0.21] | 0.6093 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 119 | 58.8% [49.6%, 68.1%] | 54.6% [45.4%, 63.9%] | -4.2% [-12.6%, 4.2%] | 16/11 | 0.4421 |
| faithful | 119 | 94.1% [89.9%, 97.5%] | 95.8% [91.6%, 99.2%] | 1.7% [-4.2%, 7.6%] | 5/7 | 0.7744 |
| refusal_accepted | 119 | 16.8% [10.1%, 23.5%] | 16.8% [10.1%, 23.5%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 119 | 4.58 [4.44, 4.71] | 4.43 [4.24, 4.60] | -0.15 [-0.38, 0.07] | 0.2494 |
| negotiation_effectiveness | 86 | 3.13 [2.91, 3.36] | 2.84 [2.63, 3.06] | -0.29 [-0.56, -0.02] | 0.0363* |
| conversational_efficiency | 119 | 3.62 [3.40, 3.83] | 3.36 [3.14, 3.58] | -0.26 [-0.50, -0.03] | 0.0263* |
| customer_experience | 99 | 3.36 [3.09, 3.62] | 3.09 [2.83, 3.34] | -0.27 [-0.52, -0.02] | 0.0409* |
| recovery_quality | 57 | 3.46 [3.16, 3.77] | 3.05 [2.77, 3.33] | -0.40 [-0.74, -0.07] | 0.0223* |

## Tier 1 (n=10)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 10 | 4.20 [2.20, 7.10] | 3.30 [2.10, 5.30] | -0.90 [-2.70, 0.00] | 1.0000 |
| efficiency_ratio | 10 | 3.40 [1.20, 6.60] | 2.20 [1.10, 4.00] | -1.20 [-3.20, 0.00] | 0.3711 |
| simulated_latency_ms | 10 | 3919.65 [2053.77, 6513.68] | 2748.28 [1842.76, 4248.95] | -1171.37 [-2980.92, -50.64] | 0.3590 |
| parse_accuracy | 10 | 0.55 [0.30, 0.75] | 0.50 [0.30, 0.70] | -0.05 [-0.15, 0.00] | 1.0000 |
| dead_end_turns | 10 | 2.20 [0.00, 5.40] | 1.00 [0.00, 2.80] | -1.20 [-3.40, 0.00] | 0.3711 |
| unsupported_facts | 10 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 10 | 80.0% [50.0%, 100.0%] | 90.0% [70.0%, 100.0%] | 10.0% [0.0%, 30.0%] | 0/1 | 1.0000 |
| faithful | 10 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 10 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 10 | 5.00 [5.00, 5.00] | 4.90 [4.70, 5.00] | -0.10 [-0.30, 0.00] | 1.0000 |
| negotiation_effectiveness | 5 | 3.40 [2.40, 4.40] | 3.80 [2.80, 4.60] | 0.40 [0.00, 1.20] | 1.0000 |
| conversational_efficiency | 10 | 4.40 [3.50, 5.00] | 4.70 [4.10, 5.00] | 0.30 [0.00, 0.90] | 1.0000 |
| customer_experience | 10 | 4.40 [3.50, 5.00] | 4.70 [4.10, 5.00] | 0.30 [0.00, 0.90] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 2 (n=10)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 10 | 8.00 [5.20, 10.70] | 10.20 [8.00, 12.00] | 2.20 [-0.80, 5.20] | 0.2084 |
| efficiency_ratio | 9 | 5.00 [2.44, 7.67] | 19.00 [6.44, 37.89] | 14.00 [0.44, 34.33] | 0.1225 |
| simulated_latency_ms | 10 | 6210.18 [3945.92, 8645.64] | 19657.50 [6921.16, 36416.01] | 13447.32 [-77.89, 31215.01] | 0.1536 |
| parse_accuracy | 9 | 0.56 [0.28, 0.83] | 0.78 [0.44, 1.00] | 0.22 [0.00, 0.44] | 0.1736 |
| dead_end_turns | 10 | 2.50 [0.30, 5.30] | 5.10 [2.10, 8.30] | 2.60 [-2.50, 7.40] | 0.3424 |
| unsupported_facts | 10 | 0.40 [0.00, 1.20] | 0.00 [0.00, 0.00] | -0.40 [-1.20, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 10 | 50.0% [20.0%, 80.0%] | 30.0% [0.0%, 60.0%] | -20.0% [-60.0%, 20.0%] | 3/1 | 0.6250 |
| faithful | 10 | 90.0% [70.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 10.0% [0.0%, 30.0%] | 0/1 | 1.0000 |
| refusal_accepted | 10 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 10 | 4.50 [3.80, 5.00] | 4.80 [4.40, 5.00] | 0.30 [-0.40, 1.10] | 0.5862 |
| negotiation_effectiveness | 9 | 2.89 [2.00, 3.78] | 2.11 [2.00, 2.33] | -0.78 [-1.78, 0.22] | 0.2207 |
| conversational_efficiency | 10 | 3.30 [2.40, 4.20] | 2.70 [2.20, 3.40] | -0.60 [-1.70, 0.40] | 0.3456 |
| customer_experience | 10 | 3.40 [2.60, 4.30] | 2.60 [2.10, 3.20] | -0.80 [-1.80, 0.10] | 0.1983 |
| recovery_quality | 0 | — | — | — | — |

## Tier 3 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 6.85 [5.25, 8.50] | 8.25 [6.60, 9.90] | 1.40 [-0.05, 3.00] | 0.1018 |
| efficiency_ratio | 20 | 6.12 [2.48, 12.78] | 10.47 [4.15, 18.65] | 4.35 [-5.53, 13.80] | 0.2328 |
| simulated_latency_ms | 20 | 18733.14 [5995.46, 42523.56] | 33132.37 [9738.92, 62980.47] | 14399.24 [-22398.53, 50593.02] | 0.5135 |
| parse_accuracy | 20 | 0.45 [0.28, 0.62] | 0.47 [0.30, 0.65] | 0.02 [-0.13, 0.18] | 0.8902 |
| dead_end_turns | 20 | 3.90 [2.40, 5.50] | 4.95 [3.20, 6.80] | 1.05 [-0.55, 2.75] | 0.2935 |
| unsupported_facts | 20 | 0.10 [0.00, 0.30] | 0.30 [0.00, 0.90] | 0.20 [-0.30, 0.90] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 75.0% [55.0%, 95.0%] | 55.0% [35.0%, 75.0%] | -20.0% [-40.0%, -5.0%] | 4/0 | 0.1250 |
| faithful | 20 | 95.0% [85.0%, 100.0%] | 95.0% [85.0%, 100.0%] | 0.0% [-15.0%, 15.0%] | 1/1 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.65 [4.30, 4.90] | 4.85 [4.60, 5.00] | 0.20 [-0.20, 0.60] | 0.3869 |
| negotiation_effectiveness | 20 | 3.85 [3.40, 4.25] | 3.05 [2.60, 3.50] | -0.80 [-1.40, -0.20] | 0.0249* |
| conversational_efficiency | 20 | 4.15 [3.70, 4.55] | 3.50 [3.00, 4.05] | -0.65 [-1.30, 0.00] | 0.0561 |
| customer_experience | 20 | 3.85 [3.25, 4.40] | 3.00 [2.55, 3.50] | -0.85 [-1.40, -0.30] | 0.0134* |
| recovery_quality | 20 | 4.15 [3.70, 4.55] | 3.30 [2.85, 3.75] | -0.85 [-1.40, -0.25] | 0.0176* |

## Tier 4 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 7.05 [5.50, 8.60] | 6.75 [5.25, 8.30] | -0.30 [-1.80, 1.15] | 0.9718 |
| efficiency_ratio | 20 | 6.65 [2.50, 13.82] | 6.15 [2.33, 12.85] | -0.50 [-9.23, 8.57] | 0.4209 |
| simulated_latency_ms | 20 | 19999.49 [5655.40, 46081.39] | 18481.65 [5459.48, 42631.33] | -1517.84 [-35539.95, 32639.14] | 0.5883 |
| parse_accuracy | 20 | 0.47 [0.25, 0.70] | 0.45 [0.25, 0.65] | -0.02 [-0.17, 0.12] | 1.0000 |
| dead_end_turns | 20 | 4.00 [2.40, 5.75] | 4.00 [2.40, 5.75] | 0.00 [-1.80, 1.80] | 0.9748 |
| unsupported_facts | 20 | 1.50 [0.00, 4.10] | 0.00 [0.00, 0.00] | -1.50 [-4.10, 0.00] | 0.3711 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 70.0% [50.0%, 90.0%] | 75.0% [55.0%, 90.0%] | 5.0% [-20.0%, 25.0%] | 2/3 | 1.0000 |
| faithful | 20 | 90.0% [75.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 10.0% [0.0%, 25.0%] | 0/2 | 0.5000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.90 [4.75, 5.00] | 4.35 [3.95, 4.70] | -0.55 [-1.00, -0.15] | 0.0326* |
| negotiation_effectiveness | 17 | 3.00 [2.53, 3.47] | 3.18 [2.71, 3.71] | 0.18 [-0.47, 0.82] | 0.7502 |
| conversational_efficiency | 20 | 3.75 [3.20, 4.25] | 3.50 [3.00, 4.00] | -0.25 [-0.65, 0.10] | 0.2117 |
| customer_experience | 20 | 3.45 [2.85, 4.05] | 3.35 [2.80, 3.90] | -0.10 [-0.65, 0.45] | 0.5500 |
| recovery_quality | 17 | 3.35 [2.76, 3.94] | 3.29 [2.82, 3.82] | -0.06 [-0.65, 0.53] | 0.8398 |

## Tier 5 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 7.90 [6.90, 9.00] | 8.75 [7.50, 9.95] | 0.85 [-0.65, 2.20] | 0.2642 |
| efficiency_ratio | 20 | 8.67 [2.27, 18.58] | 9.13 [3.12, 17.35] | 0.47 [-11.73, 11.72] | 0.3043 |
| simulated_latency_ms | 20 | 30051.88 [7238.95, 63968.92] | 46482.34 [10641.62, 94858.89] | 16430.46 [-36015.69, 74898.94] | 0.1851 |
| parse_accuracy | 20 | 0.47 [0.30, 0.68] | 0.38 [0.20, 0.55] | -0.10 [-0.25, 0.00] | 0.3458 |
| dead_end_turns | 20 | 3.30 [2.10, 4.65] | 3.75 [2.70, 4.85] | 0.45 [-1.00, 1.75] | 0.4836 |
| unsupported_facts | 20 | 0.60 [0.00, 1.60] | 0.30 [0.00, 0.90] | -0.30 [-1.40, 0.70] | 0.7893 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 75.0% [55.0%, 95.0%] | 65.0% [45.0%, 85.0%] | -10.0% [-35.0%, 20.0%] | 5/3 | 0.7266 |
| faithful | 20 | 90.0% [75.0%, 100.0%] | 95.0% [85.0%, 100.0%] | 5.0% [-10.0%, 25.0%] | 1/2 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.10 [3.65, 4.50] | 3.95 [3.40, 4.45] | -0.15 [-0.75, 0.50] | 0.6414 |
| negotiation_effectiveness | 20 | 2.50 [2.25, 2.75] | 2.45 [2.10, 2.80] | -0.05 [-0.40, 0.30] | 0.8514 |
| conversational_efficiency | 20 | 2.80 [2.45, 3.15] | 2.55 [2.15, 3.00] | -0.25 [-0.80, 0.30] | 0.3012 |
| customer_experience | 20 | 2.25 [1.90, 2.60] | 2.15 [1.75, 2.55] | -0.10 [-0.60, 0.40] | 0.7426 |
| recovery_quality | 20 | 2.85 [2.45, 3.25] | 2.60 [2.15, 3.05] | -0.25 [-0.75, 0.30] | 0.3136 |

## Tier 6 (n=19)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 19 | 7.32 [5.68, 8.95] | 7.42 [5.79, 9.05] | 0.11 [-1.47, 1.84] | 0.9155 |
| efficiency_ratio | 19 | 6.03 [3.03, 10.89] | 8.97 [2.61, 20.58] | 2.95 [-6.13, 15.61] | 0.7557 |
| simulated_latency_ms | 19 | 16310.17 [6798.42, 32949.19] | 28886.86 [6194.97, 71786.90] | 12576.69 [-22171.52, 61172.71] | 0.7936 |
| parse_accuracy | 19 | 0.39 [0.18, 0.61] | 0.42 [0.24, 0.61] | 0.03 [-0.18, 0.24] | 0.8514 |
| dead_end_turns | 19 | 4.95 [3.11, 6.89] | 3.74 [2.26, 5.32] | -1.21 [-3.21, 0.89] | 0.2714 |
| unsupported_facts | 19 | 0.00 [0.00, 0.00] | 0.53 [0.00, 1.42] | 0.53 [0.00, 1.42] | 0.3711 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 19 | 68.4% [47.4%, 89.5%] | 73.7% [52.6%, 89.5%] | 5.3% [-15.8%, 26.3%] | 2/3 | 1.0000 |
| faithful | 19 | 100.0% [100.0%, 100.0%] | 89.5% [73.7%, 100.0%] | -10.5% [-26.3%, 0.0%] | 2/0 | 0.5000 |
| refusal_accepted | 19 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 19 | 4.47 [4.16, 4.74] | 4.58 [4.26, 4.84] | 0.11 [-0.21, 0.47] | 0.5877 |
| negotiation_effectiveness | 15 | 3.20 [2.73, 3.67] | 2.80 [2.27, 3.33] | -0.40 [-1.00, 0.20] | 0.2439 |
| conversational_efficiency | 19 | 3.63 [3.11, 4.16] | 3.47 [2.84, 4.11] | -0.16 [-0.89, 0.58] | 0.6963 |
| customer_experience | 19 | 3.37 [2.84, 3.89] | 3.32 [2.74, 3.89] | -0.05 [-0.63, 0.53] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 7 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 4.60 [4.15, 5.05] | 4.95 [4.35, 5.60] | 0.35 [-0.50, 1.25] | 0.5786 |
| efficiency_ratio | 0 | — | — | — | — |
| simulated_latency_ms | 20 | 5611.62 [1786.79, 12436.63] | 2467.12 [1684.88, 3392.55] | -3144.51 [-10557.51, 1213.95] | 0.8666 |
| parse_accuracy | 0 | — | — | — | — |
| dead_end_turns | 20 | 0.80 [0.40, 1.25] | 0.80 [0.35, 1.35] | 0.00 [-0.55, 0.60] | 0.9313 |
| unsupported_facts | 20 | 0.20 [0.00, 0.60] | 0.25 [0.00, 0.75] | 0.05 [-0.60, 0.75] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 20 | 95.0% [85.0%, 100.0%] | 95.0% [85.0%, 100.0%] | 0.0% [-15.0%, 15.0%] | 1/1 | 1.0000 |
| refusal_accepted | 20 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.60 [4.35, 4.85] | 4.00 [3.35, 4.60] | -0.60 [-1.35, 0.10] | 0.2442 |
| negotiation_effectiveness | 0 | — | — | — | — |
| conversational_efficiency | 20 | 3.55 [3.20, 3.85] | 3.45 [3.00, 3.85] | -0.10 [-0.65, 0.50] | 0.6037 |
| customer_experience | 0 | — | — | — | — |
| recovery_quality | 0 | — | — | — | — |
