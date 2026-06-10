# Paired comparison — `20260608_221848__nlp_arm3_expansion__4eadd22__representative_reduced` vs `20260606_234404__nlp_arm3__e1626fa__representative_reduced`

**Pairing:** 120 valid pairs out of 120 matched scenario-runs (excluded 0 pairs where either side had `termination=error` or missing derived metrics). Baseline-only keys: 0, candidate-only: 0.

## Overall (all tiers)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 120 | 6.64 [6.03, 7.29] | 5.43 [4.85, 6.07] | -1.21 [-1.80, -0.61] | 0.0000*** |
| efficiency_ratio | 99 | 6.32 [3.99, 9.15] | 4.72 [3.27, 6.70] | -1.61 [-4.83, 1.39] | 0.7504 |
| simulated_latency_ms | 120 | 15887.57 [9073.14, 24601.02] | 12040.65 [8188.19, 17377.55] | -3846.92 [-13281.92, 4550.99] | 0.0141* |
| parse_accuracy | 99 | 0.46 [0.38, 0.55] | 0.45 [0.36, 0.54] | -0.01 [-0.08, 0.07] | 0.7139 |
| dead_end_turns | 120 | 3.23 [2.58, 3.92] | 1.27 [0.87, 1.76] | -1.95 [-2.63, -1.32] | 0.0000*** |
| unsupported_facts | 120 | 0.43 [0.10, 0.92] | 0.28 [0.07, 0.55] | -0.16 [-0.70, 0.29] | 0.6478 |
| availability_calls | 120 | 11.86 [7.12, 17.85] | 9.12 [6.16, 13.19] | -2.74 [-9.32, 3.23] | 0.6376 |
| ladder_fire_turns | 120 | 0.77 [0.56, 0.99] | 1.52 [1.27, 1.82] | 0.75 [0.47, 1.05] | 0.0000*** |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 120 | 59.2% [50.0%, 68.3%] | 65.8% [56.7%, 74.2%] | 6.7% [-0.8%, 14.2%] | 7/15 | 0.1338 |
| faithful | 120 | 94.2% [90.0%, 98.3%] | 94.2% [90.0%, 98.3%] | 0.0% [-5.8%, 5.8%] | 6/6 | 1.0000 |
| refusal_accepted | 120 | 16.7% [10.0%, 23.3%] | 16.7% [10.0%, 23.3%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 120 | 4.58 [4.44, 4.72] | 4.37 [4.20, 4.53] | -0.22 [-0.42, -0.02] | 0.0354* |
| negotiation_effectiveness | 84 | 3.07 [2.85, 3.30] | 3.71 [3.44, 4.00] | 0.64 [0.33, 0.95] | 0.0001*** |
| conversational_efficiency | 120 | 3.62 [3.40, 3.83] | 3.72 [3.49, 3.92] | 0.10 [-0.12, 0.32] | 0.2663 |
| customer_experience | 100 | 3.36 [3.09, 3.63] | 3.66 [3.39, 3.91] | 0.30 [0.03, 0.57] | 0.0327* |
| recovery_quality | 56 | 3.43 [3.11, 3.73] | 3.77 [3.45, 4.07] | 0.34 [-0.02, 0.70] | 0.0700 |

## Tier 1 (n=10)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 10 | 4.20 [2.20, 7.10] | 3.90 [1.80, 6.90] | -0.30 [-0.60, 0.00] | 0.1489 |
| efficiency_ratio | 10 | 3.40 [1.20, 6.60] | 3.40 [1.20, 6.60] | 0.00 [0.00, 0.00] | 1.0000 |
| simulated_latency_ms | 10 | 3919.65 [2053.77, 6513.68] | 4747.42 [1945.67, 8715.78] | 827.77 [-217.75, 2172.50] | 0.5408 |
| parse_accuracy | 10 | 0.55 [0.30, 0.75] | 0.50 [0.30, 0.70] | -0.05 [-0.15, 0.00] | 1.0000 |
| dead_end_turns | 10 | 2.20 [0.00, 5.40] | 1.30 [0.00, 3.20] | -0.90 [-2.40, 0.00] | 0.3711 |
| unsupported_facts | 10 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 10 | 3.40 [1.20, 6.60] | 3.40 [1.20, 6.60] | 0.00 [0.00, 0.00] | 1.0000 |
| ladder_fire_turns | 10 | 0.00 [0.00, 0.00] | 0.50 [0.10, 1.00] | 0.50 [0.10, 1.00] | 0.0890 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 10 | 80.0% [50.0%, 100.0%] | 80.0% [50.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 10 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 10 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 10 | 5.00 [5.00, 5.00] | 4.50 [3.70, 5.00] | -0.50 [-1.30, 0.00] | 0.3711 |
| negotiation_effectiveness | 4 | 3.00 [2.00, 4.00] | 3.50 [2.00, 5.00] | 0.50 [0.00, 1.00] | 0.3458 |
| conversational_efficiency | 10 | 4.40 [3.50, 5.00] | 4.40 [3.50, 5.00] | 0.00 [0.00, 0.00] | 1.0000 |
| customer_experience | 10 | 4.40 [3.50, 5.00] | 4.10 [3.20, 5.00] | -0.30 [-0.90, 0.00] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 2 (n=10)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 10 | 8.00 [5.20, 10.70] | 5.20 [2.50, 8.10] | -2.80 [-5.40, -0.70] | 0.0579 |
| efficiency_ratio | 9 | 5.00 [2.44, 7.67] | 2.56 [1.78, 3.56] | -2.44 [-5.33, 0.33] | 0.2476 |
| simulated_latency_ms | 10 | 6210.18 [3945.92, 8645.64] | 5084.92 [2857.78, 8303.84] | -1125.27 [-4118.99, 1755.23] | 0.7598 |
| parse_accuracy | 9 | 0.56 [0.28, 0.83] | 0.67 [0.39, 0.89] | 0.11 [-0.11, 0.39] | 0.5862 |
| dead_end_turns | 10 | 2.50 [0.30, 5.30] | 0.90 [0.00, 2.30] | -1.60 [-4.70, 1.20] | 0.4615 |
| unsupported_facts | 10 | 0.40 [0.00, 1.20] | 0.00 [0.00, 0.00] | -0.40 [-1.20, 0.00] | 1.0000 |
| availability_calls | 10 | 5.70 [3.10, 8.50] | 4.00 [2.00, 7.10] | -1.70 [-4.70, 1.00] | 0.3972 |
| ladder_fire_turns | 10 | 0.10 [0.00, 0.30] | 1.40 [0.70, 2.50] | 1.30 [0.60, 2.40] | 0.0083** |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 10 | 50.0% [20.0%, 80.0%] | 70.0% [40.0%, 100.0%] | 20.0% [0.0%, 50.0%] | 0/2 | 0.5000 |
| faithful | 10 | 90.0% [70.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 10.0% [0.0%, 30.0%] | 0/1 | 1.0000 |
| refusal_accepted | 10 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 10 | 4.50 [3.80, 5.00] | 4.30 [3.80, 4.70] | -0.20 [-1.00, 0.70] | 0.6707 |
| negotiation_effectiveness | 8 | 2.62 [1.88, 3.50] | 3.88 [2.75, 4.62] | 1.25 [0.25, 2.25] | 0.0863 |
| conversational_efficiency | 10 | 3.30 [2.40, 4.20] | 4.10 [3.40, 4.70] | 0.80 [0.10, 1.50] | 0.0890 |
| customer_experience | 10 | 3.40 [2.60, 4.30] | 4.00 [3.30, 4.70] | 0.60 [-0.10, 1.40] | 0.1975 |
| recovery_quality | 0 | — | — | — | — |

## Tier 3 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 6.85 [5.25, 8.50] | 6.40 [4.65, 8.20] | -0.45 [-2.05, 1.25] | 0.1675 |
| efficiency_ratio | 20 | 6.12 [2.48, 12.78] | 7.15 [3.08, 13.62] | 1.03 [-7.90, 9.27] | 0.2318 |
| simulated_latency_ms | 20 | 18733.14 [5995.46, 42523.56] | 22255.00 [8086.96, 46219.85] | 3521.86 [-29258.84, 35258.50] | 0.1978 |
| parse_accuracy | 20 | 0.45 [0.28, 0.62] | 0.45 [0.28, 0.62] | 0.00 [-0.12, 0.10] | 0.7855 |
| dead_end_turns | 20 | 3.90 [2.40, 5.50] | 2.40 [1.00, 3.95] | -1.50 [-3.25, 0.10] | 0.0624 |
| unsupported_facts | 20 | 0.10 [0.00, 0.30] | 0.15 [0.00, 0.45] | 0.05 [0.00, 0.15] | 1.0000 |
| availability_calls | 20 | 12.25 [4.95, 25.55] | 14.30 [6.15, 27.25] | 2.05 [-15.80, 18.55] | 0.2318 |
| ladder_fire_turns | 20 | 1.10 [0.60, 1.65] | 1.70 [1.30, 2.15] | 0.60 [0.20, 1.05] | 0.0179* |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 75.0% [55.0%, 95.0%] | 65.0% [45.0%, 85.0%] | -10.0% [-30.0%, 10.0%] | 3/1 | 0.6250 |
| faithful | 20 | 95.0% [85.0%, 100.0%] | 95.0% [85.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.65 [4.30, 4.90] | 4.75 [4.45, 5.00] | 0.10 [-0.25, 0.50] | 0.6788 |
| negotiation_effectiveness | 20 | 3.85 [3.40, 4.25] | 4.10 [3.50, 4.65] | 0.25 [-0.45, 0.95] | 0.4868 |
| conversational_efficiency | 20 | 4.15 [3.70, 4.55] | 4.10 [3.55, 4.65] | -0.05 [-0.70, 0.65] | 0.9172 |
| customer_experience | 20 | 3.85 [3.25, 4.40] | 4.05 [3.45, 4.60] | 0.20 [-0.50, 0.95] | 0.6046 |
| recovery_quality | 20 | 4.15 [3.70, 4.55] | 4.15 [3.60, 4.65] | 0.00 [-0.65, 0.65] | 1.0000 |

## Tier 4 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 7.05 [5.50, 8.60] | 4.25 [3.50, 5.25] | -2.80 [-4.10, -1.60] | 0.0011** |
| efficiency_ratio | 20 | 6.65 [2.50, 13.82] | 3.65 [2.00, 6.38] | -3.00 [-10.45, 1.55] | 0.4427 |
| simulated_latency_ms | 20 | 19999.49 [5655.40, 46081.39] | 9417.88 [5426.05, 15814.14] | -10581.61 [-36767.84, 4000.93] | 0.6407 |
| parse_accuracy | 20 | 0.47 [0.25, 0.70] | 0.40 [0.20, 0.60] | -0.07 [-0.32, 0.17] | 0.5271 |
| dead_end_turns | 20 | 4.00 [2.40, 5.75] | 1.05 [0.25, 2.35] | -2.95 [-4.50, -1.60] | 0.0011** |
| unsupported_facts | 20 | 1.50 [0.00, 4.10] | 0.50 [0.00, 1.40] | -1.00 [-3.70, 1.00] | 0.7127 |
| availability_calls | 20 | 13.30 [5.00, 27.65] | 7.30 [4.00, 12.75] | -6.00 [-20.90, 3.10] | 0.4427 |
| ladder_fire_turns | 20 | 0.95 [0.40, 1.65] | 1.65 [1.00, 2.65] | 0.70 [-0.15, 1.55] | 0.0817 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 70.0% [50.0%, 90.0%] | 95.0% [85.0%, 100.0%] | 25.0% [10.0%, 45.0%] | 0/5 | 0.0625 |
| faithful | 20 | 90.0% [75.0%, 100.0%] | 90.0% [75.0%, 100.0%] | 0.0% [-20.0%, 20.0%] | 2/2 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.90 [4.75, 5.00] | 4.50 [4.15, 4.80] | -0.40 [-0.75, -0.10] | 0.0401* |
| negotiation_effectiveness | 16 | 2.94 [2.44, 3.44] | 4.25 [3.88, 4.62] | 1.31 [0.88, 1.75] | 0.0013** |
| conversational_efficiency | 20 | 3.75 [3.20, 4.25] | 4.25 [3.80, 4.65] | 0.50 [0.10, 0.85] | 0.0363* |
| customer_experience | 20 | 3.45 [2.85, 4.05] | 4.15 [3.70, 4.55] | 0.70 [0.25, 1.20] | 0.0186* |
| recovery_quality | 16 | 3.25 [2.62, 3.88] | 4.25 [3.75, 4.69] | 1.00 [0.50, 1.62] | 0.0043** |

## Tier 5 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 7.90 [6.90, 9.00] | 6.50 [5.45, 7.70] | -1.40 [-2.70, -0.15] | 0.0652 |
| efficiency_ratio | 20 | 8.67 [2.27, 18.58] | 5.87 [2.45, 11.88] | -2.80 [-13.52, 6.50] | 0.7792 |
| simulated_latency_ms | 20 | 30051.88 [7238.95, 63968.92] | 19558.41 [8902.16, 37111.85] | -10493.47 [-47090.90, 19351.07] | 0.2708 |
| parse_accuracy | 20 | 0.47 [0.30, 0.68] | 0.45 [0.28, 0.65] | -0.02 [-0.08, 0.00] | 1.0000 |
| dead_end_turns | 20 | 3.30 [2.10, 4.65] | 0.95 [0.20, 1.90] | -2.35 [-3.85, -0.80] | 0.0059** |
| unsupported_facts | 20 | 0.60 [0.00, 1.60] | 0.20 [0.00, 0.50] | -0.40 [-1.40, 0.30] | 0.5807 |
| availability_calls | 20 | 26.00 [6.80, 55.75] | 17.60 [7.35, 35.65] | -8.40 [-40.55, 19.50] | 0.8219 |
| ladder_fire_turns | 20 | 0.70 [0.40, 1.00] | 2.40 [1.80, 3.20] | 1.70 [1.10, 2.40] | 0.0003*** |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 75.0% [55.0%, 95.0%] | 85.0% [70.0%, 100.0%] | 10.0% [-15.0%, 35.0%] | 2/4 | 0.6875 |
| faithful | 20 | 90.0% [75.0%, 100.0%] | 90.0% [75.0%, 100.0%] | 0.0% [-20.0%, 20.0%] | 2/2 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.10 [3.65, 4.50] | 3.70 [3.35, 4.05] | -0.40 [-1.00, 0.20] | 0.1759 |
| negotiation_effectiveness | 20 | 2.50 [2.25, 2.75] | 3.05 [2.65, 3.45] | 0.55 [0.10, 1.00] | 0.0433* |
| conversational_efficiency | 20 | 2.80 [2.45, 3.15] | 2.75 [2.45, 3.05] | -0.05 [-0.50, 0.40] | 0.8778 |
| customer_experience | 20 | 2.25 [1.90, 2.60] | 2.50 [2.15, 2.85] | 0.25 [-0.25, 0.75] | 0.3960 |
| recovery_quality | 20 | 2.85 [2.45, 3.25] | 3.00 [2.60, 3.40] | 0.15 [-0.40, 0.70] | 0.6965 |

## Tier 6 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 7.35 [5.75, 8.90] | 6.20 [4.55, 7.95] | -1.15 [-3.05, 0.80] | 0.2081 |
| efficiency_ratio | 20 | 5.90 [3.02, 10.40] | 3.83 [2.62, 5.17] | -2.08 [-6.20, 0.62] | 0.6410 |
| simulated_latency_ms | 20 | 15864.40 [6825.65, 31470.95] | 9874.26 [7021.01, 12956.94] | -5990.14 [-20755.77, 2669.35] | 0.6951 |
| parse_accuracy | 20 | 0.38 [0.17, 0.60] | 0.40 [0.20, 0.60] | 0.03 [-0.18, 0.23] | 1.0000 |
| dead_end_turns | 20 | 5.00 [3.20, 6.85] | 1.65 [0.55, 3.00] | -3.35 [-5.25, -1.75] | 0.0016** |
| unsupported_facts | 20 | 0.00 [0.00, 0.00] | 0.80 [0.00, 2.20] | 0.80 [0.00, 2.20] | 0.3711 |
| availability_calls | 20 | 11.80 [6.05, 20.80] | 7.65 [5.25, 10.35] | -4.15 [-12.40, 1.25] | 0.6410 |
| ladder_fire_turns | 20 | 1.40 [0.70, 2.20] | 1.70 [1.10, 2.50] | 0.30 [-0.65, 1.30] | 0.5695 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 70.0% [50.0%, 90.0%] | 75.0% [55.0%, 90.0%] | 5.0% [-15.0%, 25.0%] | 2/3 | 1.0000 |
| faithful | 20 | 100.0% [100.0%, 100.0%] | 90.0% [75.0%, 100.0%] | -10.0% [-25.0%, 0.0%] | 2/0 | 0.5000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.50 [4.20, 4.75] | 4.35 [3.85, 4.75] | -0.15 [-0.70, 0.35] | 0.6259 |
| negotiation_effectiveness | 16 | 3.19 [2.75, 3.62] | 3.50 [2.75, 4.19] | 0.31 [-0.62, 1.12] | 0.3554 |
| conversational_efficiency | 20 | 3.60 [3.10, 4.10] | 3.60 [2.95, 4.25] | 0.00 [-0.85, 0.80] | 0.9682 |
| customer_experience | 20 | 3.35 [2.85, 3.85] | 3.55 [2.90, 4.20] | 0.20 [-0.60, 0.95] | 0.5453 |
| recovery_quality | 0 | — | — | — | — |

## Tier 7 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 4.60 [4.15, 5.05] | 4.70 [4.10, 5.40] | 0.10 [-0.60, 0.80] | 0.9531 |
| efficiency_ratio | 0 | — | — | — | — |
| simulated_latency_ms | 20 | 5611.62 [1786.79, 12436.63] | 6222.22 [3636.93, 9115.06] | 610.59 [-7967.89, 6186.00] | 0.0613 |
| parse_accuracy | 0 | — | — | — | — |
| dead_end_turns | 20 | 0.80 [0.40, 1.25] | 0.50 [0.20, 0.85] | -0.30 [-0.75, 0.10] | 0.2501 |
| unsupported_facts | 20 | 0.20 [0.00, 0.60] | 0.00 [0.00, 0.00] | -0.20 [-0.60, 0.00] | 1.0000 |
| availability_calls | 20 | 3.25 [1.25, 6.35] | 4.15 [2.20, 6.45] | 0.90 [-3.15, 4.15] | 0.1949 |
| ladder_fire_turns | 20 | 0.40 [0.10, 0.80] | 0.70 [0.40, 1.00] | 0.30 [-0.25, 0.80] | 0.3233 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 20 | 95.0% [85.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 5.0% [0.0%, 15.0%] | 0/1 | 1.0000 |
| refusal_accepted | 20 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.60 [4.35, 4.85] | 4.50 [4.05, 4.85] | -0.10 [-0.60, 0.35] | 0.7737 |
| negotiation_effectiveness | 0 | — | — | — | — |
| conversational_efficiency | 20 | 3.55 [3.20, 3.85] | 3.35 [3.00, 3.70] | -0.20 [-0.60, 0.25] | 0.3971 |
| customer_experience | 0 | — | — | — | — |
| recovery_quality | 0 | — | — | — | — |
