# Paired comparison — `20260607_164034__expansion__927f9c2__representative_reduced` vs `20260606_205242__baseline__e1626fa__representative_reduced`

**Pairing:** 119 valid pairs out of 120 matched scenario-runs (excluded 1 pairs where either side had `termination=error` or missing derived metrics). Baseline-only keys: 0, candidate-only: 0.

## Overall (all tiers)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 119 | 6.32 [5.69, 6.97] | 5.69 [5.08, 6.33] | -0.63 [-1.20, -0.06] | 0.0118* |
| efficiency_ratio | 98 | 4.61 [3.16, 6.52] | 4.92 [3.57, 6.82] | 0.31 [-1.83, 2.51] | 0.1603 |
| simulated_latency_ms | 119 | 10049.32 [6070.51, 15690.71] | 12995.01 [9271.30, 18658.71] | 2945.69 [-3542.27, 9694.94] | 0.0001*** |
| parse_accuracy | 98 | 0.42 [0.34, 0.50] | 0.45 [0.37, 0.54] | 0.03 [-0.04, 0.10] | 0.3530 |
| dead_end_turns | 119 | 3.08 [2.44, 3.75] | 1.42 [0.98, 1.91] | -1.66 [-2.30, -1.00] | 0.0000*** |
| unsupported_facts | 119 | 0.59 [0.12, 1.30] | 0.46 [0.12, 0.95] | -0.13 [-0.96, 0.58] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 119 | 63.0% [54.6%, 71.4%] | 65.5% [56.3%, 73.9%] | 2.5% [-4.2%, 9.2%] | 7/10 | 0.6291 |
| faithful | 119 | 95.0% [90.8%, 98.3%] | 92.4% [87.4%, 96.6%] | -2.5% [-9.2%, 4.2%] | 9/6 | 0.6072 |
| refusal_accepted | 119 | 16.8% [10.1%, 23.5%] | 16.0% [9.2%, 22.7%] | -0.8% [-2.5%, 0.0%] | 1/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 119 | 4.60 [4.45, 4.73] | 4.44 [4.26, 4.60] | -0.16 [-0.37, 0.05] | 0.1463 |
| negotiation_effectiveness | 87 | 3.36 [3.11, 3.60] | 3.78 [3.53, 4.02] | 0.43 [0.11, 0.72] | 0.0083** |
| conversational_efficiency | 119 | 3.74 [3.52, 3.96] | 3.77 [3.55, 3.98] | 0.03 [-0.20, 0.26] | 0.8185 |
| customer_experience | 99 | 3.34 [3.08, 3.61] | 3.73 [3.46, 3.99] | 0.38 [0.12, 0.66] | 0.0080** |
| recovery_quality | 56 | 3.45 [3.14, 3.73] | 3.75 [3.41, 4.07] | 0.30 [-0.11, 0.71] | 0.1893 |

## Tier 1 (n=10)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 10 | 5.20 [2.70, 8.20] | 4.10 [2.00, 7.00] | -1.10 [-3.00, 0.10] | 0.2031 |
| efficiency_ratio | 10 | 5.10 [1.40, 10.20] | 3.20 [1.00, 6.30] | -1.90 [-6.10, 1.80] | 0.3613 |
| simulated_latency_ms | 10 | 6004.89 [2584.76, 10417.76] | 4810.09 [1919.02, 8882.16] | -1194.80 [-4549.14, 1740.44] | 0.3590 |
| parse_accuracy | 10 | 0.50 [0.25, 0.75] | 0.60 [0.35, 0.85] | 0.10 [-0.10, 0.35] | 0.5862 |
| dead_end_turns | 10 | 2.50 [0.00, 6.00] | 1.30 [0.00, 3.20] | -1.20 [-4.20, 1.20] | 0.5862 |
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
| negotiation_effectiveness | 3 | 2.67 [1.00, 4.00] | 3.00 [2.00, 5.00] | 0.33 [-1.00, 1.00] | 0.7728 |
| conversational_efficiency | 10 | 3.80 [2.80, 4.70] | 4.40 [3.50, 5.00] | 0.60 [0.00, 1.30] | 0.1814 |
| customer_experience | 10 | 3.80 [2.80, 4.70] | 4.40 [3.50, 5.00] | 0.60 [0.00, 1.30] | 0.1814 |
| recovery_quality | 0 | — | — | — | — |

## Tier 2 (n=10)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 10 | 7.50 [4.80, 10.20] | 8.30 [5.50, 11.10] | 0.80 [-2.00, 3.60] | 0.8501 |
| efficiency_ratio | 10 | 6.30 [3.80, 9.10] | 8.20 [4.40, 12.00] | 1.90 [-1.90, 6.10] | 0.6115 |
| simulated_latency_ms | 10 | 7846.42 [4993.41, 11535.97] | 10208.58 [5406.47, 14941.27] | 2362.16 [-1832.63, 6886.10] | 1.0000 |
| parse_accuracy | 10 | 0.50 [0.20, 0.75] | 0.55 [0.25, 0.85] | 0.05 [-0.25, 0.30] | 0.8501 |
| dead_end_turns | 10 | 5.30 [2.50, 8.30] | 2.90 [0.90, 5.20] | -2.40 [-5.20, 0.60] | 0.0820 |
| unsupported_facts | 10 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 10 | 50.0% [20.0%, 80.0%] | 40.0% [10.0%, 70.0%] | -10.0% [-40.0%, 20.0%] | 2/1 | 1.0000 |
| faithful | 10 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 10 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 10 | 4.90 [4.70, 5.00] | 4.10 [3.20, 4.80] | -0.80 [-1.60, 0.00] | 0.1736 |
| negotiation_effectiveness | 10 | 3.50 [2.60, 4.30] | 3.40 [2.50, 4.30] | -0.10 [-1.20, 1.10] | 0.9432 |
| conversational_efficiency | 10 | 3.60 [2.70, 4.40] | 3.10 [2.40, 3.90] | -0.50 [-1.50, 0.50] | 0.4291 |
| customer_experience | 10 | 3.50 [2.60, 4.40] | 3.10 [2.40, 3.90] | -0.40 [-1.40, 0.70] | 0.5697 |
| recovery_quality | 0 | — | — | — | — |

## Tier 3 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 7.10 [5.60, 8.75] | 5.30 [3.95, 6.90] | -1.80 [-2.95, -0.80] | 0.0022** |
| efficiency_ratio | 20 | 8.65 [2.55, 17.27] | 3.62 [2.60, 4.78] | -5.03 [-13.02, 0.65] | 0.5933 |
| simulated_latency_ms | 20 | 27937.59 [5890.54, 59962.20] | 10054.12 [7335.01, 12983.34] | -17883.47 [-48431.52, 3111.67] | 0.3411 |
| parse_accuracy | 20 | 0.42 [0.28, 0.57] | 0.45 [0.28, 0.65] | 0.03 [-0.08, 0.13] | 0.7656 |
| dead_end_turns | 20 | 3.95 [2.40, 5.70] | 1.35 [0.40, 2.50] | -2.60 [-4.25, -1.10] | 0.0054** |
| unsupported_facts | 20 | 0.00 [0.00, 0.00] | 0.20 [0.00, 0.55] | 0.20 [0.00, 0.55] | 0.3711 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 65.0% [45.0%, 85.0%] | 80.0% [60.0%, 95.0%] | 15.0% [0.0%, 30.0%] | 0/3 | 0.2500 |
| faithful | 20 | 100.0% [100.0%, 100.0%] | 90.0% [75.0%, 100.0%] | -10.0% [-25.0%, 0.0%] | 2/0 | 0.5000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.85 [4.55, 5.00] | 4.80 [4.55, 5.00] | -0.05 [-0.35, 0.25] | 1.0000 |
| negotiation_effectiveness | 20 | 3.60 [3.10, 4.10] | 4.40 [4.00, 4.75] | 0.80 [0.15, 1.45] | 0.0252* |
| conversational_efficiency | 20 | 4.10 [3.65, 4.55] | 4.50 [4.10, 4.80] | 0.40 [-0.05, 0.90] | 0.1463 |
| customer_experience | 20 | 3.55 [3.05, 4.00] | 4.30 [3.85, 4.70] | 0.75 [0.25, 1.30] | 0.0197* |
| recovery_quality | 20 | 3.90 [3.40, 4.35] | 4.50 [4.10, 4.85] | 0.60 [0.00, 1.20] | 0.0590 |

## Tier 4 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 6.40 [5.15, 7.70] | 4.95 [3.70, 6.40] | -1.45 [-3.00, 0.05] | 0.0697 |
| efficiency_ratio | 19 | 2.95 [2.11, 3.84] | 4.26 [1.89, 7.24] | 1.32 [-0.84, 3.92] | 0.8246 |
| simulated_latency_ms | 20 | 6555.23 [4956.25, 8334.27] | 12101.60 [5472.95, 21387.81] | 5546.37 [-599.83, 13923.68] | 0.4666 |
| parse_accuracy | 19 | 0.34 [0.18, 0.50] | 0.42 [0.24, 0.61] | 0.08 [-0.08, 0.26] | 0.4070 |
| dead_end_turns | 20 | 3.35 [2.10, 4.70] | 1.45 [0.20, 2.95] | -1.90 [-3.60, -0.35] | 0.0436* |
| unsupported_facts | 20 | 1.00 [0.00, 2.25] | 1.30 [0.00, 3.60] | 0.30 [-1.80, 3.00] | 0.8923 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 90.0% [75.0%, 100.0%] | 85.0% [70.0%, 100.0%] | -5.0% [-25.0%, 15.0%] | 3/2 | 1.0000 |
| faithful | 20 | 85.0% [70.0%, 100.0%] | 90.0% [75.0%, 100.0%] | 5.0% [-15.0%, 25.0%] | 2/3 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.55 [4.25, 4.80] | 4.50 [4.20, 4.80] | -0.05 [-0.30, 0.20] | 0.7768 |
| negotiation_effectiveness | 16 | 3.44 [2.94, 3.94] | 4.19 [3.69, 4.62] | 0.75 [0.00, 1.44] | 0.0947 |
| conversational_efficiency | 20 | 3.80 [3.40, 4.20] | 4.25 [3.80, 4.65] | 0.45 [0.00, 0.90] | 0.0972 |
| customer_experience | 20 | 3.50 [3.00, 3.95] | 4.20 [3.75, 4.60] | 0.70 [0.10, 1.30] | 0.0446* |
| recovery_quality | 16 | 3.50 [2.94, 4.06] | 4.12 [3.62, 4.56] | 0.62 [-0.12, 1.38] | 0.1725 |

## Tier 5 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 8.70 [7.45, 9.90] | 7.70 [6.55, 8.95] | -1.00 [-2.55, 0.40] | 0.2683 |
| efficiency_ratio | 20 | 3.03 [2.32, 3.98] | 4.60 [3.53, 5.77] | 1.57 [0.50, 2.73] | 0.0140* |
| simulated_latency_ms | 20 | 10430.37 [8294.18, 13107.74] | 17169.73 [13440.68, 21289.94] | 6739.36 [3200.93, 10703.47] | 0.0034** |
| parse_accuracy | 20 | 0.42 [0.25, 0.62] | 0.40 [0.23, 0.57] | -0.02 [-0.17, 0.12] | 0.8241 |
| dead_end_turns | 20 | 4.55 [3.05, 6.25] | 1.75 [0.90, 2.75] | -2.80 [-4.30, -1.50] | 0.0015** |
| unsupported_facts | 20 | 0.00 [0.00, 0.00] | 0.75 [0.05, 1.95] | 0.75 [0.05, 1.95] | 0.0975 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 80.0% [60.0%, 95.0%] | 85.0% [70.0%, 100.0%] | 5.0% [-15.0%, 25.0%] | 2/3 | 1.0000 |
| faithful | 20 | 100.0% [100.0%, 100.0%] | 80.0% [60.0%, 95.0%] | -20.0% [-40.0%, -5.0%] | 4/0 | 0.1250 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.05 [3.50, 4.55] | 3.60 [3.10, 4.10] | -0.45 [-1.25, 0.40] | 0.4062 |
| negotiation_effectiveness | 20 | 2.75 [2.35, 3.15] | 2.85 [2.50, 3.25] | 0.10 [-0.45, 0.70] | 0.7952 |
| conversational_efficiency | 20 | 2.95 [2.50, 3.40] | 2.60 [2.20, 3.05] | -0.35 [-1.00, 0.35] | 0.3690 |
| customer_experience | 20 | 2.25 [1.85, 2.65] | 2.30 [1.90, 2.75] | 0.05 [-0.55, 0.70] | 0.9225 |
| recovery_quality | 20 | 2.95 [2.50, 3.40] | 2.70 [2.25, 3.15] | -0.25 [-0.95, 0.45] | 0.5035 |

## Tier 6 (n=19)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 19 | 5.63 [4.32, 7.21] | 5.05 [3.84, 6.58] | -0.58 [-1.37, 0.05] | 0.1747 |
| efficiency_ratio | 19 | 2.53 [1.71, 3.47] | 6.47 [2.05, 14.61] | 3.95 [0.00, 11.37] | 0.1068 |
| simulated_latency_ms | 19 | 7004.89 [4850.23, 9555.68] | 21800.51 [6024.04, 51588.42] | 14795.62 [334.61, 42618.59] | 0.0559 |
| parse_accuracy | 19 | 0.39 [0.24, 0.58] | 0.39 [0.21, 0.58] | 0.00 [-0.11, 0.11] | 0.8415 |
| dead_end_turns | 19 | 2.05 [1.05, 3.32] | 0.79 [0.00, 1.89] | -1.26 [-2.63, -0.11] | 0.0266* |
| unsupported_facts | 19 | 1.95 [0.00, 5.63] | 0.00 [0.00, 0.00] | -1.95 [-5.63, 0.00] | 0.3711 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 19 | 84.2% [68.4%, 100.0%] | 84.2% [68.4%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 19 | 89.5% [73.7%, 100.0%] | 100.0% [100.0%, 100.0%] | 10.5% [0.0%, 26.3%] | 0/2 | 0.5000 |
| refusal_accepted | 19 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 19 | 4.47 [4.21, 4.74] | 4.68 [4.42, 4.89] | 0.21 [-0.11, 0.53] | 0.2402 |
| negotiation_effectiveness | 18 | 3.72 [3.17, 4.22] | 4.11 [3.61, 4.56] | 0.39 [-0.11, 0.89] | 0.1735 |
| conversational_efficiency | 19 | 3.89 [3.26, 4.47] | 4.26 [3.74, 4.68] | 0.37 [-0.05, 0.79] | 0.1616 |
| customer_experience | 19 | 3.79 [3.16, 4.37] | 4.11 [3.47, 4.63] | 0.32 [-0.16, 0.74] | 0.2091 |
| recovery_quality | 0 | — | — | — | — |

## Tier 7 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 3.70 [3.25, 4.15] | 4.90 [4.05, 6.00] | 1.20 [0.10, 2.55] | 0.1029 |
| efficiency_ratio | 0 | — | — | — | — |
| simulated_latency_ms | 20 | 1289.97 [707.66, 1919.48] | 9775.07 [4611.19, 17128.34] | 8485.10 [3411.37, 15965.56] | 0.0020** |
| parse_accuracy | 0 | — | — | — | — |
| dead_end_turns | 20 | 0.60 [0.20, 1.10] | 1.05 [0.30, 2.20] | 0.45 [-0.40, 1.75] | 0.7912 |
| unsupported_facts | 20 | 0.00 [0.00, 0.00] | 0.50 [0.00, 1.50] | 0.50 [0.00, 1.50] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 20 | 100.0% [100.0%, 100.0%] | 95.0% [85.0%, 100.0%] | -5.0% [-15.0%, 0.0%] | 1/0 | 1.0000 |
| refusal_accepted | 20 | 100.0% [100.0%, 100.0%] | 95.0% [85.0%, 100.0%] | -5.0% [-15.0%, 0.0%] | 1/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.85 [4.60, 5.00] | 4.50 [4.00, 4.85] | -0.35 [-0.85, 0.00] | 0.1198 |
| negotiation_effectiveness | 0 | — | — | — | — |
| conversational_efficiency | 20 | 4.00 [3.60, 4.35] | 3.30 [3.00, 3.60] | -0.70 [-1.15, -0.25] | 0.0155* |
| customer_experience | 0 | — | — | — | — |
| recovery_quality | 0 | — | — | — | — |
