# Paired comparison — `20260608_221848__nlp_arm3_expansion__4eadd22__representative_reduced` vs `20260607_164034__expansion__927f9c2__representative_reduced`

**Pairing:** 119 valid pairs out of 120 matched scenario-runs (excluded 1 pairs where either side had `termination=error` or missing derived metrics). Baseline-only keys: 0, candidate-only: 0.

## Overall (all tiers)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 119 | 5.69 [5.08, 6.33] | 5.38 [4.78, 6.03] | -0.31 [-0.87, 0.24] | 0.2566 |
| efficiency_ratio | 99 | 4.88 [3.54, 6.76] | 4.81 [3.35, 6.79] | -0.07 [-2.12, 2.07] | 0.7895 |
| simulated_latency_ms | 119 | 12995.01 [9271.30, 18658.71] | 11988.29 [8122.83, 17265.14] | -1006.72 [-7458.68, 5134.66] | 0.4427 |
| parse_accuracy | 99 | 0.45 [0.37, 0.54] | 0.46 [0.38, 0.56] | 0.01 [-0.06, 0.09] | 0.8267 |
| dead_end_turns | 119 | 1.42 [0.98, 1.91] | 1.23 [0.81, 1.70] | -0.19 [-0.70, 0.30] | 0.6043 |
| unsupported_facts | 119 | 0.46 [0.12, 0.95] | 0.28 [0.07, 0.58] | -0.18 [-0.60, 0.20] | 0.5688 |
| availability_calls | 119 | 8.97 [6.71, 12.13] | 9.07 [6.13, 13.02] | 0.09 [-3.66, 4.10] | 0.6166 |
| ladder_fire_turns | 119 | 1.70 [1.40, 2.04] | 1.50 [1.24, 1.81] | -0.19 [-0.54, 0.13] | 0.4315 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 119 | 65.5% [56.3%, 73.9%] | 66.4% [57.1%, 74.8%] | 0.8% [-5.0%, 6.7%] | 6/7 | 1.0000 |
| faithful | 119 | 92.4% [87.4%, 96.6%] | 94.1% [89.9%, 98.3%] | 1.7% [-4.2%, 7.6%] | 6/8 | 0.7905 |
| refusal_accepted | 119 | 16.0% [9.2%, 22.7%] | 16.8% [10.1%, 23.5%] | 0.8% [0.0%, 2.5%] | 0/1 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 119 | 4.44 [4.26, 4.60] | 4.36 [4.18, 4.53] | -0.08 [-0.29, 0.14] | 0.4641 |
| negotiation_effectiveness | 83 | 3.76 [3.51, 4.01] | 3.73 [3.46, 4.01] | -0.02 [-0.29, 0.24] | 0.7756 |
| conversational_efficiency | 119 | 3.77 [3.55, 3.98] | 3.73 [3.50, 3.96] | -0.04 [-0.27, 0.18] | 0.6543 |
| customer_experience | 99 | 3.73 [3.46, 3.99] | 3.68 [3.39, 3.94] | -0.05 [-0.30, 0.20] | 0.6111 |
| recovery_quality | 56 | 3.75 [3.41, 4.07] | 3.77 [3.45, 4.07] | 0.02 [-0.29, 0.32] | 0.9911 |

## Tier 1 (n=10)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 10 | 4.10 [2.00, 7.00] | 3.90 [1.80, 6.90] | -0.20 [-0.60, 0.20] | 0.4237 |
| efficiency_ratio | 10 | 3.20 [1.00, 6.30] | 3.40 [1.20, 6.60] | 0.20 [0.00, 0.50] | 0.3458 |
| simulated_latency_ms | 10 | 4810.09 [1919.02, 8882.16] | 4747.42 [1945.67, 8715.78] | -62.66 [-357.82, 233.97] | 1.0000 |
| parse_accuracy | 10 | 0.60 [0.35, 0.85] | 0.50 [0.30, 0.70] | -0.10 [-0.25, 0.00] | 0.3458 |
| dead_end_turns | 10 | 1.30 [0.00, 3.20] | 1.30 [0.00, 3.20] | 0.00 [0.00, 0.00] | 1.0000 |
| unsupported_facts | 10 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 10 | 3.20 [1.00, 6.30] | 3.40 [1.20, 6.60] | 0.20 [0.00, 0.50] | 0.3458 |
| ladder_fire_turns | 10 | 0.30 [0.00, 0.60] | 0.50 [0.10, 1.00] | 0.20 [0.00, 0.50] | 0.3458 |

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
| negotiation_effectiveness | 3 | 3.00 [2.00, 5.00] | 3.00 [2.00, 5.00] | 0.00 [0.00, 0.00] | 1.0000 |
| conversational_efficiency | 10 | 4.40 [3.50, 5.00] | 4.40 [3.50, 5.00] | 0.00 [0.00, 0.00] | 1.0000 |
| customer_experience | 10 | 4.40 [3.50, 5.00] | 4.10 [3.20, 5.00] | -0.30 [-0.90, 0.00] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 2 (n=10)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 10 | 8.30 [5.50, 11.10] | 5.20 [2.50, 8.10] | -3.10 [-6.10, -0.20] | 0.0890 |
| efficiency_ratio | 10 | 8.20 [4.40, 12.00] | 4.00 [2.00, 7.10] | -4.20 [-7.90, -0.70] | 0.0498* |
| simulated_latency_ms | 10 | 10208.58 [5406.47, 14941.27] | 5084.92 [2857.78, 8303.84] | -5123.66 [-10072.55, -549.69] | 0.1536 |
| parse_accuracy | 10 | 0.55 [0.25, 0.85] | 0.70 [0.45, 0.95] | 0.15 [-0.05, 0.40] | 0.3447 |
| dead_end_turns | 10 | 2.90 [0.90, 5.20] | 0.90 [0.00, 2.30] | -2.00 [-4.70, 0.60] | 0.2059 |
| unsupported_facts | 10 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 10 | 8.20 [4.40, 12.00] | 4.00 [2.00, 7.10] | -4.20 [-7.90, -0.70] | 0.0498* |
| ladder_fire_turns | 10 | 1.50 [0.80, 2.40] | 1.40 [0.70, 2.50] | -0.10 [-0.90, 0.60] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 10 | 40.0% [10.0%, 70.0%] | 70.0% [40.0%, 100.0%] | 30.0% [0.0%, 60.0%] | 0/3 | 0.2500 |
| faithful | 10 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 10 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 10 | 4.10 [3.20, 4.80] | 4.30 [3.80, 4.70] | 0.20 [-0.40, 1.10] | 0.7855 |
| negotiation_effectiveness | 9 | 3.56 [2.56, 4.44] | 4.00 [3.00, 5.00] | 0.44 [-0.67, 1.56] | 0.5839 |
| conversational_efficiency | 10 | 3.10 [2.40, 3.90] | 4.10 [3.40, 4.70] | 1.00 [0.00, 2.00] | 0.1344 |
| customer_experience | 10 | 3.10 [2.40, 3.90] | 4.00 [3.30, 4.70] | 0.90 [-0.10, 2.00] | 0.2021 |
| recovery_quality | 0 | — | — | — | — |

## Tier 3 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 5.30 [3.95, 6.90] | 6.40 [4.65, 8.20] | 1.10 [-0.05, 2.45] | 0.2223 |
| efficiency_ratio | 20 | 3.62 [2.60, 4.78] | 7.15 [3.08, 13.62] | 3.53 [-0.15, 9.58] | 0.2473 |
| simulated_latency_ms | 20 | 10054.12 [7335.01, 12983.34] | 22255.00 [8086.96, 46219.85] | 12200.88 [-840.83, 35025.44] | 0.8373 |
| parse_accuracy | 20 | 0.45 [0.28, 0.65] | 0.45 [0.28, 0.62] | 0.00 [-0.08, 0.08] | 0.6374 |
| dead_end_turns | 20 | 1.35 [0.40, 2.50] | 2.40 [1.00, 3.95] | 1.05 [-0.05, 2.35] | 0.2016 |
| unsupported_facts | 20 | 0.20 [0.00, 0.55] | 0.15 [0.00, 0.45] | -0.05 [-0.50, 0.40] | 1.0000 |
| availability_calls | 20 | 7.25 [5.20, 9.55] | 14.30 [6.15, 27.25] | 7.05 [-0.30, 19.15] | 0.2473 |
| ladder_fire_turns | 20 | 1.80 [1.25, 2.45] | 1.70 [1.30, 2.15] | -0.10 [-0.75, 0.50] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 80.0% [60.0%, 95.0%] | 65.0% [45.0%, 85.0%] | -15.0% [-30.0%, 0.0%] | 3/0 | 0.2500 |
| faithful | 20 | 90.0% [75.0%, 100.0%] | 95.0% [85.0%, 100.0%] | 5.0% [-10.0%, 25.0%] | 1/2 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.80 [4.55, 5.00] | 4.75 [4.45, 5.00] | -0.05 [-0.40, 0.25] | 0.8902 |
| negotiation_effectiveness | 20 | 4.40 [4.00, 4.75] | 4.10 [3.50, 4.65] | -0.30 [-0.85, 0.25] | 0.3329 |
| conversational_efficiency | 20 | 4.50 [4.10, 4.80] | 4.10 [3.55, 4.65] | -0.40 [-0.90, 0.05] | 0.1156 |
| customer_experience | 20 | 4.30 [3.85, 4.70] | 4.05 [3.45, 4.60] | -0.25 [-0.75, 0.20] | 0.3543 |
| recovery_quality | 20 | 4.50 [4.10, 4.85] | 4.15 [3.60, 4.65] | -0.35 [-0.90, 0.20] | 0.2809 |

## Tier 4 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 4.95 [3.70, 6.40] | 4.25 [3.50, 5.25] | -0.70 [-1.70, 0.15] | 0.2274 |
| efficiency_ratio | 20 | 4.08 [1.85, 6.95] | 3.65 [2.00, 6.38] | -0.43 [-3.38, 2.33] | 0.3443 |
| simulated_latency_ms | 20 | 12101.60 [5472.95, 21387.81] | 9417.88 [5426.05, 15814.14] | -2683.72 [-11917.81, 4594.01] | 0.1851 |
| parse_accuracy | 20 | 0.45 [0.28, 0.62] | 0.40 [0.20, 0.60] | -0.05 [-0.25, 0.15] | 0.6675 |
| dead_end_turns | 20 | 1.45 [0.20, 2.95] | 1.05 [0.25, 2.35] | -0.40 [-1.65, 0.55] | 0.7196 |
| unsupported_facts | 20 | 1.30 [0.00, 3.60] | 0.50 [0.00, 1.40] | -0.80 [-2.30, 0.20] | 0.4227 |
| availability_calls | 20 | 8.15 [3.70, 13.90] | 7.30 [4.00, 12.75] | -0.85 [-6.75, 4.65] | 0.3443 |
| ladder_fire_turns | 20 | 1.85 [0.95, 3.05] | 1.65 [1.00, 2.65] | -0.20 [-1.45, 0.90] | 0.7598 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 85.0% [70.0%, 100.0%] | 95.0% [85.0%, 100.0%] | 10.0% [0.0%, 25.0%] | 0/2 | 0.5000 |
| faithful | 20 | 90.0% [75.0%, 100.0%] | 90.0% [75.0%, 100.0%] | 0.0% [-15.0%, 15.0%] | 1/1 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.50 [4.20, 4.80] | 4.50 [4.15, 4.80] | 0.00 [-0.40, 0.35] | 0.9415 |
| negotiation_effectiveness | 16 | 4.19 [3.69, 4.62] | 4.25 [3.88, 4.62] | 0.06 [-0.38, 0.50] | 0.8605 |
| conversational_efficiency | 20 | 4.25 [3.80, 4.65] | 4.25 [3.80, 4.65] | 0.00 [-0.45, 0.40] | 1.0000 |
| customer_experience | 20 | 4.20 [3.75, 4.60] | 4.15 [3.70, 4.55] | -0.05 [-0.50, 0.35] | 0.8319 |
| recovery_quality | 16 | 4.12 [3.62, 4.56] | 4.25 [3.75, 4.69] | 0.12 [-0.44, 0.62] | 0.7590 |

## Tier 5 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 7.70 [6.55, 8.95] | 6.50 [5.45, 7.70] | -1.20 [-2.75, 0.30] | 0.1466 |
| efficiency_ratio | 20 | 4.60 [3.53, 5.77] | 5.87 [2.45, 11.88] | 1.27 [-2.20, 6.85] | 0.2552 |
| simulated_latency_ms | 20 | 17169.73 [13440.68, 21289.94] | 19558.41 [8902.16, 37111.85] | 2388.68 [-7803.01, 17374.24] | 0.1126 |
| parse_accuracy | 20 | 0.40 [0.23, 0.57] | 0.45 [0.28, 0.65] | 0.05 [-0.07, 0.17] | 0.4840 |
| dead_end_turns | 20 | 1.75 [0.90, 2.75] | 0.95 [0.20, 1.90] | -0.80 [-2.15, 0.50] | 0.1653 |
| unsupported_facts | 20 | 0.75 [0.05, 1.95] | 0.20 [0.00, 0.50] | -0.55 [-1.85, 0.30] | 0.6707 |
| availability_calls | 20 | 13.80 [10.60, 17.30] | 17.60 [7.35, 35.65] | 3.80 [-6.60, 20.55] | 0.2659 |
| ladder_fire_turns | 20 | 3.10 [2.50, 3.70] | 2.40 [1.80, 3.20] | -0.70 [-1.45, 0.10] | 0.0637 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 85.0% [70.0%, 100.0%] | 85.0% [70.0%, 100.0%] | 0.0% [-20.0%, 20.0%] | 2/2 | 1.0000 |
| faithful | 20 | 80.0% [60.0%, 95.0%] | 90.0% [75.0%, 100.0%] | 10.0% [-15.0%, 35.0%] | 2/4 | 0.6875 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 3.60 [3.10, 4.10] | 3.70 [3.35, 4.05] | 0.10 [-0.55, 0.75] | 0.7970 |
| negotiation_effectiveness | 20 | 2.85 [2.50, 3.25] | 3.05 [2.65, 3.45] | 0.20 [-0.25, 0.70] | 0.4911 |
| conversational_efficiency | 20 | 2.60 [2.20, 3.05] | 2.75 [2.45, 3.05] | 0.15 [-0.30, 0.60] | 0.5385 |
| customer_experience | 20 | 2.30 [1.90, 2.75] | 2.50 [2.15, 2.85] | 0.20 [-0.35, 0.70] | 0.4359 |
| recovery_quality | 20 | 2.70 [2.25, 3.15] | 3.00 [2.60, 3.40] | 0.30 [-0.15, 0.80] | 0.2842 |

## Tier 6 (n=19)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 19 | 5.05 [3.84, 6.58] | 5.89 [4.32, 7.63] | 0.84 [-0.16, 2.11] | 0.3985 |
| efficiency_ratio | 19 | 6.47 [2.05, 14.61] | 3.63 [2.50, 5.08] | -2.84 [-9.68, 0.84] | 0.4660 |
| simulated_latency_ms | 19 | 21800.51 [6024.04, 51588.42] | 9432.28 [6715.51, 12732.89] | -12368.23 [-39187.53, 1690.39] | 0.9839 |
| parse_accuracy | 19 | 0.39 [0.21, 0.58] | 0.42 [0.21, 0.63] | 0.03 [-0.21, 0.24] | 0.9155 |
| dead_end_turns | 19 | 0.79 [0.00, 1.89] | 1.37 [0.37, 2.63] | 0.58 [0.05, 1.26] | 0.0707 |
| unsupported_facts | 19 | 0.00 [0.00, 0.00] | 0.84 [0.00, 2.32] | 0.84 [0.00, 2.32] | 0.3711 |
| availability_calls | 19 | 12.95 [4.11, 29.21] | 7.26 [5.00, 10.16] | -5.68 [-19.37, 1.68] | 0.4660 |
| ladder_fire_turns | 19 | 1.32 [0.95, 1.74] | 1.63 [1.00, 2.53] | 0.32 [-0.11, 0.84] | 0.2755 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 19 | 84.2% [68.4%, 100.0%] | 78.9% [57.9%, 94.7%] | -5.3% [-15.8%, 0.0%] | 1/0 | 1.0000 |
| faithful | 19 | 100.0% [100.0%, 100.0%] | 89.5% [73.7%, 100.0%] | -10.5% [-26.3%, 0.0%] | 2/0 | 0.5000 |
| refusal_accepted | 19 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 19 | 4.68 [4.42, 4.89] | 4.32 [3.79, 4.74] | -0.37 [-0.89, 0.11] | 0.1997 |
| negotiation_effectiveness | 15 | 3.93 [3.40, 4.47] | 3.60 [2.80, 4.33] | -0.33 [-1.00, 0.33] | 0.3929 |
| conversational_efficiency | 19 | 4.26 [3.74, 4.68] | 3.68 [3.00, 4.32] | -0.58 [-1.32, 0.11] | 0.1496 |
| customer_experience | 19 | 4.11 [3.47, 4.63] | 3.63 [2.95, 4.26] | -0.47 [-1.16, 0.16] | 0.1638 |
| recovery_quality | 0 | — | — | — | — |

## Tier 7 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 4.90 [4.05, 6.00] | 4.70 [4.10, 5.40] | -0.20 [-1.55, 0.95] | 0.9771 |
| efficiency_ratio | 0 | — | — | — | — |
| simulated_latency_ms | 20 | 9775.07 [4611.19, 17128.34] | 6222.22 [3636.93, 9115.06] | -3552.85 [-11772.82, 2223.56] | 0.9553 |
| parse_accuracy | 0 | — | — | — | — |
| dead_end_turns | 20 | 1.05 [0.30, 2.20] | 0.50 [0.20, 0.85] | -0.55 [-1.80, 0.25] | 0.5469 |
| unsupported_facts | 20 | 0.50 [0.00, 1.50] | 0.00 [0.00, 0.00] | -0.50 [-1.50, 0.00] | 1.0000 |
| availability_calls | 20 | 6.20 [2.95, 10.50] | 4.15 [2.20, 6.45] | -2.05 [-6.90, 1.75] | 0.4431 |
| ladder_fire_turns | 20 | 1.20 [0.50, 2.25] | 0.70 [0.40, 1.00] | -0.50 [-1.60, 0.25] | 0.4584 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 20 | 95.0% [85.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 5.0% [0.0%, 15.0%] | 0/1 | 1.0000 |
| refusal_accepted | 20 | 95.0% [85.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 5.0% [0.0%, 15.0%] | 0/1 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.50 [4.00, 4.85] | 4.50 [4.05, 4.85] | 0.00 [-0.60, 0.65] | 0.9434 |
| negotiation_effectiveness | 0 | — | — | — | — |
| conversational_efficiency | 20 | 3.30 [3.00, 3.60] | 3.35 [3.00, 3.70] | 0.05 [-0.40, 0.50] | 0.9015 |
| customer_experience | 0 | — | — | — | — |
| recovery_quality | 0 | — | — | — | — |
