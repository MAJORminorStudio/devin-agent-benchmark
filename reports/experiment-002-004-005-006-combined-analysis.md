# Combined capability-frontier analysis: E002, E004, E005, and E006

> Primary comparison across Moderate, HARD, and VERY-HARD tiers. E003 is supplemental and excluded from the primary denominator.

## Primary results

| Tier | Medium | Max | Paired outcomes |
|---|:---:|:---:|---|
| Moderate (E002 historical + E004 novel calibrated) | 10/10 | 8/10 | 8 both success, 2 Medium-only |
| HARD (E005) | 7/10 | 6/10 | 5 both success, 2 Medium-only, 1 Max-only, 2 both fail |
| VERY-HARD (E006) | 7/10 | 9/10 | 7 both success, 2 Max-only, 1 both fail |
| **Cumulative primary (30 pairs)** | **24/30** | **23/30** | **20 both success, 4 Medium-only, 3 Max-only, 3 both fail** |

The tier series is not monotonic for either condition. Medium falls from 10/10 Moderate to 7/10 HARD and remains 7/10 VERY-HARD. Max falls from 8/10 Moderate to 6/10 HARD, then rises to 9/10 VERY-HARD. E006 is therefore a capability-frontier tier by its hidden-contract and withheld-case behavior, not by a claim that every aggregate is harder than E005.

## Resource profile

| Tier | Medium wall / steps / tools | Max wall / steps / tools |
|---|---|---|
| Moderate (E002 + E004) | mean wall 222.9 s; steps 28.0; tools 23.0 | mean wall 429.5 s; steps 36.2; tools 43.7 |
| HARD (E005) | mean wall 186.1 s; steps 28.0; tools 29.3 | mean wall 438.4 s; steps 38.1; tools 39.8 |
| VERY-HARD (E006) | mean wall 440.7 s; steps 22.3; tools 20.8 | mean wall 719.0 s; steps 36.0; tools 36.9 |

E006 Max used more resources than E006 Medium on every captured aggregate: 1.63× mean wall, 1.61× steps, 1.77× tools, 3.92× prompt tokens, 5.07× completion tokens, and 4.27× cached tokens. The E006 sample also shows that resource scale is not a guarantee: H04 failed under both conditions.

## What E006 adds

- It introduces four newly constructed withheld cases alongside five historical public cases, making provenance a visible part of interpretation.
- Historical K cases passed 5/5 under both conditions; withheld H cases passed 2/5 Medium and 4/5 Max.
- Max had two unique successes and no Medium-only success in E006, positive descriptive evidence of unique frontier value in this sample.
- Failures were concentrated in hidden behavioral contracts: cycle-error typing (H01-M), oversized-frame resynchronization (H03-M), and stable dispatch membership (H04-M/X).

## Cautions and scope

This is a fixed, balanced, paired execution, not a randomized estimate of general model performance. The runs use the frozen E006 image, exact order, single-run-per-cell protocol, and evaluator-after-session-close rule. Results are not causal proof, and the provenance split means the K and H subsets should not be collapsed without qualification.

See the [E006 report](experiment-006-results.md), [E006 summary](../results/experiment-006-summary.json), [E006 ledger](../results/experiment-006-ledger.json), and [sanitized E006 artifacts](../artifacts/experiment-006/). E002, E004, and E005 source summaries remain unchanged.
