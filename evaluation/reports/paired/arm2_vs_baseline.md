# Paired comparison — `20260607_014848__nlp_arm2__e1626fa__representative_reduced` vs `20260606_205242__baseline__e1626fa__representative_reduced`

**Pairing:** 119 valid pairs out of 120 matched scenario-runs (excluded 1 pairs where either side had `termination=error` or missing derived metrics). Baseline-only keys: 0, candidate-only: 0.

## Overall (all tiers)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 119 | 6.35 [5.72, 7.03] | 7.14 [6.50, 7.82] | 0.79 [0.13, 1.47] | 0.0167* |
| efficiency_ratio | 98 | 4.62 [3.17, 6.52] | 9.08 [5.95, 13.01] | 4.45 [0.78, 8.77] | 0.0160* |
| simulated_latency_ms | 119 | 10058.52 [6061.03, 15712.81] | 23396.45 [13028.80, 36399.09] | 13337.93 [1752.56, 26807.25] | 0.1119 |
| parse_accuracy | 98 | 0.41 [0.33, 0.49] | 0.47 [0.39, 0.56] | 0.06 [-0.01, 0.13] | 0.0999 |
| dead_end_turns | 119 | 3.13 [2.47, 3.82] | 3.38 [2.73, 4.07] | 0.24 [-0.51, 0.99] | 0.4691 |
| unsupported_facts | 119 | 0.59 [0.11, 1.32] | 0.23 [0.05, 0.45] | -0.36 [-0.99, 0.10] | 0.2829 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 119 | 62.2% [52.9%, 70.6%] | 54.6% [45.4%, 63.9%] | -7.6% [-16.8%, 1.7%] | 20/11 | 0.1496 |
| faithful | 119 | 95.0% [90.8%, 98.3%] | 95.8% [91.6%, 99.2%] | 0.8% [-4.2%, 5.9%] | 4/5 | 1.0000 |
| refusal_accepted | 119 | 16.8% [10.1%, 23.5%] | 16.8% [10.1%, 23.5%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 119 | 4.61 [4.45, 4.74] | 4.43 [4.24, 4.60] | -0.18 [-0.39, 0.04] | 0.1334 |
| negotiation_effectiveness | 89 | 3.35 [3.10, 3.60] | 2.90 [2.69, 3.12] | -0.45 [-0.74, -0.17] | 0.0050** |
| conversational_efficiency | 119 | 3.74 [3.52, 3.96] | 3.36 [3.14, 3.58] | -0.38 [-0.65, -0.12] | 0.0070** |
| customer_experience | 99 | 3.34 [3.08, 3.61] | 3.09 [2.83, 3.34] | -0.25 [-0.54, 0.02] | 0.0732 |
| recovery_quality | 57 | 3.47 [3.18, 3.79] | 3.05 [2.77, 3.33] | -0.42 [-0.77, -0.07] | 0.0287* |

## Tier 1 (n=10)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 10 | 5.20 [2.70, 8.20] | 3.30 [2.10, 5.30] | -1.90 [-4.50, 0.00] | 0.1675 |
| efficiency_ratio | 10 | 5.10 [1.40, 10.20] | 2.20 [1.10, 4.00] | -2.90 [-8.30, 1.20] | 0.3613 |
| simulated_latency_ms | 10 | 6004.89 [2584.76, 10417.76] | 2748.28 [1842.76, 4248.95] | -3256.61 [-7847.64, 62.18] | 0.2622 |
| parse_accuracy | 10 | 0.50 [0.25, 0.75] | 0.50 [0.30, 0.70] | 0.00 [-0.20, 0.25] | 0.7855 |
| dead_end_turns | 10 | 2.50 [0.00, 6.00] | 1.00 [0.00, 2.80] | -1.50 [-5.10, 1.60] | 0.4227 |
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
| temporal_understanding | 10 | 4.70 [4.10, 5.00] | 4.90 [4.70, 5.00] | 0.20 [-0.30, 0.90] | 1.0000 |
| negotiation_effectiveness | 5 | 3.00 [1.80, 4.20] | 3.80 [2.80, 4.60] | 0.80 [0.20, 1.40] | 0.1736 |
| conversational_efficiency | 10 | 3.80 [2.80, 4.70] | 4.70 [4.10, 5.00] | 0.90 [0.20, 1.70] | 0.0975 |
| customer_experience | 10 | 3.80 [2.80, 4.70] | 4.70 [4.10, 5.00] | 0.90 [0.20, 1.70] | 0.0975 |
| recovery_quality | 0 | — | — | — | — |

## Tier 2 (n=10)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 10 | 7.50 [4.80, 10.20] | 10.20 [8.00, 12.00] | 2.70 [-0.50, 5.90] | 0.1290 |
| efficiency_ratio | 10 | 6.30 [3.80, 9.10] | 18.30 [7.10, 35.00] | 12.00 [0.50, 29.60] | 0.1065 |
| simulated_latency_ms | 10 | 7846.42 [4993.41, 11535.97] | 19657.50 [6921.16, 36416.01] | 11811.08 [-1617.01, 29872.94] | 0.4148 |
| parse_accuracy | 10 | 0.50 [0.20, 0.75] | 0.80 [0.50, 1.00] | 0.30 [0.10, 0.55] | 0.0947 |
| dead_end_turns | 10 | 5.30 [2.50, 8.30] | 5.10 [2.10, 8.30] | -0.20 [-2.90, 2.70] | 0.7995 |
| unsupported_facts | 10 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 10 | 50.0% [20.0%, 80.0%] | 30.0% [0.0%, 60.0%] | -20.0% [-60.0%, 20.0%] | 3/1 | 0.6250 |
| faithful | 10 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 10 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 10 | 4.90 [4.70, 5.00] | 4.80 [4.40, 5.00] | -0.10 [-0.60, 0.30] | 1.0000 |
| negotiation_effectiveness | 10 | 3.50 [2.60, 4.30] | 2.40 [2.00, 3.00] | -1.10 [-2.00, -0.20] | 0.0707 |
| conversational_efficiency | 10 | 3.60 [2.70, 4.40] | 2.70 [2.20, 3.40] | -0.90 [-2.00, 0.20] | 0.1311 |
| customer_experience | 10 | 3.50 [2.60, 4.40] | 2.60 [2.10, 3.20] | -0.90 [-2.00, 0.20] | 0.1934 |
| recovery_quality | 0 | — | — | — | — |

## Tier 3 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 7.10 [5.60, 8.75] | 8.25 [6.60, 9.90] | 1.15 [-0.70, 3.05] | 0.2836 |
| efficiency_ratio | 20 | 8.65 [2.55, 17.27] | 10.47 [4.15, 18.65] | 1.82 [-9.18, 12.55] | 0.4011 |
| simulated_latency_ms | 20 | 27937.59 [5890.54, 59962.20] | 33132.37 [9738.92, 62980.47] | 5194.79 [-35721.15, 44817.31] | 0.6143 |
| parse_accuracy | 20 | 0.42 [0.28, 0.57] | 0.47 [0.30, 0.65] | 0.05 [-0.08, 0.20] | 0.5716 |
| dead_end_turns | 20 | 3.95 [2.40, 5.70] | 4.95 [3.20, 6.80] | 1.00 [-1.20, 3.20] | 0.3871 |
| unsupported_facts | 20 | 0.00 [0.00, 0.00] | 0.30 [0.00, 0.90] | 0.30 [0.00, 0.90] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 65.0% [45.0%, 85.0%] | 55.0% [35.0%, 75.0%] | -10.0% [-35.0%, 15.0%] | 4/2 | 0.6875 |
| faithful | 20 | 100.0% [100.0%, 100.0%] | 95.0% [85.0%, 100.0%] | -5.0% [-15.0%, 0.0%] | 1/0 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.85 [4.55, 5.00] | 4.85 [4.60, 5.00] | 0.00 [-0.35, 0.40] | 0.7893 |
| negotiation_effectiveness | 20 | 3.60 [3.10, 4.10] | 3.05 [2.60, 3.50] | -0.55 [-1.20, 0.15] | 0.1251 |
| conversational_efficiency | 20 | 4.10 [3.65, 4.55] | 3.50 [3.00, 4.05] | -0.60 [-1.25, 0.05] | 0.1164 |
| customer_experience | 20 | 3.55 [3.05, 4.00] | 3.00 [2.55, 3.50] | -0.55 [-1.10, 0.05] | 0.0956 |
| recovery_quality | 20 | 3.90 [3.40, 4.35] | 3.30 [2.85, 3.75] | -0.60 [-1.15, 0.00] | 0.0681 |

## Tier 4 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 6.40 [5.15, 7.70] | 6.75 [5.25, 8.30] | 0.35 [-1.25, 1.95] | 0.6971 |
| efficiency_ratio | 19 | 2.95 [2.11, 3.84] | 6.42 [2.39, 13.26] | 3.47 [-0.53, 10.29] | 0.4843 |
| simulated_latency_ms | 20 | 6555.23 [4956.25, 8334.27] | 18481.65 [5459.48, 42631.33] | 11926.42 [-1043.23, 35713.93] | 0.5883 |
| parse_accuracy | 19 | 0.34 [0.18, 0.50] | 0.45 [0.24, 0.68] | 0.11 [-0.05, 0.26] | 0.2402 |
| dead_end_turns | 20 | 3.35 [2.10, 4.70] | 4.00 [2.40, 5.75] | 0.65 [-1.00, 2.30] | 0.4763 |
| unsupported_facts | 20 | 1.00 [0.00, 2.25] | 0.00 [0.00, 0.00] | -1.00 [-2.25, 0.00] | 0.1814 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 90.0% [75.0%, 100.0%] | 75.0% [55.0%, 90.0%] | -15.0% [-40.0%, 10.0%] | 5/2 | 0.4531 |
| faithful | 20 | 85.0% [70.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 15.0% [0.0%, 30.0%] | 0/3 | 0.2500 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.55 [4.25, 4.80] | 4.35 [3.95, 4.70] | -0.20 [-0.65, 0.25] | 0.4947 |
| negotiation_effectiveness | 17 | 3.47 [3.00, 3.94] | 3.18 [2.71, 3.71] | -0.29 [-0.94, 0.35] | 0.4498 |
| conversational_efficiency | 20 | 3.80 [3.40, 4.20] | 3.50 [3.00, 4.00] | -0.30 [-0.85, 0.25] | 0.2442 |
| customer_experience | 20 | 3.50 [3.00, 3.95] | 3.35 [2.80, 3.90] | -0.15 [-0.75, 0.45] | 0.5570 |
| recovery_quality | 17 | 3.59 [3.06, 4.12] | 3.29 [2.82, 3.82] | -0.29 [-0.94, 0.41] | 0.4427 |

## Tier 5 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 8.70 [7.45, 9.90] | 8.75 [7.50, 9.95] | 0.05 [-1.20, 1.30] | 0.9584 |
| efficiency_ratio | 20 | 3.03 [2.32, 3.98] | 9.13 [3.12, 17.35] | 6.10 [0.00, 14.38] | 0.1384 |
| simulated_latency_ms | 20 | 10430.37 [8294.18, 13107.74] | 46482.34 [10641.62, 94858.89] | 36051.97 [123.15, 84803.64] | 0.4666 |
| parse_accuracy | 20 | 0.42 [0.25, 0.62] | 0.38 [0.20, 0.55] | -0.05 [-0.20, 0.10] | 0.5877 |
| dead_end_turns | 20 | 4.55 [3.05, 6.25] | 3.75 [2.70, 4.85] | -0.80 [-2.50, 0.85] | 0.3773 |
| unsupported_facts | 20 | 0.00 [0.00, 0.00] | 0.30 [0.00, 0.90] | 0.30 [0.00, 0.90] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 80.0% [60.0%, 95.0%] | 65.0% [45.0%, 85.0%] | -15.0% [-40.0%, 10.0%] | 5/2 | 0.4531 |
| faithful | 20 | 100.0% [100.0%, 100.0%] | 95.0% [85.0%, 100.0%] | -5.0% [-15.0%, 0.0%] | 1/0 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.05 [3.50, 4.55] | 3.95 [3.40, 4.45] | -0.10 [-0.75, 0.55] | 0.7193 |
| negotiation_effectiveness | 20 | 2.75 [2.35, 3.15] | 2.45 [2.10, 2.80] | -0.30 [-0.65, 0.05] | 0.1200 |
| conversational_efficiency | 20 | 2.95 [2.50, 3.40] | 2.55 [2.15, 3.00] | -0.40 [-1.00, 0.15] | 0.2195 |
| customer_experience | 20 | 2.25 [1.85, 2.65] | 2.15 [1.75, 2.55] | -0.10 [-0.55, 0.35] | 0.8128 |
| recovery_quality | 20 | 2.95 [2.50, 3.40] | 2.60 [2.15, 3.05] | -0.35 [-0.95, 0.20] | 0.3088 |

## Tier 6 (n=19)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 19 | 5.84 [4.37, 7.47] | 7.42 [5.79, 9.05] | 1.58 [0.16, 3.21] | 0.1116 |
| efficiency_ratio | 19 | 2.61 [1.74, 3.58] | 8.97 [2.61, 20.58] | 6.37 [0.24, 17.55] | 0.0727 |
| simulated_latency_ms | 19 | 7062.51 [4903.62, 9485.84] | 28886.86 [6194.97, 71786.90] | 21824.35 [-24.36, 63509.50] | 0.3443 |
| parse_accuracy | 19 | 0.37 [0.21, 0.55] | 0.42 [0.24, 0.61] | 0.05 [-0.13, 0.21] | 0.6078 |
| dead_end_turns | 19 | 2.42 [1.16, 4.00] | 3.74 [2.26, 5.32] | 1.32 [-0.58, 3.26] | 0.2203 |
| unsupported_facts | 19 | 1.95 [0.00, 5.63] | 0.53 [0.00, 1.42] | -1.42 [-4.37, 0.32] | 0.4227 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 19 | 78.9% [57.9%, 94.7%] | 73.7% [52.6%, 89.5%] | -5.3% [-26.3%, 15.8%] | 3/2 | 1.0000 |
| faithful | 19 | 89.5% [73.7%, 100.0%] | 89.5% [73.7%, 100.0%] | 0.0% [-15.8%, 15.8%] | 1/1 | 1.0000 |
| refusal_accepted | 19 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 19 | 4.53 [4.26, 4.79] | 4.58 [4.26, 4.84] | 0.05 [-0.21, 0.32] | 0.7768 |
| negotiation_effectiveness | 17 | 3.65 [3.06, 4.18] | 3.00 [2.47, 3.53] | -0.65 [-1.47, 0.12] | 0.1414 |
| conversational_efficiency | 19 | 3.89 [3.26, 4.47] | 3.47 [2.84, 4.11] | -0.42 [-1.21, 0.32] | 0.3877 |
| customer_experience | 19 | 3.79 [3.16, 4.37] | 3.32 [2.74, 3.89] | -0.47 [-1.11, 0.11] | 0.1674 |
| recovery_quality | 0 | — | — | — | — |

## Tier 7 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 3.70 [3.25, 4.15] | 4.95 [4.35, 5.60] | 1.25 [0.45, 2.10] | 0.0105* |
| efficiency_ratio | 0 | — | — | — | — |
| simulated_latency_ms | 20 | 1289.97 [707.66, 1919.48] | 2467.12 [1684.88, 3392.55] | 1177.15 [160.90, 2396.70] | 0.0702 |
| parse_accuracy | 0 | — | — | — | — |
| dead_end_turns | 20 | 0.60 [0.20, 1.10] | 0.80 [0.35, 1.35] | 0.20 [-0.30, 0.75] | 0.4299 |
| unsupported_facts | 20 | 0.00 [0.00, 0.00] | 0.25 [0.00, 0.75] | 0.25 [0.00, 0.75] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 20 | 100.0% [100.0%, 100.0%] | 95.0% [85.0%, 100.0%] | -5.0% [-15.0%, 0.0%] | 1/0 | 1.0000 |
| refusal_accepted | 20 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.85 [4.60, 5.00] | 4.00 [3.35, 4.60] | -0.85 [-1.60, -0.15] | 0.0505 |
| negotiation_effectiveness | 0 | — | — | — | — |
| conversational_efficiency | 20 | 4.00 [3.60, 4.35] | 3.45 [3.00, 3.85] | -0.55 [-1.10, 0.00] | 0.0941 |
| customer_experience | 0 | — | — | — | — |
| recovery_quality | 0 | — | — | — | — |
