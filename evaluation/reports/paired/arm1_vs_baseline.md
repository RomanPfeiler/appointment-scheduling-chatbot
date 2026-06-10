# Paired comparison — `20260606_222357__nlp_arm1__e1626fa__representative_reduced` vs `20260606_205242__baseline__e1626fa__representative_reduced`

**Pairing:** 120 valid pairs out of 120 matched scenario-runs (excluded 0 pairs where either side had `termination=error` or missing derived metrics). Baseline-only keys: 0, candidate-only: 0.

## Overall (all tiers)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 120 | 6.37 [5.73, 7.05] | 6.31 [5.67, 6.95] | -0.06 [-0.72, 0.61] | 0.9944 |
| efficiency_ratio | 99 | 4.63 [3.18, 6.58] | 4.33 [3.01, 6.41] | -0.30 [-2.67, 2.28] | 0.7117 |
| simulated_latency_ms | 120 | 10072.43 [6071.93, 15721.83] | 9607.06 [5993.78, 15586.80] | -465.37 [-7446.39, 7085.89] | 0.7452 |
| parse_accuracy | 99 | 0.41 [0.33, 0.49] | 0.44 [0.36, 0.52] | 0.03 [-0.05, 0.09] | 0.4694 |
| dead_end_turns | 120 | 3.15 [2.48, 3.86] | 3.12 [2.51, 3.78] | -0.02 [-0.72, 0.69] | 0.8307 |
| unsupported_facts | 120 | 0.58 [0.12, 1.32] | 0.30 [0.10, 0.57] | -0.28 [-1.08, 0.28] | 0.6997 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 120 | 62.5% [53.3%, 70.8%] | 63.3% [54.2%, 71.7%] | 0.8% [-7.5%, 8.3%] | 11/12 | 1.0000 |
| faithful | 120 | 95.0% [90.8%, 98.3%] | 94.2% [89.2%, 97.5%] | -0.8% [-6.7%, 5.0%] | 7/6 | 1.0000 |
| refusal_accepted | 120 | 16.7% [10.0%, 23.3%] | 15.8% [9.2%, 22.5%] | -0.8% [-2.5%, 0.0%] | 1/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 120 | 4.60 [4.45, 4.74] | 4.23 [4.03, 4.42] | -0.37 [-0.60, -0.15] | 0.0022** |
| negotiation_effectiveness | 89 | 3.33 [3.09, 3.57] | 3.12 [2.89, 3.36] | -0.20 [-0.49, 0.09] | 0.1887 |
| conversational_efficiency | 120 | 3.73 [3.51, 3.94] | 3.60 [3.39, 3.81] | -0.12 [-0.37, 0.11] | 0.2512 |
| customer_experience | 100 | 3.33 [3.06, 3.59] | 3.32 [3.07, 3.56] | -0.01 [-0.28, 0.26] | 0.9060 |
| recovery_quality | 57 | 3.47 [3.18, 3.79] | 3.44 [3.16, 3.72] | -0.04 [-0.35, 0.30] | 0.7289 |

## Tier 1 (n=10)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 10 | 5.20 [2.70, 8.20] | 3.20 [2.00, 5.30] | -2.00 [-4.70, 0.00] | 0.1696 |
| efficiency_ratio | 10 | 5.10 [1.40, 10.20] | 2.50 [1.20, 4.70] | -2.60 [-6.00, 0.00] | 0.1362 |
| simulated_latency_ms | 10 | 6004.89 [2584.76, 10417.76] | 3236.28 [2033.71, 5231.94] | -2768.61 [-5666.96, -415.29] | 0.1263 |
| parse_accuracy | 10 | 0.50 [0.25, 0.75] | 0.60 [0.40, 0.80] | 0.10 [-0.10, 0.35] | 0.5862 |
| dead_end_turns | 10 | 2.50 [0.00, 6.00] | 1.20 [0.00, 3.60] | -1.30 [-3.80, 0.00] | 0.3711 |
| unsupported_facts | 10 | 1.30 [0.00, 3.90] | 0.00 [0.00, 0.00] | -1.30 [-3.90, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 10 | 70.0% [40.0%, 100.0%] | 90.0% [70.0%, 100.0%] | 20.0% [0.0%, 50.0%] | 0/2 | 0.5000 |
| faithful | 10 | 90.0% [70.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 10.0% [0.0%, 30.0%] | 0/1 | 1.0000 |
| refusal_accepted | 10 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 10 | 4.70 [4.10, 5.00] | 4.60 [4.00, 5.00] | -0.10 [-1.00, 0.80] | 1.0000 |
| negotiation_effectiveness | 5 | 3.00 [1.80, 4.20] | 4.20 [3.00, 5.00] | 1.20 [-0.40, 3.00] | 0.4227 |
| conversational_efficiency | 10 | 3.80 [2.80, 4.70] | 4.60 [4.00, 5.00] | 0.80 [0.00, 1.60] | 0.1736 |
| customer_experience | 10 | 3.80 [2.80, 4.70] | 4.60 [4.00, 5.00] | 0.80 [0.00, 1.60] | 0.1736 |
| recovery_quality | 0 | — | — | — | — |

## Tier 2 (n=10)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 10 | 7.50 [4.80, 10.20] | 7.50 [4.70, 10.20] | 0.00 [-3.70, 3.50] | 0.9163 |
| efficiency_ratio | 10 | 6.30 [3.80, 9.10] | 6.10 [3.20, 9.00] | -0.20 [-4.50, 3.90] | 1.0000 |
| simulated_latency_ms | 10 | 7846.42 [4993.41, 11535.97] | 7774.11 [4147.31, 11741.23] | -72.31 [-5782.31, 4699.11] | 0.7598 |
| parse_accuracy | 10 | 0.50 [0.20, 0.75] | 0.55 [0.30, 0.80] | 0.05 [-0.10, 0.20] | 0.7728 |
| dead_end_turns | 10 | 5.30 [2.50, 8.30] | 4.70 [1.60, 7.90] | -0.60 [-4.90, 3.60] | 0.7661 |
| unsupported_facts | 10 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 10 | 50.0% [20.0%, 80.0%] | 60.0% [30.0%, 90.0%] | 10.0% [-20.0%, 40.0%] | 1/2 | 1.0000 |
| faithful | 10 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 10 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 10 | 4.90 [4.70, 5.00] | 4.40 [3.70, 4.90] | -0.50 [-1.20, 0.10] | 0.2031 |
| negotiation_effectiveness | 9 | 3.33 [2.56, 4.22] | 3.22 [2.33, 4.22] | -0.11 [-1.22, 1.00] | 1.0000 |
| conversational_efficiency | 10 | 3.60 [2.70, 4.40] | 3.50 [2.70, 4.40] | -0.10 [-1.30, 1.10] | 1.0000 |
| customer_experience | 10 | 3.50 [2.60, 4.40] | 3.50 [2.70, 4.40] | 0.00 [-1.20, 1.20] | 0.9139 |
| recovery_quality | 0 | — | — | — | — |

## Tier 3 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 7.10 [5.60, 8.75] | 6.75 [5.25, 8.40] | -0.35 [-1.95, 1.30] | 0.5004 |
| efficiency_ratio | 20 | 8.65 [2.55, 17.27] | 2.92 [2.17, 3.83] | -5.73 [-14.22, 0.20] | 0.3584 |
| simulated_latency_ms | 20 | 27937.59 [5890.54, 59962.20] | 6868.23 [5227.80, 8867.91] | -21069.36 [-52946.57, 427.66] | 0.4898 |
| parse_accuracy | 20 | 0.42 [0.28, 0.57] | 0.38 [0.25, 0.53] | -0.05 [-0.12, 0.00] | 0.3458 |
| dead_end_turns | 20 | 3.95 [2.40, 5.70] | 3.95 [2.55, 5.55] | 0.00 [-1.95, 1.95] | 0.8640 |
| unsupported_facts | 20 | 0.00 [0.00, 0.00] | 0.30 [0.00, 0.90] | 0.30 [0.00, 0.90] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 65.0% [45.0%, 85.0%] | 70.0% [50.0%, 90.0%] | 5.0% [-15.0%, 25.0%] | 2/3 | 1.0000 |
| faithful | 20 | 100.0% [100.0%, 100.0%] | 95.0% [85.0%, 100.0%] | -5.0% [-15.0%, 0.0%] | 1/0 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.85 [4.55, 5.00] | 4.45 [3.85, 4.90] | -0.40 [-1.05, 0.20] | 0.2785 |
| negotiation_effectiveness | 20 | 3.60 [3.10, 4.10] | 3.70 [3.25, 4.15] | 0.10 [-0.45, 0.70] | 0.7887 |
| conversational_efficiency | 20 | 4.10 [3.65, 4.55] | 3.90 [3.35, 4.40] | -0.20 [-0.80, 0.40] | 0.6202 |
| customer_experience | 20 | 3.55 [3.05, 4.00] | 3.60 [3.10, 4.10] | 0.05 [-0.45, 0.55] | 0.9706 |
| recovery_quality | 20 | 3.90 [3.40, 4.35] | 3.90 [3.35, 4.40] | 0.00 [-0.55, 0.55] | 0.9421 |

## Tier 4 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 6.40 [5.15, 7.70] | 6.60 [5.25, 7.95] | 0.20 [-1.25, 1.45] | 0.5159 |
| efficiency_ratio | 19 | 2.95 [2.11, 3.84] | 7.03 [2.11, 16.13] | 4.08 [-0.95, 13.24] | 0.9793 |
| simulated_latency_ms | 20 | 6555.23 [4956.25, 8334.27] | 22568.24 [5278.71, 55489.23] | 16013.01 [-1599.96, 49115.37] | 0.7228 |
| parse_accuracy | 19 | 0.34 [0.18, 0.50] | 0.34 [0.18, 0.53] | 0.00 [-0.18, 0.18] | 0.9139 |
| dead_end_turns | 20 | 3.35 [2.10, 4.70] | 3.45 [2.15, 4.80] | 0.10 [-1.40, 1.45] | 0.7257 |
| unsupported_facts | 20 | 1.00 [0.00, 2.25] | 0.60 [0.00, 1.40] | -0.40 [-1.85, 0.90] | 0.5992 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 90.0% [75.0%, 100.0%] | 90.0% [75.0%, 100.0%] | 0.0% [-20.0%, 20.0%] | 2/2 | 1.0000 |
| faithful | 20 | 85.0% [70.0%, 100.0%] | 85.0% [70.0%, 100.0%] | 0.0% [-25.0%, 25.0%] | 3/3 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.55 [4.25, 4.80] | 4.35 [3.95, 4.70] | -0.20 [-0.65, 0.20] | 0.3889 |
| negotiation_effectiveness | 17 | 3.47 [3.00, 3.94] | 3.59 [3.18, 4.00] | 0.12 [-0.65, 0.82] | 0.6516 |
| conversational_efficiency | 20 | 3.80 [3.40, 4.20] | 3.95 [3.55, 4.35] | 0.15 [-0.40, 0.75] | 0.6801 |
| customer_experience | 20 | 3.50 [3.00, 3.95] | 3.70 [3.25, 4.10] | 0.20 [-0.40, 0.90] | 0.6682 |
| recovery_quality | 17 | 3.59 [3.06, 4.12] | 3.82 [3.41, 4.24] | 0.24 [-0.53, 1.00] | 0.4951 |

## Tier 5 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 8.70 [7.45, 9.90] | 8.15 [6.95, 9.45] | -0.55 [-2.10, 1.05] | 0.5361 |
| efficiency_ratio | 20 | 3.03 [2.32, 3.98] | 3.20 [2.45, 4.13] | 0.17 [-0.80, 1.13] | 0.7770 |
| simulated_latency_ms | 20 | 10430.37 [8294.18, 13107.74] | 11047.03 [8732.52, 13804.57] | 616.65 [-2127.08, 3448.86] | 0.8666 |
| parse_accuracy | 20 | 0.42 [0.25, 0.62] | 0.45 [0.25, 0.65] | 0.03 [-0.17, 0.22] | 0.8514 |
| dead_end_turns | 20 | 4.55 [3.05, 6.25] | 4.30 [2.90, 5.80] | -0.25 [-2.15, 1.75] | 0.7348 |
| unsupported_facts | 20 | 0.00 [0.00, 0.00] | 0.30 [0.00, 0.90] | 0.30 [0.00, 0.90] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 80.0% [60.0%, 95.0%] | 70.0% [50.0%, 90.0%] | -10.0% [-35.0%, 15.0%] | 4/2 | 0.6875 |
| faithful | 20 | 100.0% [100.0%, 100.0%] | 95.0% [85.0%, 100.0%] | -5.0% [-15.0%, 0.0%] | 1/0 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.05 [3.50, 4.55] | 3.75 [3.25, 4.25] | -0.30 [-1.00, 0.35] | 0.3606 |
| negotiation_effectiveness | 20 | 2.75 [2.35, 3.15] | 2.25 [2.00, 2.50] | -0.50 [-0.90, -0.10] | 0.0354* |
| conversational_efficiency | 20 | 2.95 [2.50, 3.40] | 2.80 [2.45, 3.10] | -0.15 [-0.55, 0.25] | 0.5242 |
| customer_experience | 20 | 2.25 [1.85, 2.65] | 2.05 [1.85, 2.25] | -0.20 [-0.65, 0.30] | 0.4888 |
| recovery_quality | 20 | 2.95 [2.50, 3.40] | 2.65 [2.35, 2.95] | -0.30 [-0.70, 0.10] | 0.1865 |

## Tier 6 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 5.95 [4.50, 7.50] | 6.50 [5.05, 8.05] | 0.55 [-0.75, 2.00] | 0.5216 |
| efficiency_ratio | 20 | 2.73 [1.85, 3.67] | 4.33 [2.25, 7.05] | 1.60 [-0.25, 4.20] | 0.3950 |
| simulated_latency_ms | 20 | 7295.74 [5143.10, 9692.62] | 9462.57 [5237.53, 14863.38] | 2166.82 [-1884.24, 7470.39] | 0.7228 |
| parse_accuracy | 20 | 0.38 [0.20, 0.55] | 0.45 [0.28, 0.62] | 0.08 [-0.08, 0.25] | 0.4070 |
| dead_end_turns | 20 | 2.55 [1.30, 4.10] | 3.40 [2.00, 4.95] | 0.85 [-0.50, 2.25] | 0.1804 |
| unsupported_facts | 20 | 1.85 [0.00, 5.35] | 0.60 [0.00, 1.65] | -1.25 [-5.00, 1.20] | 0.8551 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 80.0% [60.0%, 95.0%] | 75.0% [55.0%, 90.0%] | -5.0% [-20.0%, 10.0%] | 2/1 | 1.0000 |
| faithful | 20 | 90.0% [75.0%, 100.0%] | 90.0% [75.0%, 100.0%] | 0.0% [-20.0%, 20.0%] | 2/2 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.50 [4.25, 4.75] | 4.30 [3.90, 4.65] | -0.20 [-0.60, 0.20] | 0.3261 |
| negotiation_effectiveness | 18 | 3.61 [3.06, 4.11] | 2.67 [2.28, 3.11] | -0.94 [-1.50, -0.39] | 0.0083** |
| conversational_efficiency | 20 | 3.80 [3.15, 4.40] | 3.55 [3.05, 4.05] | -0.25 [-0.80, 0.20] | 0.4773 |
| customer_experience | 20 | 3.70 [3.10, 4.25] | 3.20 [2.70, 3.70] | -0.50 [-1.05, 0.00] | 0.0848 |
| recovery_quality | 0 | — | — | — | — |

## Tier 7 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 3.70 [3.25, 4.15] | 4.50 [3.70, 5.60] | 0.80 [-0.10, 1.90] | 0.1639 |
| efficiency_ratio | 0 | — | — | — | — |
| simulated_latency_ms | 20 | 1289.97 [707.66, 1919.48] | 2191.10 [1149.12, 3499.56] | 901.13 [-129.90, 2265.19] | 0.4331 |
| parse_accuracy | 0 | — | — | — | — |
| dead_end_turns | 20 | 0.60 [0.20, 1.10] | 0.70 [0.25, 1.30] | 0.10 [-0.35, 0.60] | 0.6600 |
| unsupported_facts | 20 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 20 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 20 | 100.0% [100.0%, 100.0%] | 95.0% [85.0%, 100.0%] | -5.0% [-15.0%, 0.0%] | 1/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.85 [4.60, 5.00] | 4.05 [3.45, 4.60] | -0.80 [-1.40, -0.25] | 0.0230* |
| negotiation_effectiveness | 0 | — | — | — | — |
| conversational_efficiency | 20 | 4.00 [3.60, 4.35] | 3.35 [2.95, 3.80] | -0.65 [-1.15, -0.10] | 0.0238* |
| customer_experience | 0 | — | — | — | — |
| recovery_quality | 0 | — | — | — | — |
