# Paired comparison — `20260608_221848__nlp_arm3_expansion__4eadd22__representative_reduced` vs `20260606_205242__baseline__e1626fa__representative_reduced`

**Pairing:** 120 valid pairs out of 120 matched scenario-runs (excluded 0 pairs where either side had `termination=error` or missing derived metrics). Baseline-only keys: 0, candidate-only: 0.

## Overall (all tiers)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 120 | 6.37 [5.73, 7.05] | 5.43 [4.85, 6.07] | -0.93 [-1.57, -0.32] | 0.0013** |
| efficiency_ratio | 99 | 4.63 [3.18, 6.58] | 4.88 [3.42, 6.88] | 0.25 [-1.50, 1.97] | 0.6142 |
| simulated_latency_ms | 120 | 10072.43 [6071.93, 15721.83] | 12040.65 [8188.19, 17377.55] | 1968.23 [-2833.30, 6318.55] | 0.0203* |
| parse_accuracy | 99 | 0.41 [0.33, 0.49] | 0.45 [0.37, 0.54] | 0.04 [-0.03, 0.11] | 0.2287 |
| dead_end_turns | 120 | 3.15 [2.48, 3.86] | 1.27 [0.87, 1.76] | -1.88 [-2.58, -1.21] | 0.0000*** |
| unsupported_facts | 120 | 0.58 [0.12, 1.32] | 0.28 [0.07, 0.55] | -0.31 [-1.11, 0.27] | 0.5061 |
| availability_calls | 120 | 7.33 [4.95, 10.47] | 9.12 [6.16, 13.19] | 1.79 [-1.39, 5.54] | 0.0610 |
| ladder_fire_turns | 120 | 0.78 [0.53, 1.08] | 1.52 [1.27, 1.82] | 0.73 [0.39, 1.09] | 0.0000*** |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 120 | 62.5% [53.3%, 70.8%] | 65.8% [56.7%, 74.2%] | 3.3% [-3.3%, 10.0%] | 6/10 | 0.4545 |
| faithful | 120 | 95.0% [90.8%, 98.3%] | 94.2% [90.0%, 98.3%] | -0.8% [-6.7%, 5.0%] | 7/6 | 1.0000 |
| refusal_accepted | 120 | 16.7% [10.0%, 23.3%] | 16.7% [10.0%, 23.3%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 120 | 4.60 [4.45, 4.74] | 4.37 [4.20, 4.53] | -0.23 [-0.42, -0.05] | 0.0204* |
| negotiation_effectiveness | 86 | 3.30 [3.06, 3.55] | 3.72 [3.45, 3.99] | 0.42 [0.09, 0.74] | 0.0130* |
| conversational_efficiency | 120 | 3.73 [3.51, 3.94] | 3.72 [3.49, 3.92] | -0.01 [-0.26, 0.24] | 0.9702 |
| customer_experience | 100 | 3.33 [3.06, 3.59] | 3.66 [3.39, 3.91] | 0.33 [0.06, 0.61] | 0.0192* |
| recovery_quality | 57 | 3.46 [3.16, 3.75] | 3.75 [3.46, 4.05] | 0.30 [-0.09, 0.67] | 0.1693 |

## Tier 1 (n=10)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 10 | 5.20 [2.70, 8.20] | 3.90 [1.80, 6.90] | -1.30 [-3.40, 0.00] | 0.1198 |
| efficiency_ratio | 10 | 5.10 [1.40, 10.20] | 3.40 [1.20, 6.60] | -1.70 [-5.60, 1.80] | 0.3613 |
| simulated_latency_ms | 10 | 6004.89 [2584.76, 10417.76] | 4747.42 [1945.67, 8715.78] | -1257.47 [-4641.11, 1717.09] | 0.3081 |
| parse_accuracy | 10 | 0.50 [0.25, 0.75] | 0.50 [0.30, 0.70] | 0.00 [-0.20, 0.25] | 0.7855 |
| dead_end_turns | 10 | 2.50 [0.00, 6.00] | 1.30 [0.00, 3.20] | -1.20 [-4.20, 1.20] | 0.5862 |
| unsupported_facts | 10 | 1.30 [0.00, 3.90] | 0.00 [0.00, 0.00] | -1.30 [-3.90, 0.00] | 1.0000 |
| availability_calls | 10 | 5.10 [1.40, 10.20] | 3.40 [1.20, 6.60] | -1.70 [-5.60, 1.80] | 0.3613 |
| ladder_fire_turns | 10 | 1.40 [0.00, 3.70] | 0.50 [0.10, 1.00] | -0.90 [-2.90, 0.30] | 0.5716 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 10 | 70.0% [40.0%, 100.0%] | 80.0% [50.0%, 100.0%] | 10.0% [0.0%, 30.0%] | 0/1 | 1.0000 |
| faithful | 10 | 90.0% [70.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 10.0% [0.0%, 30.0%] | 0/1 | 1.0000 |
| refusal_accepted | 10 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 10 | 4.70 [4.10, 5.00] | 4.50 [3.70, 5.00] | -0.20 [-0.50, 0.00] | 0.3458 |
| negotiation_effectiveness | 4 | 2.50 [1.50, 3.50] | 3.50 [2.00, 5.00] | 1.00 [-0.50, 2.50] | 0.3447 |
| conversational_efficiency | 10 | 3.80 [2.80, 4.70] | 4.40 [3.50, 5.00] | 0.60 [0.00, 1.30] | 0.1814 |
| customer_experience | 10 | 3.80 [2.80, 4.70] | 4.10 [3.20, 5.00] | 0.30 [-0.20, 1.00] | 0.5862 |
| recovery_quality | 0 | — | — | — | — |

## Tier 2 (n=10)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 10 | 7.50 [4.80, 10.20] | 5.20 [2.50, 8.10] | -2.30 [-5.90, 1.40] | 0.1241 |
| efficiency_ratio | 10 | 6.30 [3.80, 9.10] | 4.00 [2.00, 7.10] | -2.30 [-6.30, 2.10] | 0.2710 |
| simulated_latency_ms | 10 | 7846.42 [4993.41, 11535.97] | 5084.92 [2857.78, 8303.84] | -2761.51 [-7657.93, 1778.05] | 0.1536 |
| parse_accuracy | 10 | 0.50 [0.20, 0.75] | 0.70 [0.45, 0.95] | 0.20 [0.00, 0.45] | 0.1736 |
| dead_end_turns | 10 | 5.30 [2.50, 8.30] | 0.90 [0.00, 2.30] | -4.40 [-7.80, -1.00] | 0.0311* |
| unsupported_facts | 10 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 10 | 6.30 [3.80, 9.10] | 4.00 [2.00, 7.10] | -2.30 [-6.30, 2.10] | 0.2710 |
| ladder_fire_turns | 10 | 0.40 [0.10, 0.70] | 1.40 [0.70, 2.50] | 1.00 [0.20, 2.00] | 0.0418* |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 10 | 50.0% [20.0%, 80.0%] | 70.0% [40.0%, 100.0%] | 20.0% [-20.0%, 60.0%] | 1/3 | 0.6250 |
| faithful | 10 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 10 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 10 | 4.90 [4.70, 5.00] | 4.30 [3.80, 4.70] | -0.60 [-1.10, -0.20] | 0.0947 |
| negotiation_effectiveness | 9 | 3.56 [2.67, 4.44] | 4.00 [3.00, 5.00] | 0.44 [-0.67, 1.56] | 0.5708 |
| conversational_efficiency | 10 | 3.60 [2.70, 4.40] | 4.10 [3.40, 4.70] | 0.50 [-0.60, 1.60] | 0.4568 |
| customer_experience | 10 | 3.50 [2.60, 4.40] | 4.00 [3.30, 4.70] | 0.50 [-0.60, 1.60] | 0.4568 |
| recovery_quality | 0 | — | — | — | — |

## Tier 3 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 7.10 [5.60, 8.75] | 6.40 [4.65, 8.20] | -0.70 [-1.85, 0.50] | 0.0463* |
| efficiency_ratio | 20 | 8.65 [2.55, 17.27] | 7.15 [3.08, 13.62] | -1.50 [-7.93, 2.35] | 0.3099 |
| simulated_latency_ms | 20 | 27937.59 [5890.54, 59962.20] | 22255.00 [8086.96, 46219.85] | -5682.59 [-30165.40, 8640.93] | 0.1403 |
| parse_accuracy | 20 | 0.42 [0.28, 0.57] | 0.45 [0.28, 0.62] | 0.03 [-0.05, 0.12] | 0.7728 |
| dead_end_turns | 20 | 3.95 [2.40, 5.70] | 2.40 [1.00, 3.95] | -1.55 [-2.80, -0.40] | 0.0149* |
| unsupported_facts | 20 | 0.00 [0.00, 0.00] | 0.15 [0.00, 0.45] | 0.15 [0.00, 0.45] | 1.0000 |
| availability_calls | 20 | 17.30 [5.10, 34.55] | 14.30 [6.15, 27.25] | -3.00 [-15.85, 4.70] | 0.3099 |
| ladder_fire_turns | 20 | 1.10 [0.30, 2.10] | 1.70 [1.30, 2.15] | 0.60 [-0.25, 1.35] | 0.0810 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 65.0% [45.0%, 85.0%] | 65.0% [45.0%, 85.0%] | 0.0% [-15.0%, 15.0%] | 1/1 | 1.0000 |
| faithful | 20 | 100.0% [100.0%, 100.0%] | 95.0% [85.0%, 100.0%] | -5.0% [-15.0%, 0.0%] | 1/0 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.85 [4.55, 5.00] | 4.75 [4.45, 5.00] | -0.10 [-0.50, 0.30] | 0.8539 |
| negotiation_effectiveness | 20 | 3.60 [3.10, 4.10] | 4.10 [3.50, 4.65] | 0.50 [-0.05, 1.15] | 0.1617 |
| conversational_efficiency | 20 | 4.10 [3.65, 4.55] | 4.10 [3.55, 4.65] | 0.00 [-0.35, 0.45] | 0.8211 |
| customer_experience | 20 | 3.55 [3.05, 4.00] | 4.05 [3.45, 4.60] | 0.50 [0.10, 0.95] | 0.0331* |
| recovery_quality | 20 | 3.90 [3.40, 4.35] | 4.15 [3.60, 4.65] | 0.25 [-0.25, 0.85] | 0.5060 |

## Tier 4 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 6.40 [5.15, 7.70] | 4.25 [3.50, 5.25] | -2.15 [-3.45, -0.80] | 0.0056** |
| efficiency_ratio | 19 | 2.95 [2.11, 3.84] | 3.82 [2.11, 6.76] | 0.87 [-1.00, 3.87] | 0.8121 |
| simulated_latency_ms | 20 | 6555.23 [4956.25, 8334.27] | 9417.88 [5426.05, 15814.14] | 2862.64 [-1252.68, 9222.67] | 0.6677 |
| parse_accuracy | 19 | 0.34 [0.18, 0.50] | 0.37 [0.16, 0.58] | 0.03 [-0.11, 0.16] | 0.7768 |
| dead_end_turns | 20 | 3.35 [2.10, 4.70] | 1.05 [0.25, 2.35] | -2.30 [-3.95, -0.60] | 0.0088** |
| unsupported_facts | 20 | 1.00 [0.00, 2.25] | 0.50 [0.00, 1.40] | -0.50 [-1.95, 0.90] | 0.5896 |
| availability_calls | 20 | 5.70 [4.05, 7.50] | 7.30 [4.00, 12.75] | 1.60 [-1.95, 7.10] | 0.7593 |
| ladder_fire_turns | 20 | 0.80 [0.35, 1.30] | 1.65 [1.00, 2.65] | 0.85 [0.10, 1.90] | 0.0664 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 90.0% [75.0%, 100.0%] | 95.0% [85.0%, 100.0%] | 5.0% [-10.0%, 20.0%] | 1/2 | 1.0000 |
| faithful | 20 | 85.0% [70.0%, 100.0%] | 90.0% [75.0%, 100.0%] | 5.0% [-15.0%, 25.0%] | 2/3 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.55 [4.25, 4.80] | 4.50 [4.15, 4.80] | -0.05 [-0.45, 0.35] | 0.8302 |
| negotiation_effectiveness | 17 | 3.47 [3.00, 3.94] | 4.18 [3.82, 4.53] | 0.71 [0.00, 1.41] | 0.0871 |
| conversational_efficiency | 20 | 3.80 [3.40, 4.20] | 4.25 [3.80, 4.65] | 0.45 [-0.05, 0.95] | 0.1082 |
| customer_experience | 20 | 3.50 [3.00, 3.95] | 4.15 [3.70, 4.55] | 0.65 [0.05, 1.30] | 0.0719 |
| recovery_quality | 17 | 3.53 [3.00, 4.06] | 4.18 [3.71, 4.59] | 0.65 [-0.12, 1.41] | 0.1178 |

## Tier 5 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 8.70 [7.45, 9.90] | 6.50 [5.45, 7.70] | -2.20 [-3.65, -0.60] | 0.0212* |
| efficiency_ratio | 20 | 3.03 [2.32, 3.98] | 5.87 [2.45, 11.88] | 2.83 [-0.83, 8.90] | 0.9058 |
| simulated_latency_ms | 20 | 10430.37 [8294.18, 13107.74] | 19558.41 [8902.16, 37111.85] | 9128.04 [-2171.49, 26766.51] | 0.9553 |
| parse_accuracy | 20 | 0.42 [0.25, 0.62] | 0.45 [0.28, 0.65] | 0.03 [-0.10, 0.15] | 0.7768 |
| dead_end_turns | 20 | 4.55 [3.05, 6.25] | 0.95 [0.20, 1.90] | -3.60 [-5.60, -1.55] | 0.0037** |
| unsupported_facts | 20 | 0.00 [0.00, 0.00] | 0.20 [0.00, 0.50] | 0.20 [0.00, 0.50] | 0.3458 |
| availability_calls | 20 | 9.10 [6.95, 11.95] | 17.60 [7.35, 35.65] | 8.50 [-2.50, 26.70] | 0.9244 |
| ladder_fire_turns | 20 | 0.95 [0.45, 1.60] | 2.40 [1.80, 3.20] | 1.45 [0.50, 2.45] | 0.0165* |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 80.0% [60.0%, 95.0%] | 85.0% [70.0%, 100.0%] | 5.0% [-15.0%, 25.0%] | 2/3 | 1.0000 |
| faithful | 20 | 100.0% [100.0%, 100.0%] | 90.0% [75.0%, 100.0%] | -10.0% [-25.0%, 0.0%] | 2/0 | 0.5000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.05 [3.50, 4.55] | 3.70 [3.35, 4.05] | -0.35 [-0.90, 0.20] | 0.3241 |
| negotiation_effectiveness | 20 | 2.75 [2.35, 3.15] | 3.05 [2.65, 3.45] | 0.30 [-0.25, 0.80] | 0.3155 |
| conversational_efficiency | 20 | 2.95 [2.50, 3.40] | 2.75 [2.45, 3.05] | -0.20 [-0.80, 0.40] | 0.5393 |
| customer_experience | 20 | 2.25 [1.85, 2.65] | 2.50 [2.15, 2.85] | 0.25 [-0.25, 0.70] | 0.3873 |
| recovery_quality | 20 | 2.95 [2.50, 3.40] | 3.00 [2.60, 3.40] | 0.05 [-0.60, 0.70] | 0.9578 |

## Tier 6 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 5.95 [4.50, 7.50] | 6.20 [4.55, 7.95] | 0.25 [-1.10, 1.85] | 0.8881 |
| efficiency_ratio | 20 | 2.73 [1.85, 3.67] | 3.83 [2.62, 5.17] | 1.10 [0.30, 1.95] | 0.0276* |
| simulated_latency_ms | 20 | 7295.74 [5143.10, 9692.62] | 9874.26 [7021.01, 12956.94] | 2578.51 [809.64, 4397.42] | 0.0458* |
| parse_accuracy | 20 | 0.38 [0.20, 0.55] | 0.40 [0.20, 0.60] | 0.03 [-0.17, 0.22] | 0.8514 |
| dead_end_turns | 20 | 2.55 [1.30, 4.10] | 1.65 [0.55, 3.00] | -0.90 [-1.95, 0.15] | 0.1289 |
| unsupported_facts | 20 | 1.85 [0.00, 5.35] | 0.80 [0.00, 2.20] | -1.05 [-4.95, 1.60] | 1.0000 |
| availability_calls | 20 | 5.45 [3.70, 7.35] | 7.65 [5.25, 10.35] | 2.20 [0.60, 3.90] | 0.0276* |
| ladder_fire_turns | 20 | 0.90 [0.60, 1.20] | 1.70 [1.10, 2.50] | 0.80 [0.25, 1.50] | 0.0165* |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 80.0% [60.0%, 95.0%] | 75.0% [55.0%, 90.0%] | -5.0% [-15.0%, 0.0%] | 1/0 | 1.0000 |
| faithful | 20 | 90.0% [75.0%, 100.0%] | 90.0% [75.0%, 100.0%] | 0.0% [-20.0%, 20.0%] | 2/2 | 1.0000 |
| refusal_accepted | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.50 [4.25, 4.75] | 4.35 [3.85, 4.75] | -0.15 [-0.65, 0.30] | 0.6244 |
| negotiation_effectiveness | 16 | 3.50 [2.94, 4.06] | 3.50 [2.75, 4.19] | 0.00 [-1.00, 0.94] | 0.8735 |
| conversational_efficiency | 20 | 3.80 [3.15, 4.40] | 3.60 [2.95, 4.25] | -0.20 [-1.10, 0.65] | 0.7040 |
| customer_experience | 20 | 3.70 [3.10, 4.25] | 3.55 [2.90, 4.20] | -0.15 [-0.95, 0.65] | 0.7500 |
| recovery_quality | 0 | — | — | — | — |

## Tier 7 (n=20)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 20 | 3.70 [3.25, 4.15] | 4.70 [4.10, 5.40] | 1.00 [0.30, 1.70] | 0.0196* |
| efficiency_ratio | 0 | — | — | — | — |
| simulated_latency_ms | 20 | 1289.97 [707.66, 1919.48] | 6222.22 [3636.93, 9115.06] | 4932.25 [2654.57, 7572.49] | 0.0021** |
| parse_accuracy | 0 | — | — | — | — |
| dead_end_turns | 20 | 0.60 [0.20, 1.10] | 0.50 [0.20, 0.85] | -0.10 [-0.30, 0.10] | 0.4237 |
| unsupported_facts | 20 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 20 | 0.70 [0.20, 1.30] | 4.15 [2.20, 6.45] | 3.45 [1.80, 5.45] | 0.0037** |
| ladder_fire_turns | 20 | 0.05 [0.00, 0.15] | 0.70 [0.40, 1.00] | 0.65 [0.35, 0.95] | 0.0021** |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 20 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 20 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 20 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 20 | 4.85 [4.60, 5.00] | 4.50 [4.05, 4.85] | -0.35 [-0.85, 0.10] | 0.2217 |
| negotiation_effectiveness | 0 | — | — | — | — |
| conversational_efficiency | 20 | 4.00 [3.60, 4.35] | 3.35 [3.00, 3.70] | -0.65 [-1.05, -0.25] | 0.0102* |
| customer_experience | 0 | — | — | — | — |
| recovery_quality | 0 | — | — | — | — |
