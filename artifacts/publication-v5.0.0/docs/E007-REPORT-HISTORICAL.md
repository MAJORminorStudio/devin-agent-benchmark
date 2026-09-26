> **Historical report:** This preserves E007 as first reported. Its evaluator scores (16/30, 18/30, 18/30) are not silently replaced. See `../CORRECTION.md` and `../PUBLICATION.md` for the subsequent E008 clean recheck.

> The frozen planning documents also retain a pre-run catalog-based expectation; that was not a billing measurement. Actual monetary cost is unknown.

# E007 Report

**Status: all 90 primary cells executed and evaluated.** E007 is an independent replication of SWE-2 effort-level behavior with High added; it is not an old-Devin-versus-SWE-2 comparison.

## Execution and provenance

Preserved E002–E006 evidence verified SWE-2 Medium and Max as the original conditions. Current execution used Devin CLI 3000.10.21, `--model swe-2-medium`, `--model swe-2-high`, and `--model swe-2-max`; the authenticated in-container catalog showed all three selectable and labeled Free. All 90 intended cells have evaluator results. There were no container errors and no substantive human interventions. The evaluator ran serially after agent execution.

One E006 K05 High session export contains the full final 54-step session and was evaluated successfully after a Codex API reconnect interrupted the outer process before it wrote container timing/exit metadata. The record has a missing-wrapper flag; its outcome, model identity, steps, and token counts are preserved, while runtime, start/end timestamps, and wrapper return code remain null. This is a documented protocol deviation and is excluded from runtime summaries only.

## Primary results

| Effort | Solved | Exact 95% binomial CI |
|---|---:|---:|
| Medium | 16/30 (53.3%) | 34.3%–71.7% |
| High | 18/30 (60.0%) | 40.6%–77.3% |
| Max | 18/30 (60.0%) | 40.6%–77.3% |

| Difficulty | Medium | High | Max |
|---|---:|---:|---:|
| Moderate | 7/10 | 8/10 | 8/10 |
| Hard | 7/10 | 8/10 | 8/10 |
| Very-Hard | 2/10 | 2/10 | 2/10 |

## Replication

| Condition | Original | E007 | Both solve | Both fail | Original only | E007 only | Exact agreement |
|---|---:|---:|---:|---:|---:|---:|---:|
| Medium | 24/30 | 16/30 | 15 | 5 | 9 | 1 | 20/30 (66.7%) |
| Max | 23/30 | 18/30 | 15 | 4 | 8 | 3 | 19/30 (63.3%) |

E007 Medium and Max each underperformed the original aggregate totals. Case-level agreement is shown above and disaggregated by tier in E007-REPLICATION-ANALYSIS.md.

## Paired effort and statistics

| Pair | Both solve | First only | Second only | Both fail | Δ first−second | Exact McNemar p |
|---|---:|---:|---:|---:|---:|---:|
| Medium Vs High | 16 | 0 | 2 | 12 | -6.7% | 0.5000 |
| Medium Vs Max | 15 | 1 | 3 | 11 | -6.7% | 0.6250 |
| High Vs Max | 17 | 1 | 1 | 11 | +0.0% | 1.0000 |

Cochran Q=2.000 (df=2; asymptotic p=0.3679). Pairwise exact McNemar tests are shown in the table. Paired bootstrap confidence intervals for absolute differences and exact solve-rate intervals are in E007-RESULTS.json. Small n, especially per tier, limits precision.

## Efficiency and behavior

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

Mean/median resource summaries use observed values only, with the available n retained. Direct cost and billing were not returned by the session exports, so cost per task/success cannot be calculated. Steps before first edit are heuristic session-trace estimates. Eight requested charts are in `charts/`. Detailed outcome-transition trace comparisons are in E007-FAILURE-ANALYSIS.md.

## Interpretation

The preregistered nonuniform-effort hypothesis is not supported as an aggregate performance curve: Medium solved fewer cases than High and Max, while High and Max tied overall. Only four cases changed outcome across effort settings; 26 were stable. Moderate-tier details and case transitions should be read from machine-derived outputs. No causal account of effort is warranted from a single run per cell.

## Deviations and publication readiness

The protocol/provenance files record the initial pre-session authentication/proxy recovery, the evaluator path repair, and brief early evaluator overlap. The interrupted E006 K05 High wrapper record is the only scored cell with incomplete execution metadata. All 90 cells have evaluator output; no additional tasks or stochastic repeats were added. Raw session exports and private workspaces are preserved outside the repository.

The result is publication-ready as a transparently documented single-run replication with High added, subject to independent review of trace-derived telemetry and the explicitly missing wrapper timing record. Recompute from `E007-RUNS.jsonl` using the analysis script before reuse.
