# Paired comparison — `20260606_234404__nlp_arm3__e1626fa__representative_reduced` vs `20260606_205242__baseline__e1626fa__representative_reduced`

**Pairing:** 120 valid pairs out of 120 matched scenario-runs (excluded 0 pairs where either side had `termination=error` or missing derived metrics). Baseline-only keys: 0, candidate-only: 0.

## Overall (all tiers)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 120 | 6.37 [5.73, 7.05] | 6.64 [6.03, 7.29] | 0.28 [-0.32, 0.90] | 0.1505 |
| efficiency_ratio | 98 | 4.64 [3.15, 6.65] | 6.38 [4.06, 9.14] | 1.73 [-1.29, 4.97] | 0.5522 |
| simulated_latency_ms | 120 | 10072.43 [6071.93, 15721.83] | 15887.57 [9073.14, 24601.02] | 5815.15 [-3045.17, 15547.29] | 0.4554 |
| parse_accuracy | 98 | 0.41 [0.33, 0.48] | 0.46 [0.37, 0.55] | 0.06 [-0.02, 0.13] | 0.1395 |
| dead_end_turns | 120 | 3.15 [2.48, 3.86] | 3.23 [2.58, 3.92] | 0.08 [-0.65, 0.83] | 0.6354 |
| unsupported_facts | 120 | 0.58 [0.12, 1.32] | 0.43 [0.10, 0.92] | -0.15 [-0.98, 0.54] | 0.7523 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 120 | 62.5% [53.3%, 70.8%] | 59.2% [50.0%, 68.3%] | -3.3% [-10.8%, 4.2%] | 13/9 | 0.5235 |
| faithful | 120 | 95.0% [90.8%, 98.3%] | 94.2% [90.0%, 98.3%] | -0.8% [-6.7%, 5.0%] | 7/6 | 1.0000 |
| refusal_accepted | 120 | 16.7% [10.0%, 23.3%] | 16.7% [10.0%, 23.3%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 120 | 4.60 [4.45, 4.74] | 4.58 [4.44, 4.72] | -0.02 [-0.19, 0.16] | 0.7990 |
| negotiation_effectiveness | 87 | 3.30 [3.06, 3.54] | 3.13 [2.91, 3.36] | -0.17 [-0.47, 0.11] | 0.2746 |
| conversational_efficiency | 120 | 3.73 [3.51, 3.94] | 3.62 [3.40, 3.83] | -0.11 [-0.35, 0.12] | 0.4576 |
| customer_experience | 100 | 3.33 [3.06, 3.59] | 3.36 [3.09, 3.63] | 0.03 [-0.25, 0.31] | 0.9157 |
| recovery_quality | 57 | 3.47 [3.18, 3.79] | 3.46 [3.16, 3.77] | -0.02 [-0.40, 0.37] | 0.9488 |

## Tier 1 (n=10)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 10 | 5.20 [2.70, 8.20] | 4.20 [2.20, 7.10] | -1.00 [-2.90, 0.10] | 0.3447 |
| efficiency_ratio | 10 | 5.10 [1.40, 10.20] | 3.40 [1.20, 6.60] | -1.70 [-5.60, 1.80] | 0.3613 |
| simulated_latency_ms | 10 | 6004.89 [2584.76, 10417.76] | 3919.65 [2053.77, 6513.68] | -2085.24 [-5417.42, 470.73] | 0.3590 |
| parse_accuracy | 10 | 0.50 [0.25, 0.75] | 0.55 [0.30, 0.75] | 0.05 [-0.15, 0.30] | 1.0000 |
| dead_end_turns | 10 | 2.50 [0.00, 6.00] | 2.20 [0.00, 5.40] | -0.30 [-3.60, 2.70] | 1.0000 |
| unsupported_facts | 10 | 1.30 [0.00, 3.90] | 0.00 [0.00, 0.00] | -1.30 [-3.90, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 10 | 70.0% [40.0%, 100.0%] | 80.0% [50.0%, 100.0%] | 10.0% [0.0%, 30.0%] | 0/1 | 1.0000 |
| faithful | 10 | 90.0% [70.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 10.0% [0.0%, 30.0%] | 0/1 | 1.0000 |
| refusal_accepted | 10 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 10 | 4.70 [4.10, 5.00] | 5.00 [5.00, 5.00] | 0.30 [0.00, 0.90] | 1.0000 |
| negotiation_effectiveness | 4 | 2.50 [1.50, 3.50] | 3.00 [2.00, 4.00] | 0.50 [-0.50, 1.50] | 0.5862 |
| conversational_efficiency | 10 | 3.80 [2.80, 4.70] | 4.40 [3.50, 5.00] | 0.60 [0.00, 1.30] | 0.1814 |
| customer_experience | 10 | 3.80 [2.80, 4.70] | 4.40 [3.50, 5.00] | 0.60 [0.00, 1.30] | 0.1814 |
| recovery_quality | 0 | — | — | — | — |

## Tier 2 (n=10)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 10 | 7.50 [4.80, 10.20] | 8.00 [5.20, 10.70] | 0.50 [-3.40, 4.20] | 1.0000 |
| efficiency_ratio | 9 | 6.67 [3.89, 9.56] | 5.00 [2.44, 7.67] | -1.67 [-6.11, 2.67] | 0.4406 |
| simulated_latency_ms | 10 | 7846.42 [4993.41, 11535.97] | 6210.18 [3945.92, 8645.64] | -1636.24 [-6538.18, 2588.63] | 0.6835 |
| parse_accuracy | 9 | 0.44 [0.17, 0.72] | 0.56 [0.28, 0.83] | 0.11 [-0.11, 0.28] | 0.4237 |
| dead_end_turns | 10 | 5.30 [2.50, 8.30] | 2.50 [0.30, 5.30] | -2.80 [-6.70, 0.70] | 0.1882 |
| unsupported_facts | 10 | 0.00 [0.00, 0.00] | 0.40 [0.00, 1.20] | 0.40 [0.00, 1.20] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 10 | 50.0% [20.0%, 80.0%] | 50.0% [20.0%, 80.0%] | 0.0% [-40.0%, 40.0%] | 2/2 | 1.0000 |
| faithful | 10 | 100.0% [100.0%, 100.0%] | 90.0% [70.0%, 100.0%] | -10.0% [-30.0%, 0.0%] | 1/0 | 1.0000 |
| refusal_accepted | 10 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 10 | 4.90 [4.70, 5.00] | 4.50 [3.80, 5.00] | -0.40 [-1.20, 0.20] | 0.4227 |
| negotiation_effectiveness | 9 | 3.33 [2.56, 4.22] | 2.89 [2.00, 3.78] | -0.44 [-1.78, 0.89] | 0.5711 |
| conversational_efficiency | 10 | 3.60 [2.70, 4.40] | 3.30 [2.40, 4.20] | -0.30 [-1.60, 1.00] | 0.7835 |
| customer_experience | 10 | 3.50 [2.60, 4.40] | 3.40 [2.60, 4.30] | -0.10 [-1.30, 1.20] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 3 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 7.10 [5.60, 8.75] | 6.85 [5.25, 8.50] | -0.25 [-1.75, 1.30] | 0.5560 |
| efficiency_ratio | 20 | 8.65 [2.55, 17.27] | 6.12 [2.48, 12.78] | -2.53 [-11.80, 6.97] | 0.6594 |
| simulated_latency_ms | 20 | 27937.59 [5890.54, 59962.20] | 18733.14 [5995.46, 42523.56] | -9204.45 [-43371.78, 25128.28] | 0.9553 |
| parse_accuracy | 20 | 0.42 [0.28, 0.57] | 0.45 [0.28, 0.62] | 0.03 [-0.05, 0.10] | 0.7728 |
| dead_end_turns | 20 | 3.95 [2.40, 5.70] | 3.90 [2.40, 5.50] | -0.05 [-1.75, 1.75] | 1.0000 |
| unsupported_facts | 20 | 0.00 [0.00, 0.00] | 0.10 [0.00, 0.30] | 0.10 [0.00, 0.30] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 65.0% [45.0%, 85.0%] | 75.0% [55.0%, 95.0%] | 10.0% [-10.0%, 30.0%] | 1/3 | 0.6250 |
| faithful | 20 | 100.0% [100.0%, 100.0%] | 95.0% [85.0%, 100.0%] | -5.0% [-15.0%, 0.0%] | 1/0 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.85 [4.55, 5.00] | 4.65 [4.30, 4.90] | -0.20 [-0.65, 0.25] | 0.5827 |
| negotiation_effectiveness | 20 | 3.60 [3.10, 4.10] | 3.85 [3.40, 4.25] | 0.25 [-0.40, 0.90] | 0.4425 |
| conversational_efficiency | 20 | 4.10 [3.65, 4.55] | 4.15 [3.70, 4.55] | 0.05 [-0.60, 0.70] | 0.9172 |
| customer_experience | 20 | 3.55 [3.05, 4.00] | 3.85 [3.25, 4.40] | 0.30 [-0.35, 0.95] | 0.4718 |
| recovery_quality | 20 | 3.90 [3.40, 4.35] | 4.15 [3.70, 4.55] | 0.25 [-0.40, 0.90] | 0.5595 |

## Tier 4 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 6.40 [5.15, 7.70] | 7.05 [5.50, 8.60] | 0.65 [-0.80, 2.20] | 0.4600 |
| efficiency_ratio | 19 | 2.95 [2.11, 3.84] | 6.95 [2.63, 14.16] | 4.00 [-0.24, 11.11] | 0.3924 |
| simulated_latency_ms | 20 | 6555.23 [4956.25, 8334.27] | 19999.49 [5655.40, 46081.39] | 13444.25 [-612.74, 39112.22] | 0.6677 |
| parse_accuracy | 19 | 0.34 [0.18, 0.50] | 0.47 [0.26, 0.68] | 0.13 [-0.05, 0.34] | 0.2117 |
| dead_end_turns | 20 | 3.35 [2.10, 4.70] | 4.00 [2.40, 5.75] | 0.65 [-0.90, 2.25] | 0.4888 |
| unsupported_facts | 20 | 1.00 [0.00, 2.25] | 1.50 [0.00, 4.10] | 0.50 [-1.70, 3.40] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 90.0% [75.0%, 100.0%] | 70.0% [50.0%, 90.0%] | -20.0% [-40.0%, 0.0%] | 5/1 | 0.2188 |
| faithful | 20 | 85.0% [70.0%, 100.0%] | 90.0% [75.0%, 100.0%] | 5.0% [-15.0%, 25.0%] | 2/3 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.55 [4.25, 4.80] | 4.90 [4.75, 5.00] | 0.35 [0.00, 0.70] | 0.0804 |
| negotiation_effectiveness | 17 | 3.47 [3.00, 3.94] | 3.00 [2.53, 3.47] | -0.47 [-1.24, 0.35] | 0.2809 |
| conversational_efficiency | 20 | 3.80 [3.40, 4.20] | 3.75 [3.20, 4.25] | -0.05 [-0.65, 0.55] | 0.9361 |
| customer_experience | 20 | 3.50 [3.00, 3.95] | 3.45 [2.85, 4.05] | -0.05 [-0.75, 0.60] | 0.9232 |
| recovery_quality | 17 | 3.59 [3.06, 4.12] | 3.35 [2.76, 3.94] | -0.24 [-1.12, 0.59] | 0.6706 |

## Tier 5 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 8.70 [7.45, 9.90] | 7.90 [6.90, 9.00] | -0.80 [-2.10, 0.35] | 0.4950 |
| efficiency_ratio | 20 | 3.03 [2.32, 3.98] | 8.67 [2.27, 18.58] | 5.63 [-0.97, 15.62] | 0.9355 |
| simulated_latency_ms | 20 | 10430.37 [8294.18, 13107.74] | 30051.88 [7238.95, 63968.92] | 19621.51 [-3789.77, 54033.61] | 0.5135 |
| parse_accuracy | 20 | 0.42 [0.25, 0.62] | 0.47 [0.30, 0.68] | 0.05 [-0.10, 0.20] | 0.5877 |
| dead_end_turns | 20 | 4.55 [3.05, 6.25] | 3.30 [2.10, 4.65] | -1.25 [-2.80, 0.20] | 0.1523 |
| unsupported_facts | 20 | 0.00 [0.00, 0.00] | 0.60 [0.00, 1.60] | 0.60 [0.00, 1.60] | 0.3711 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 80.0% [60.0%, 95.0%] | 75.0% [55.0%, 95.0%] | -5.0% [-20.0%, 10.0%] | 2/1 | 1.0000 |
| faithful | 20 | 100.0% [100.0%, 100.0%] | 90.0% [75.0%, 100.0%] | -10.0% [-25.0%, 0.0%] | 2/0 | 0.5000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.05 [3.50, 4.55] | 4.10 [3.65, 4.50] | 0.05 [-0.50, 0.65] | 0.8467 |
| negotiation_effectiveness | 20 | 2.75 [2.35, 3.15] | 2.50 [2.25, 2.75] | -0.25 [-0.65, 0.10] | 0.2362 |
| conversational_efficiency | 20 | 2.95 [2.50, 3.40] | 2.80 [2.45, 3.15] | -0.15 [-0.60, 0.30] | 0.5944 |
| customer_experience | 20 | 2.25 [1.85, 2.65] | 2.25 [1.90, 2.60] | 0.00 [-0.45, 0.50] | 0.9578 |
| recovery_quality | 20 | 2.95 [2.50, 3.40] | 2.85 [2.45, 3.25] | -0.10 [-0.65, 0.45] | 0.7456 |

## Tier 6 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 5.95 [4.50, 7.50] | 7.35 [5.75, 8.90] | 1.40 [0.35, 2.75] | 0.0317* |
| efficiency_ratio | 20 | 2.73 [1.85, 3.67] | 5.90 [3.02, 10.40] | 3.18 [0.68, 7.22] | 0.0111* |
| simulated_latency_ms | 20 | 7295.74 [5143.10, 9692.62] | 15864.40 [6825.65, 31470.95] | 8568.66 [-33.36, 23594.30] | 0.1615 |
| parse_accuracy | 20 | 0.38 [0.20, 0.55] | 0.38 [0.17, 0.60] | 0.00 [-0.20, 0.20] | 1.0000 |
| dead_end_turns | 20 | 2.55 [1.30, 4.10] | 5.00 [3.20, 6.85] | 2.45 [0.85, 4.40] | 0.0165* |
| unsupported_facts | 20 | 1.85 [0.00, 5.35] | 0.00 [0.00, 0.00] | -1.85 [-5.35, 0.00] | 0.3711 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 80.0% [60.0%, 95.0%] | 70.0% [50.0%, 90.0%] | -10.0% [-30.0%, 10.0%] | 3/1 | 0.6250 |
| faithful | 20 | 90.0% [75.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 10.0% [0.0%, 25.0%] | 0/2 | 0.5000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.50 [4.25, 4.75] | 4.50 [4.20, 4.75] | 0.00 [-0.30, 0.30] | 0.9542 |
| negotiation_effectiveness | 17 | 3.59 [3.00, 4.12] | 3.29 [2.82, 3.76] | -0.29 [-0.82, 0.18] | 0.3311 |
| conversational_efficiency | 20 | 3.80 [3.15, 4.40] | 3.60 [3.10, 4.10] | -0.20 [-0.75, 0.30] | 0.5697 |
| customer_experience | 20 | 3.70 [3.10, 4.25] | 3.35 [2.85, 3.85] | -0.35 [-0.85, 0.10] | 0.1780 |
| recovery_quality | 0 | — | — | — | — |

## Tier 7 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 3.70 [3.25, 4.15] | 4.60 [4.15, 5.05] | 0.90 [0.35, 1.40] | 0.0066** |
| efficiency_ratio | 0 | — | — | — | — |
| simulated_latency_ms | 20 | 1289.97 [707.66, 1919.48] | 5611.62 [1786.79, 12436.63] | 4321.65 [427.18, 11330.11] | 0.0207* |
| parse_accuracy | 0 | — | — | — | — |
| dead_end_turns | 20 | 0.60 [0.20, 1.10] | 0.80 [0.40, 1.25] | 0.20 [-0.25, 0.65] | 0.3500 |
| unsupported_facts | 20 | 0.00 [0.00, 0.00] | 0.20 [0.00, 0.60] | 0.20 [0.00, 0.60] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 20 | 100.0% [100.0%, 100.0%] | 95.0% [85.0%, 100.0%] | -5.0% [-15.0%, 0.0%] | 1/0 | 1.0000 |
| refusal_accepted | 20 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.85 [4.60, 5.00] | 4.60 [4.35, 4.85] | -0.25 [-0.50, 0.00] | 0.0726 |
| negotiation_effectiveness | 0 | — | — | — | — |
| conversational_efficiency | 20 | 4.00 [3.60, 4.35] | 3.55 [3.20, 3.85] | -0.45 [-0.85, -0.10] | 0.0437* |
| customer_experience | 0 | — | — | — | — |
| recovery_quality | 0 | — | — | — | — |
