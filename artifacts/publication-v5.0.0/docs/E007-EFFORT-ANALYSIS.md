# E007 Effort Analysis

## Success

| Effort | Overall |
|---|---:|
| Medium | 16/30 (53.3%; exact 95% CI 34.3%–71.7%) |
| High | 18/30 (60.0%; exact 95% CI 40.6%–77.3%) |
| Max | 18/30 (60.0%; exact 95% CI 40.6%–77.3%) |

| Difficulty | Medium | High | Max |
|---|---:|---:|---:|
| Moderate | 7/10 | 8/10 | 8/10 |
| Hard | 7/10 | 8/10 | 8/10 |
| Very-Hard | 2/10 | 2/10 | 2/10 |

## Paired comparisons

| Pair | Both solve | First only | Second only | Both fail | Δ first−second | Exact McNemar p |
|---|---:|---:|---:|---:|---:|---:|
| Medium Vs High | 16 | 0 | 2 | 12 | -6.7% | 0.5000 |
| Medium Vs Max | 15 | 1 | 3 | 11 | -6.7% | 0.6250 |
| High Vs Max | 17 | 1 | 1 | 11 | +0.0% | 1.0000 |

Exact two-sided McNemar p-values use the discordant pairs. Paired bootstrap 95% intervals for the absolute rate difference are in E007-RESULTS.json; solve-rate intervals use exact Clopper–Pearson intervals. Cochran Q across the three efforts: Q=2.000, df=2, asymptotic p=0.3679.

## Transitions

| Increasing effort | Failure → success | Success → failure |
|---|---|---|
| Medium → High | E002-C02, E005-K01 | none |
| High → Max | E004-N03 | E002-C04 |
| Medium → Max | E002-C02, E004-N03, E005-K01 | E002-C04 |


## Cases solved by only one effort

- **Medium only:** none
- **High only:** none
- **Max only:** E004-N03

## Efficiency

| Effort | Success | Mean min | Median min | Mean steps | Median steps | Mean input tokens | Mean output tokens | Mean total tokens | Direct cost | First edit step mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| Medium | 16/30 | 3.1 (n=30) | 2.0 | 24.5 | 16.5 | 413366 | 5109 | 418475 | unavailable | 14.0 (n=30) |
| High | 18/30 | 5.3 (n=29) | 3.9 | 33.6 | 20.5 | 1149640 | 14235 | 1163874 | unavailable | 18.3 (n=30) |
| Max | 18/30 | 8.7 (n=30) | 5.0 | 41.3 | 19.5 | 1828093 | 23405 | 1851498 | unavailable | 18.8 (n=30) |

**Successful runs only**

| Effort | Successful runs | Mean min | Median min | Mean steps | Median steps | Mean input tokens | Mean output tokens | Mean total tokens |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Medium | 16/30 | 3.0 (n=16) | 2.7 | 25.8 | 26.5 | 377944 | 3890 | 381834 |
| High | 18/30 | 5.9 (n=17) | 6.0 | 38.1 | 36.5 | 1230032 | 15026 | 1245058 |
| Max | 18/30 | 11.1 (n=18) | 6.7 | 51.4 | 38.5 | 2588455 | 28277 | 2616732 |


Ratios relative to Medium are in `E007-RESULTS.json`. Cochran Q by difficulty tier is also reported there. No run exposed direct billing or account-reported cost, so cost per attempt and per successful case are unavailable, not zero. One recovered E006 K05 High session lacks the wrapper timing record; it contributes to session-derived steps/tokens and outcome but not runtime summaries.

## Difficulty × effort

| Difficulty | Medium | High | Max |
|---|---:|---:|---:|
| Moderate | 7/10 | 8/10 | 8/10 |
| Hard | 7/10 | 8/10 | 8/10 |
| Very-Hard | 2/10 | 2/10 | 2/10 |

E007’s observed pattern does not match the parent study: Medium has fewer aggregate solves than both High and Max. Hard and very-hard tier samples are small and should be interpreted descriptively.
