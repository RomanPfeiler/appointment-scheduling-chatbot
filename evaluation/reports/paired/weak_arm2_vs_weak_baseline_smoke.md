# Paired comparison — `20260610_193716__weak_nlp_arm2__99324a4__smoke` vs `20260610_183456__weak_baseline__a368480__smoke`

**Pairing:** 14 valid pairs out of 14 matched scenario-runs (excluded 0 pairs where either side had `termination=error` or missing derived metrics). Baseline-only keys: 0, candidate-only: 0.

## Overall (all tiers)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 14 | 8.57 [6.57, 10.36] | 9.36 [7.64, 10.93] | 0.79 [-1.00, 2.71] | 0.6704 |
| efficiency_ratio | 12 | 3.19 [1.94, 4.82] | 4.81 [2.88, 6.97] | 1.61 [-0.08, 3.63] | 0.2131 |
| simulated_latency_ms | 14 | 18269.52 [4871.45, 38413.19] | 8589.62 [5309.08, 12586.93] | -9679.90 [-26192.30, 2310.42] | 0.8017 |
| parse_accuracy | 12 | 0.38 [0.12, 0.62] | 0.62 [0.38, 0.83] | 0.25 [-0.04, 0.58] | 0.1300 |
| dead_end_turns | 14 | 3.43 [1.86, 5.29] | 4.79 [2.86, 6.79] | 1.36 [-0.93, 3.71] | 0.3561 |
| unsupported_facts | 14 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 14 | 4.64 [2.79, 6.64] | 6.29 [4.21, 8.21] | 1.64 [-0.29, 3.71] | 0.2341 |
| ladder_fire_turns | 14 | 0.21 [0.00, 0.57] | 0.21 [0.00, 0.57] | 0.00 [-0.43, 0.43] | 0.8527 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 14 | 50.0% [21.4%, 78.6%] | 35.7% [14.3%, 57.1%] | -14.3% [-35.7%, 0.0%] | 2/0 | 0.5000 |
| faithful | 14 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 14 | 14.3% [0.0%, 35.7%] | 14.3% [0.0%, 35.7%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 14 | 3.86 [3.43, 4.29] | 3.64 [2.93, 4.29] | -0.21 [-1.00, 0.57] | 0.6493 |
| negotiation_effectiveness | 11 | 2.64 [2.18, 3.18] | 1.91 [1.73, 2.00] | -0.73 [-1.27, -0.18] | 0.0719 |
| conversational_efficiency | 14 | 2.64 [2.14, 3.21] | 1.86 [1.50, 2.21] | -0.79 [-1.50, -0.07] | 0.0621 |
| customer_experience | 12 | 2.50 [2.00, 3.08] | 1.75 [1.42, 2.08] | -0.75 [-1.42, -0.17] | 0.0578 |
| recovery_quality | 6 | 2.33 [2.00, 3.00] | 1.67 [1.33, 2.00] | -0.67 [-1.33, -0.17] | 0.1736 |

## Tier 1 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 7.50 [3.00, 12.00] | 8.50 [5.00, 12.00] | 1.00 [0.00, 2.00] | 1.0000 |
| efficiency_ratio | 2 | 6.00 [1.00, 11.00] | 6.00 [1.00, 11.00] | 0.00 [0.00, 0.00] | 1.0000 |
| simulated_latency_ms | 2 | 33048.90 [2286.82, 63810.97] | 6099.91 [1785.75, 10414.08] | -26948.98 [-53396.89, -501.08] | 0.3711 |
| parse_accuracy | 2 | 0.50 [0.00, 1.00] | 1.00 [1.00, 1.00] | 0.50 [0.00, 1.00] | 1.0000 |
| dead_end_turns | 2 | 5.50 [0.00, 11.00] | 2.00 [0.00, 4.00] | -3.50 [-7.00, 0.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 6.00 [1.00, 11.00] | 6.00 [1.00, 11.00] | 0.00 [0.00, 0.00] | 1.0000 |
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
| temporal_understanding | 2 | 4.50 [4.00, 5.00] | 4.50 [4.00, 5.00] | 0.00 [-1.00, 1.00] | 0.6374 |
| negotiation_effectiveness | 1 | 2.00 [2.00, 2.00] | 2.00 [2.00, 2.00] | 0.00 [0.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 3.50 [2.00, 5.00] | 2.00 [2.00, 2.00] | -1.50 [-3.00, 0.00] | 1.0000 |
| customer_experience | 2 | 3.50 [2.00, 5.00] | 2.00 [2.00, 2.00] | -1.50 [-3.00, 0.00] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 2 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 7.50 [3.00, 12.00] | 12.00 [12.00, 12.00] | 4.50 [0.00, 9.00] | 1.0000 |
| efficiency_ratio | 2 | 2.50 [1.00, 4.00] | 11.00 [11.00, 11.00] | 8.50 [7.00, 10.00] | 0.3711 |
| simulated_latency_ms | 2 | 4161.43 [3512.29, 4810.56] | 10373.73 [10318.24, 10429.23] | 6212.31 [5618.67, 6805.95] | 0.3711 |
| parse_accuracy | 2 | 0.50 [0.00, 1.00] | 0.75 [0.50, 1.00] | 0.25 [-0.50, 1.00] | 1.0000 |
| dead_end_turns | 2 | 2.00 [0.00, 4.00] | 11.00 [11.00, 11.00] | 9.00 [7.00, 11.00] | 0.3711 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 2.50 [1.00, 4.00] | 11.00 [11.00, 11.00] | 8.50 [7.00, 10.00] | 0.3711 |
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
| temporal_understanding | 2 | 3.50 [3.00, 4.00] | 5.00 [5.00, 5.00] | 1.50 [1.00, 2.00] | 0.3711 |
| negotiation_effectiveness | 2 | 3.00 [2.00, 4.00] | 2.00 [2.00, 2.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 3.00 [2.00, 4.00] | 1.50 [1.00, 2.00] | -1.50 [-2.00, -1.00] | 0.3711 |
| customer_experience | 2 | 3.00 [2.00, 4.00] | 2.00 [2.00, 2.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 3 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 9.50 [7.00, 12.00] | 8.50 [7.00, 10.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| efficiency_ratio | 2 | 1.75 [1.00, 2.50] | 3.00 [2.00, 4.00] | 1.25 [-0.50, 3.00] | 1.0000 |
| simulated_latency_ms | 2 | 4532.58 [3969.14, 5096.02] | 6327.20 [4393.05, 8261.34] | 1794.62 [-702.97, 4292.20] | 1.0000 |
| parse_accuracy | 2 | 0.75 [0.50, 1.00] | 0.75 [0.50, 1.00] | 0.00 [0.00, 0.00] | 1.0000 |
| dead_end_turns | 2 | 2.00 [1.00, 3.00] | 3.50 [3.00, 4.00] | 1.50 [0.00, 3.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 3.50 [2.00, 5.00] | 6.00 [4.00, 8.00] | 2.50 [-1.00, 6.00] | 1.0000 |
| ladder_fire_turns | 2 | 0.00 [0.00, 0.00] | 1.00 [0.00, 2.00] | 1.00 [0.00, 2.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 3.00 [3.00, 3.00] | 3.00 [3.00, 3.00] | 0.00 [0.00, 0.00] | 1.0000 |
| negotiation_effectiveness | 2 | 3.00 [2.00, 4.00] | 2.00 [2.00, 2.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 2.00 [2.00, 2.00] | 2.00 [2.00, 2.00] | 0.00 [0.00, 0.00] | 1.0000 |
| customer_experience | 2 | 2.50 [2.00, 3.00] | 2.00 [2.00, 2.00] | -0.50 [-1.00, 0.00] | 1.0000 |
| recovery_quality | 2 | 3.00 [2.00, 4.00] | 2.00 [2.00, 2.00] | -1.00 [-2.00, 0.00] | 1.0000 |

## Tier 4 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 11.00 [10.00, 12.00] | 12.00 [12.00, 12.00] | 1.00 [0.00, 2.00] | 1.0000 |
| efficiency_ratio | 2 | 3.75 [3.50, 4.00] | 3.25 [3.00, 3.50] | -0.50 [-1.00, 0.00] | 1.0000 |
| simulated_latency_ms | 2 | 13662.74 [7061.44, 20264.03] | 6818.82 [5831.07, 7806.58] | -6843.91 [-14432.96, 745.14] | 1.0000 |
| parse_accuracy | 2 | 0.00 [0.00, 0.00] | 0.50 [0.00, 1.00] | 0.50 [0.00, 1.00] | 1.0000 |
| dead_end_turns | 2 | 6.00 [5.00, 7.00] | 5.50 [4.00, 7.00] | -0.50 [-3.00, 2.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 7.50 [7.00, 8.00] | 6.50 [6.00, 7.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| ladder_fire_turns | 2 | 1.00 [0.00, 2.00] | 0.50 [0.00, 1.00] | -0.50 [-2.00, 1.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 50.0% [0.0%, 100.0%] | 0.0% [0.0%, 0.0%] | -50.0% [-100.0%, 0.0%] | 1/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 4.00 [3.00, 5.00] | 2.50 [2.00, 3.00] | -1.50 [-2.00, -1.00] | 0.3711 |
| negotiation_effectiveness | 2 | 2.50 [2.00, 3.00] | 1.50 [1.00, 2.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 2.50 [2.00, 3.00] | 1.00 [1.00, 1.00] | -1.50 [-2.00, -1.00] | 0.3711 |
| customer_experience | 2 | 2.00 [2.00, 2.00] | 1.00 [1.00, 1.00] | -1.00 [-1.00, -1.00] | 0.3458 |
| recovery_quality | 2 | 2.00 [2.00, 2.00] | 1.00 [1.00, 1.00] | -1.00 [-1.00, -1.00] | 0.3458 |

## Tier 5 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 12.00 [12.00, 12.00] | 12.00 [12.00, 12.00] | 0.00 [0.00, 0.00] | 1.0000 |
| efficiency_ratio | 2 | 2.67 [1.67, 3.67] | 3.33 [3.00, 3.67] | 0.67 [-0.67, 2.00] | 1.0000 |
| simulated_latency_ms | 2 | 63703.23 [5709.76, 121696.69] | 23398.79 [19175.45, 27622.12] | -40304.44 [-94074.57, 13465.69] | 1.0000 |
| parse_accuracy | 2 | 0.50 [0.00, 1.00] | 0.75 [0.50, 1.00] | 0.25 [-0.50, 1.00] | 1.0000 |
| dead_end_turns | 2 | 5.00 [3.00, 7.00] | 9.00 [8.00, 10.00] | 4.00 [1.00, 7.00] | 0.3711 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 8.00 [5.00, 11.00] | 10.00 [9.00, 11.00] | 2.00 [-2.00, 6.00] | 1.0000 |
| ladder_fire_turns | 2 | 0.50 [0.00, 1.00] | 0.00 [0.00, 0.00] | -0.50 [-1.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 4.00 [3.00, 5.00] | 4.00 [3.00, 5.00] | 0.00 [-2.00, 2.00] | 0.6374 |
| negotiation_effectiveness | 2 | 3.00 [2.00, 4.00] | 2.00 [2.00, 2.00] | -1.00 [-2.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 1.50 [1.00, 2.00] | 2.50 [2.00, 3.00] | 1.00 [1.00, 1.00] | 0.3458 |
| customer_experience | 2 | 1.50 [1.00, 2.00] | 1.50 [1.00, 2.00] | 0.00 [0.00, 0.00] | 1.0000 |
| recovery_quality | 2 | 2.00 [2.00, 2.00] | 2.00 [2.00, 2.00] | 0.00 [0.00, 0.00] | 1.0000 |

## Tier 6 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 6.00 [3.00, 9.00] | 8.50 [6.00, 11.00] | 2.50 [-3.00, 8.00] | 1.0000 |
| efficiency_ratio | 2 | 2.50 [1.00, 4.00] | 2.25 [2.00, 2.50] | -0.25 [-1.50, 1.00] | 1.0000 |
| simulated_latency_ms | 2 | 7511.05 [6127.86, 8894.23] | 6467.73 [5205.52, 7729.93] | -1043.32 [-3688.72, 1602.07] | 1.0000 |
| parse_accuracy | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| dead_end_turns | 2 | 3.50 [1.00, 6.00] | 2.50 [2.00, 3.00] | -1.00 [-3.00, 1.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 5.00 [2.00, 8.00] | 4.50 [4.00, 5.00] | -0.50 [-3.00, 2.00] | 1.0000 |
| ladder_fire_turns | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |

### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)

| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |
|---|---:|---:|---:|---:|---:|---:|
| booked | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| faithful | 2 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |
| refusal_accepted | 2 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 0/0 | 1.0000 |

### Judge dimensions (Wilcoxon signed-rank on per-record means)

| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| temporal_understanding | 2 | 3.50 [3.00, 4.00] | 3.50 [2.00, 5.00] | 0.00 [-1.00, 1.00] | 0.6374 |
| negotiation_effectiveness | 2 | 2.00 [2.00, 2.00] | 2.00 [2.00, 2.00] | 0.00 [0.00, 0.00] | 1.0000 |
| conversational_efficiency | 2 | 3.50 [3.00, 4.00] | 2.00 [1.00, 3.00] | -1.50 [-3.00, 0.00] | 1.0000 |
| customer_experience | 2 | 2.50 [2.00, 3.00] | 2.00 [1.00, 3.00] | -0.50 [-2.00, 1.00] | 1.0000 |
| recovery_quality | 0 | — | — | — | — |

## Tier 7 (n=2)

### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)

| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |
|---|---:|---:|---:|---:|---:|
| turn_count | 2 | 6.50 [5.00, 8.00] | 4.00 [3.00, 5.00] | -2.50 [-5.00, 0.00] | 1.0000 |
| efficiency_ratio | 0 | — | — | — | — |
| simulated_latency_ms | 2 | 1266.73 [1162.02, 1371.45] | 641.16 [430.30, 852.02] | -625.57 [-941.15, -310.00] | 0.3711 |
| parse_accuracy | 0 | — | — | — | — |
| dead_end_turns | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| unsupported_facts | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
| availability_calls | 2 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.0000 |
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
| conversational_efficiency | 2 | 2.50 [2.00, 3.00] | 2.00 [1.00, 3.00] | -0.50 [-2.00, 1.00] | 1.0000 |
| customer_experience | 0 | — | — | — | — |
| recovery_quality | 0 | — | — | — | — |
