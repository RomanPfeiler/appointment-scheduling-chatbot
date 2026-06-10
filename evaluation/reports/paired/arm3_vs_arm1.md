# Paired comparison — `20260606_234404__nlp_arm3__e1626fa__representative_reduced` vs `20260606_222357__nlp_arm1__e1626fa__representative_reduced`

**Pairing:** 120 valid pairs out of 120 matched scenario-runs (excluded 0 pairs where either side had `termination=error` or missing derived metrics). Baseline-only keys: 0, candidate-only: 0.

## Overall (all tiers)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 120 | 6.31 [5.67, 6.95] | 6.64 [6.03, 7.29] | 0.33 [-0.16, 0.83] | 0.1613 |
| efficiency_ratio | 99 | 4.26 [2.92, 6.34] | 6.32 [3.99, 9.15] | 2.06 [-0.88, 5.14] | 0.0996 |
| simulated_latency_ms | 120 | 9607.06 [5993.78, 15586.80] | 15887.57 [9073.14, 24601.02] | 6280.52 [-2741.59, 15945.55] | 0.3220 |
| parse_accuracy | 99 | 0.43 [0.35, 0.51] | 0.46 [0.38, 0.55] | 0.04 [-0.04, 0.11] | 0.3249 |
| dead_end_turns | 120 | 3.12 [2.51, 3.78] | 3.23 [2.58, 3.92] | 0.10 [-0.47, 0.71] | 0.5916 |
| unsupported_facts | 120 | 0.30 [0.10, 0.57] | 0.43 [0.10, 0.92] | 0.13 [-0.28, 0.65] | 0.8433 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 120 | 63.3% [54.2%, 71.7%] | 59.2% [50.0%, 68.3%] | -4.2% [-10.8%, 2.5%] | 11/6 | 0.3323 |
| faithful | 120 | 94.2% [89.2%, 97.5%] | 94.2% [90.0%, 98.3%] | 0.0% [-5.0%, 5.0%] | 5/5 | 1.0000 |
| refusal_accepted | 120 | 15.8% [9.2%, 22.5%] | 16.7% [10.0%, 23.3%] | 0.8% [0.0%, 2.5%] | 0/1 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 120 | 4.23 [4.03, 4.42] | 4.58 [4.44, 4.72] | 0.35 [0.13, 0.58] | 0.0040** |
| negotiation_effectiveness | 87 | 3.11 [2.89, 3.36] | 3.13 [2.91, 3.36] | 0.01 [-0.21, 0.23] | 0.9145 |
| conversational_efficiency | 120 | 3.60 [3.39, 3.81] | 3.62 [3.40, 3.83] | 0.02 [-0.17, 0.19] | 0.8369 |
| customer_experience | 100 | 3.32 [3.07, 3.56] | 3.36 [3.09, 3.63] | 0.04 [-0.14, 0.21] | 0.7641 |
| recovery_quality | 57 | 3.44 [3.16, 3.72] | 3.46 [3.16, 3.77] | 0.02 [-0.26, 0.32] | 1.0000 |

## Tier 1 (n=10)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 10 | 3.20 [2.00, 5.30] | 4.20 [2.20, 7.10] | 1.00 [0.00, 3.00] | 1.0000 |
| efficiency_ratio | 10 | 2.50 [1.20, 4.70] | 3.40 [1.20, 6.60] | 0.90 [-0.30, 3.00] | 1.0000 |
| simulated_latency_ms | 10 | 3236.28 [2033.71, 5231.94] | 3919.65 [2053.77, 6513.68] | 683.37 [-344.58, 2420.84] | 0.6835 |
| parse_accuracy | 10 | 0.60 [0.40, 0.80] | 0.55 [0.30, 0.75] | -0.05 [-0.15, 0.00] | 1.0000 |
| dead_end_turns | 10 | 1.20 [0.00, 3.60] | 2.20 [0.00, 5.40] | 1.00 [0.00, 3.00] | 1.0000 |
| unsupported_facts | 10 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 10 | 90.0% [70.0%, 100.0%] | 80.0% [50.0%, 100.0%] | -10.0% [-30.0%, 0.0%] | 1/0 | 1.0000 |
| faithful | 10 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 10 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 10 | 4.60 [4.00, 5.00] | 5.00 [5.00, 5.00] | 0.40 [0.00, 1.10] | 0.3711 |
| negotiation_effectiveness | 5 | 4.20 [3.00, 5.00] | 3.40 [2.40, 4.40] | -0.80 [-2.00, 0.00] | 0.3711 |
| conversational_efficiency | 10 | 4.60 [4.00, 5.00] | 4.40 [3.50, 5.00] | -0.20 [-0.60, 0.00] | 1.0000 |
| customer_experience | 10 | 4.60 [4.00, 5.00] | 4.40 [3.50, 5.00] | -0.20 [-0.60, 0.00] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 2 (n=10)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 10 | 7.50 [4.70, 10.20] | 8.00 [5.20, 10.70] | 0.50 [-0.60, 1.90] | 0.5807 |
| efficiency_ratio | 9 | 5.78 [2.67, 8.89] | 5.00 [2.44, 7.67] | -0.78 [-3.44, 1.22] | 1.0000 |
| simulated_latency_ms | 10 | 7774.11 [4147.31, 11741.23] | 6210.18 [3945.92, 8645.64] | -1563.93 [-5073.31, 1023.87] | 0.6835 |
| parse_accuracy | 9 | 0.50 [0.22, 0.78] | 0.56 [0.28, 0.83] | 0.06 [0.00, 0.17] | 1.0000 |
| dead_end_turns | 10 | 4.70 [1.60, 7.90] | 2.50 [0.30, 5.30] | -2.20 [-5.00, 0.30] | 0.2476 |
| unsupported_facts | 10 | 0.00 [0.00, 0.00] | 0.40 [0.00, 1.20] | 0.40 [0.00, 1.20] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 10 | 60.0% [30.0%, 90.0%] | 50.0% [20.0%, 80.0%] | -10.0% [-40.0%, 20.0%] | 2/1 | 1.0000 |
| faithful | 10 | 100.0% [100.0%, 100.0%] | 90.0% [70.0%, 100.0%] | -10.0% [-30.0%, 0.0%] | 1/0 | 1.0000 |
| refusal_accepted | 10 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 10 | 4.40 [3.70, 4.90] | 4.50 [3.80, 5.00] | 0.10 [-0.90, 1.10] | 0.9153 |
| negotiation_effectiveness | 9 | 3.22 [2.33, 4.22] | 2.89 [2.00, 3.78] | -0.33 [-0.89, 0.11] | 0.3447 |
| conversational_efficiency | 10 | 3.50 [2.70, 4.40] | 3.30 [2.40, 4.20] | -0.20 [-0.90, 0.30] | 1.0000 |
| customer_experience | 10 | 3.50 [2.70, 4.40] | 3.40 [2.60, 4.30] | -0.10 [-0.60, 0.30] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 3 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 6.75 [5.25, 8.40] | 6.85 [5.25, 8.50] | 0.10 [-1.15, 1.25] | 0.5966 |
| efficiency_ratio | 20 | 2.92 [2.17, 3.83] | 6.12 [2.48, 12.78] | 3.20 [-0.27, 9.55] | 0.2471 |
| simulated_latency_ms | 20 | 6868.23 [5227.80, 8867.91] | 18733.14 [5995.46, 42523.56] | 11864.91 [-305.82, 34986.29] | 0.4009 |
| parse_accuracy | 20 | 0.38 [0.25, 0.53] | 0.45 [0.28, 0.62] | 0.08 [-0.03, 0.18] | 0.2330 |
| dead_end_turns | 20 | 3.95 [2.55, 5.55] | 3.90 [2.40, 5.50] | -0.05 [-1.15, 1.20] | 0.7178 |
| unsupported_facts | 20 | 0.30 [0.00, 0.90] | 0.10 [0.00, 0.30] | -0.20 [-0.60, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 70.0% [50.0%, 90.0%] | 75.0% [55.0%, 95.0%] | 5.0% [-10.0%, 20.0%] | 1/2 | 1.0000 |
| faithful | 20 | 95.0% [85.0%, 100.0%] | 95.0% [85.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.45 [3.85, 4.90] | 4.65 [4.30, 4.90] | 0.20 [-0.40, 0.85] | 0.6056 |
| negotiation_effectiveness | 20 | 3.70 [3.25, 4.15] | 3.85 [3.40, 4.25] | 0.15 [-0.25, 0.60] | 0.6270 |
| conversational_efficiency | 20 | 3.90 [3.35, 4.40] | 4.15 [3.70, 4.55] | 0.25 [-0.25, 0.75] | 0.3739 |
| customer_experience | 20 | 3.60 [3.10, 4.10] | 3.85 [3.25, 4.40] | 0.25 [-0.20, 0.70] | 0.3557 |
| recovery_quality | 20 | 3.90 [3.35, 4.40] | 4.15 [3.70, 4.55] | 0.25 [-0.25, 0.80] | 0.4775 |

## Tier 4 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 6.60 [5.25, 7.95] | 7.05 [5.50, 8.60] | 0.45 [-0.90, 1.90] | 0.6869 |
| efficiency_ratio | 20 | 6.78 [2.10, 15.50] | 6.65 [2.50, 13.82] | -0.12 [-11.23, 9.95] | 0.5890 |
| simulated_latency_ms | 20 | 22568.24 [5278.71, 55489.23] | 19999.49 [5655.40, 46081.39] | -2568.75 [-46107.25, 36188.60] | 0.9256 |
| parse_accuracy | 20 | 0.33 [0.15, 0.50] | 0.47 [0.25, 0.70] | 0.15 [0.00, 0.33] | 0.1236 |
| dead_end_turns | 20 | 3.45 [2.15, 4.80] | 4.00 [2.40, 5.75] | 0.55 [-0.95, 2.10] | 0.5503 |
| unsupported_facts | 20 | 0.60 [0.00, 1.40] | 1.50 [0.00, 4.10] | 0.90 [-0.80, 3.40] | 0.8551 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 90.0% [75.0%, 100.0%] | 70.0% [50.0%, 90.0%] | -20.0% [-40.0%, -5.0%] | 4/0 | 0.1250 |
| faithful | 20 | 85.0% [70.0%, 100.0%] | 90.0% [75.0%, 100.0%] | 5.0% [-10.0%, 20.0%] | 1/2 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.35 [3.95, 4.70] | 4.90 [4.75, 5.00] | 0.55 [0.15, 0.95] | 0.0279* |
| negotiation_effectiveness | 17 | 3.59 [3.18, 4.00] | 3.00 [2.53, 3.47] | -0.59 [-1.18, -0.06] | 0.0692 |
| conversational_efficiency | 20 | 3.95 [3.55, 4.35] | 3.75 [3.20, 4.25] | -0.20 [-0.65, 0.25] | 0.4320 |
| customer_experience | 20 | 3.70 [3.25, 4.10] | 3.45 [2.85, 4.05] | -0.25 [-0.75, 0.25] | 0.3122 |
| recovery_quality | 17 | 3.82 [3.41, 4.24] | 3.35 [2.76, 3.94] | -0.47 [-1.06, 0.12] | 0.1460 |

## Tier 5 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 8.15 [6.95, 9.45] | 7.90 [6.90, 9.00] | -0.25 [-1.70, 1.20] | 0.6894 |
| efficiency_ratio | 20 | 3.20 [2.45, 4.13] | 8.67 [2.27, 18.58] | 5.47 [-0.95, 15.17] | 0.6946 |
| simulated_latency_ms | 20 | 11047.03 [8732.52, 13804.57] | 30051.88 [7238.95, 63968.92] | 19004.86 [-3524.06, 52150.33] | 0.3411 |
| parse_accuracy | 20 | 0.45 [0.25, 0.65] | 0.47 [0.30, 0.68] | 0.02 [-0.15, 0.20] | 0.7921 |
| dead_end_turns | 20 | 4.30 [2.90, 5.80] | 3.30 [2.10, 4.65] | -1.00 [-2.70, 0.65] | 0.2094 |
| unsupported_facts | 20 | 0.30 [0.00, 0.90] | 0.60 [0.00, 1.60] | 0.30 [-0.70, 1.40] | 0.7893 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 70.0% [50.0%, 90.0%] | 75.0% [55.0%, 95.0%] | 5.0% [-15.0%, 25.0%] | 2/3 | 1.0000 |
| faithful | 20 | 95.0% [85.0%, 100.0%] | 90.0% [75.0%, 100.0%] | -5.0% [-25.0%, 10.0%] | 2/1 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 3.75 [3.25, 4.25] | 4.10 [3.65, 4.50] | 0.35 [-0.20, 0.90] | 0.2506 |
| negotiation_effectiveness | 20 | 2.25 [2.00, 2.50] | 2.50 [2.25, 2.75] | 0.25 [0.00, 0.50] | 0.1096 |
| conversational_efficiency | 20 | 2.80 [2.45, 3.10] | 2.80 [2.45, 3.15] | 0.00 [-0.35, 0.35] | 0.9646 |
| customer_experience | 20 | 2.05 [1.85, 2.25] | 2.25 [1.90, 2.60] | 0.20 [-0.15, 0.55] | 0.3075 |
| recovery_quality | 20 | 2.65 [2.35, 2.95] | 2.85 [2.45, 3.25] | 0.20 [-0.20, 0.55] | 0.3363 |

## Tier 6 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 6.50 [5.05, 8.05] | 7.35 [5.75, 8.90] | 0.85 [0.05, 1.70] | 0.0746 |
| efficiency_ratio | 20 | 4.33 [2.25, 7.05] | 5.90 [3.02, 10.40] | 1.58 [-1.15, 4.90] | 0.0494* |
| simulated_latency_ms | 20 | 9462.57 [5237.53, 14863.38] | 15864.40 [6825.65, 31470.95] | 6401.83 [-1602.59, 18952.41] | 0.0290* |
| parse_accuracy | 20 | 0.45 [0.28, 0.62] | 0.38 [0.17, 0.60] | -0.08 [-0.28, 0.15] | 0.5242 |
| dead_end_turns | 20 | 3.40 [2.00, 4.95] | 5.00 [3.20, 6.85] | 1.60 [0.50, 2.80] | 0.0150* |
| unsupported_facts | 20 | 0.60 [0.00, 1.65] | 0.00 [0.00, 0.00] | -0.60 [-1.65, 0.00] | 0.3711 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 75.0% [55.0%, 90.0%] | 70.0% [50.0%, 90.0%] | -5.0% [-15.0%, 0.0%] | 1/0 | 1.0000 |
| faithful | 20 | 90.0% [75.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 10.0% [0.0%, 25.0%] | 0/2 | 0.5000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.30 [3.90, 4.65] | 4.50 [4.20, 4.75] | 0.20 [-0.20, 0.65] | 0.3889 |
| negotiation_effectiveness | 16 | 2.56 [2.19, 3.00] | 3.19 [2.75, 3.62] | 0.62 [0.25, 1.00] | 0.0192* |
| conversational_efficiency | 20 | 3.55 [3.05, 4.05] | 3.60 [3.10, 4.10] | 0.05 [-0.30, 0.35] | 0.9300 |
| customer_experience | 20 | 3.20 [2.70, 3.70] | 3.35 [2.85, 3.85] | 0.15 [-0.10, 0.40] | 0.2986 |
| recovery_quality | 0 | — | — | — | — |

## Tier 7 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 4.50 [3.70, 5.60] | 4.60 [4.15, 5.05] | 0.10 [-1.05, 1.05] | 0.3073 |
| efficiency_ratio | 0 | — | — | — | — |
| simulated_latency_ms | 20 | 2191.10 [1149.12, 3499.56] | 5611.62 [1786.79, 12436.63] | 3420.53 [-948.76, 10846.02] | 0.3048 |
| parse_accuracy | 0 | — | — | — | — |
| dead_end_turns | 20 | 0.70 [0.25, 1.30] | 0.80 [0.40, 1.25] | 0.10 [-0.45, 0.55] | 0.5862 |
| unsupported_facts | 20 | 0.00 [0.00, 0.00] | 0.20 [0.00, 0.60] | 0.20 [0.00, 0.60] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 20 | 100.0% [100.0%, 100.0%] | 95.0% [85.0%, 100.0%] | -5.0% [-15.0%, 0.0%] | 1/0 | 1.0000 |
| refusal_accepted | 20 | 95.0% [85.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 5.0% [0.0%, 15.0%] | 0/1 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.05 [3.45, 4.60] | 4.60 [4.35, 4.85] | 0.55 [0.00, 1.15] | 0.1126 |
| negotiation_effectiveness | 0 | — | — | — | — |
| conversational_efficiency | 20 | 3.35 [2.95, 3.80] | 3.55 [3.20, 3.85] | 0.20 [-0.35, 0.70] | 0.3518 |
| customer_experience | 0 | — | — | — | — |
| recovery_quality | 0 | — | — | — | — |
