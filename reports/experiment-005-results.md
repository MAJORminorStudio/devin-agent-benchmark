# Experiment 005 Results

## Outcome

Experiment 005 completed all 20 frozen runs: five historical/public BugsInPy defects and five newly constructed withheld defects, each paired across SWE-2 Medium and SWE-2 Max.

Medium solved **7/10 (70%)** and Max solved **6/10 (60%)**, for 13/20 complete behavioral repairs. The public suite passed on 19/20 runs, the held-out behavioral suite on 14/20, and the regression suite on 19/20. Every container completed normally; there were no retries, substantive interventions, evaluator-process errors, workspace leaks, or infrastructure incidents.

The paired outcomes were 5 both-success, 2 Medium-only, 1 Max-only, and 2 both-fail. The result is descriptive evidence for this 10-case HARD-tier sample, not a general or causal claim about reasoning effort.

## Frozen protocol and isolation

The freeze matched the control repository at commit `11bbf007d2d332e4108805f6e28bbdcb3e8bf2ac`; the freeze manifest SHA-256 is `4c948de5d65bc90ca327d8f7a729b6cc3df571bcde0fab7bf6e7d6bb0c8602c1`. The exact image was `devin-e002:3000.10.21@sha256:bb045374bc655c185cced99a6cb769a6695c88527fb432456eb8e0d6dd0e4bb6` on linux/arm64, using the `e002-internal` network and restricted proxy `http://egress-proxy:3128`. Each run used dangerous permission mode with effective Bypass, a read-only root, all capabilities dropped, no-new-privileges, 4 GiB memory, 4 CPUs, a 512-process limit, no Docker socket, no control-repository/evaluator/reference mounts, one read-only credential mount, sequential execution, zero retries, and a 5400-second maximum.

The evaluator ran only after each container closed. The only external pause was a user-requested controller pause after run 5; it did not alter an active Devin session, provide task assistance, or count as a substantive intervention. Reported wall time uses the container runner's start-to-close duration and excludes that pause.

## Complete 20-run ledger

| Run | Case | Provenance | Condition | TASK_SUCCESS | Public | Held-out | Regression | Wall s | Steps | Tools | Prompt tok | Completion tok | Patch | Churn |
|---:|---|---|---:|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | E005-K04-X | historical-public | X | 1 | pass | pass | pass | 723.560 | 69 | 67 | 80422 | 980 | +13/-0 | 2 |
| 2 | E005-K05-M | historical-public | M | 1 | pass | pass | pass | 146.705 | 22 | 18 | 20055 | 354 | +7/-6 | 2 |
| 3 | E005-K02-X | historical-public | X | 0 | pass | fail | pass | 571.750 | 56 | 54 | 68993 | 639 | +5/-0 | 1 |
| 4 | E005-K01-M | historical-public | M | 1 | pass | pass | pass | 771.697 | 81 | 132 | 129859 | 583 | +145/-14 | 4 |
| 5 | E005-H05-X | newly-constructed-withheld | X | 0 | pass | fail | pass | 235.559 | 17 | 19 | 22189 | 411 | +13/-5 | 3 |
| 6 | E005-K04-M | historical-public | M | 0 | fail | fail | pass | 145.060 | 32 | 26 | 26590 | 282 | +4/-0 | 2 |
| 7 | E005-H05-M | newly-constructed-withheld | M | 0 | pass | fail | pass | 81.553 | 14 | 7 | 14770 | 130 | +3/-1 | 2 |
| 8 | E005-H04-X | newly-constructed-withheld | X | 1 | pass | pass | pass | 113.596 | 16 | 16 | 18259 | 293 | +1/-1 | 1 |
| 9 | E005-H03-X | newly-constructed-withheld | X | 0 | pass | pass | fail | 226.066 | 18 | 16 | 25074 | 304 | +10/-4 | 2 |
| 10 | E005-K02-M | historical-public | M | 1 | pass | pass | pass | 238.310 | 54 | 49 | 37616 | 400 | +5/-1 | 2 |
| 11 | E005-H03-M | newly-constructed-withheld | M | 1 | pass | pass | pass | 90.428 | 14 | 10 | 15506 | 229 | +2/-4 | 2 |
| 12 | E005-K03-X | historical-public | X | 1 | pass | pass | pass | 569.543 | 45 | 46 | 57123 | 801 | +16/-2 | 2 |
| 13 | E005-H01-M | newly-constructed-withheld | M | 1 | pass | pass | pass | 81.594 | 13 | 12 | 16161 | 238 | +5/-8 | 2 |
| 14 | E005-H02-M | newly-constructed-withheld | M | 0 | pass | fail | pass | 74.668 | 13 | 10 | 15786 | 159 | +3/-0 | 1 |
| 15 | E005-H04-M | newly-constructed-withheld | M | 1 | pass | pass | pass | 81.612 | 14 | 12 | 16113 | 224 | +1/-1 | 1 |
| 16 | E005-H01-X | newly-constructed-withheld | X | 1 | pass | pass | pass | 171.703 | 16 | 18 | 21009 | 305 | +5/-8 | 2 |
| 17 | E005-H02-X | newly-constructed-withheld | X | 0 | pass | fail | pass | 408.733 | 17 | 16 | 31547 | 314 | +7/-1 | 1 |
| 18 | E005-K01-X | historical-public | X | 1 | pass | pass | pass | 953.018 | 81 | 101 | 134630 | 503 | +144/-15 | 4 |
| 19 | E005-K03-M | historical-public | M | 1 | pass | pass | pass | 148.895 | 23 | 17 | 26575 | 272 | +8/-0 | 1 |
| 20 | E005-K05-X | historical-public | X | 1 | pass | pass | pass | 410.320 | 46 | 45 | 39692 | 798 | +7/-6 | 2 |

The complete sanitized record-level machine-readable ledger is [`results/experiment-005-ledger.json`](../results/experiment-005-ledger.json). Per-run sanitized prompts, source patches, evaluator outcomes, timelines, summaries, metadata, and hashes are under [`artifacts/experiment-005/`](../artifacts/experiment-005/).

## Condition aggregates

All wall-time values below are container start-to-close seconds; token values are the captured prompt/completion/cache counters.

| Condition | Success | Wall total / mean / median s | Steps total / mean / median | Tools total / mean / median | Prompt tokens | Completion tokens | Cached tokens | Source patch | Workspace churn |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Medium | 7/10 | 1860.522 / 186.052 / 117.744 | 280 / 28.00 / 18.00 | 293 / 29.30 / 14.50 | 319031 | 2871 | 310943 | +183/-35 lines, 19 source files | 19 files, generated 0 |
| Max | 6/10 | 4383.847 / 438.385 / 409.526 | 381 / 38.10 / 31.50 | 398 / 39.80 / 32.00 | 498938 | 5348 | 481869 | +221/-42 lines, 20 source files | 20 files, generated 0 |

Max/Medium mean ratios were **2.356× wall time**, **1.361× steps**, **1.358× tool calls**, **1.564× prompt tokens**, **1.863× completion tokens**, and **1.550× cached tokens**. Source-only patch totals were +183/-35 lines for Medium and +221/-42 for Max. All 39 changed entries were source files; generated/environment-file churn was zero.

## Historical versus newly constructed

| Subset | Medium | Max | Medium wall mean s | Max wall mean s | Medium steps | Max steps | Medium tools | Max tools |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Historical/public | 4/5 | 4/5 | 290.133 | 645.638 | 42.4 | 59.4 | 48.4 | 62.6 |
| Newly constructed/withheld | 3/5 | 2/5 | 81.971 | 231.131 | 13.6 | 16.8 | 10.2 | 17.0 |

Historical/public cases produced 4/5 for both conditions. Newly constructed/withheld cases produced 3/5 for Medium and 2/5 for Max. This provenance association is descriptive: the K cases may be known from public historical data, while H cases were withheld until execution; no absolute training-corpus absence claim is made.

## Paired outcomes and resource deltas

The paired CSV is [`results/experiment-005-paired.csv`](../results/experiment-005-paired.csv). Deltas are Max minus Medium; positive wall-time values mean Max took longer.

| Case | Provenance | Outcome | Wall Δ s | Steps Δ | Tools Δ | Prompt Δ | Completion Δ | Cached Δ | Same patch | Visible/held-out disagreement |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| E005-H01 | newly-constructed-withheld | both success | 90.108 | 3 | 6 | 4848 | 67 | -8192 | yes | no |
| E005-H02 | newly-constructed-withheld | both fail | 334.064 | 4 | 6 | 15761 | 155 | 15744 | no | yes |
| E005-H03 | newly-constructed-withheld | Medium-only | 135.638 | 4 | 6 | 9568 | 75 | 12864 | no | no |
| E005-H04 | newly-constructed-withheld | both success | 31.985 | 2 | 4 | 2146 | 69 | 1984 | yes | no |
| E005-H05 | newly-constructed-withheld | both fail | 154.006 | 3 | 12 | 7419 | 281 | 6375 | no | yes |
| E005-K01 | historical-public | both success | 181.321 | 0 | -31 | 4771 | -80 | 6901 | no | no |
| E005-K02 | historical-public | Medium-only | 333.440 | 2 | 5 | 31377 | 239 | 30876 | no | yes |
| E005-K03 | historical-public | both success | 420.648 | 22 | 29 | 30548 | 529 | 30528 | no | no |
| E005-K04 | historical-public | Max-only | 578.499 | 37 | 41 | 53832 | 698 | 53578 | no | no |
| E005-K05 | historical-public | both success | 263.615 | 24 | 27 | 19637 | 444 | 20268 | no | no |

Max took longer in all 10 pairs. It used at least as many steps in every pair (more in 9/10), more tool calls in 9/10, and more prompt and completion tokens in every pair. Cached tokens were higher in 9/10 pairs; H01 was the one exception. Source patches were byte-identical in 2/10 pairs (H01 and H04).

## Every behavioral failure

- **E005-H02-M:** Held-out behavior failed because cancellation was recorded as terminal but the CancelledError was not retained as the job's error provenance; public and regression suites passed.
- **E005-H02-X:** Held-out behavior failed because cancellation was recorded as terminal but the CancelledError was not retained as the job's error provenance; public and regression suites passed.
- **E005-H03-X:** Regression failed because the attempted oversized-frame recovery skipped the following valid frame when the declared oversized payload bytes were not present; public and held-out suites passed.
- **E005-H05-M:** Held-out behavior failed because a subscription closed during an active dispatch was skipped immediately, instead of remaining effective for the current stable dispatch; public and regression suites passed.
- **E005-H05-X:** Held-out behavior failed because a subscription closed during an active dispatch was skipped immediately, instead of remaining effective for the current stable dispatch; public and regression suites passed.
- **E005-K02-X:** Held-out behavior failed because the patch added the scheduler parameter and pruning call but did not enable pruning in the local scheduler factory; public and regression suites passed.
- **E005-K04-M:** Public and held-out behavior failed because cycle cleanup was moved into RequestHandler.finish, clearing template state before an ordinary WebSocket render; regression passed.

The seven failed task outcomes were all evaluator-observed behavioral misses, not infrastructure failures. There were no timeouts: all 20 termination states were `completed`, all runner return codes were 0, all evaluator statuses were `OK`, and all workspace leak audits passed.

## Comparison with moderate experiments

E002 historical and E004 novel-calibrated form the frozen moderate comparator specified by E005. E003 is supplemental and excluded from the balanced primary tier.

| Dataset | Medium | Max | Both success | Medium-only | Max-only | Both fail |
|---|---:|---:|---:|---:|---:|---:|
| E002 historical | 5/5 | 4/5 | 4 | 1 | 0 | 0 |
| E004 novel calibrated | 5/5 | 4/5 | 4 | 1 | 0 | 0 |
| Combined moderate comparator | 10/10 | 8/10 | 8 | 2 | 0 | 0 |
| E005 HARD historical/public | 4/5 | 4/5 | 3 | 1 | 1 | 0 |
| E005 HARD newly constructed/withheld | 3/5 | 2/5 | 2 | 1 | 0 | 2 |
| E005 HARD balanced total | 7/10 | 6/10 | 5 | 2 | 1 | 2 |
| E003 supplemental novel/easier | 5/5 | 5/5 | 5 | 0 | 0 | 0 |

The combined moderate comparator's resource means were **222.880 wall seconds, 28.0 steps, and 23.0 tool calls per Medium run**, versus **429.483 wall seconds, 36.2 steps, and 43.7 tool calls per Max run**. Its aggregate prompt/completion/cached tokens were 4,773,353/72,965/4,557,005 for Medium and 12,598,295/185,635/12,200,427 for Max. E005 used fewer Medium prompt tokens and far fewer Max prompt tokens than that combined comparator, but its Max wall mean was slightly higher; resource scale is therefore not a single-axis hardness measure.

Outcome-wise, E005 was more discriminating than the moderate comparator: Medium fell from 10/10 to 7/10 and Max from 8/10 to 6/10, with two both-fail pairs appearing in the withheld H set. This is an empirical hardness signal, not a calibrated causal measurement, because the case sets and repository surfaces differ.

Raw workloads are not directly interchangeable. E005's historical means were 290.133 seconds for Medium and 645.638 for Max, versus E002's 363.262 and 729.956; E005's newly constructed means were 81.971 and 231.131, versus E004's 82.498 and 129.009. Thus E005 was lighter than E002 on historical wall time, similar to E004 for Medium, and heavier than E004 for Max, while its complete-repair outcomes were lower than both moderate datasets.

## Supplemental E003

E003's five novel/easier pairs were all successful for both conditions (5/5 each; five both-success pairs). E005's five historical and five withheld cases were materially harder in observed repair outcomes, especially on withheld Max (2/5 on the H subset). E003 remains supplemental evidence, not part of E005's balanced HARD denominator.

## What additional effort did and did not show

Max did not improve the overall E005 success rate: it solved 6/10 versus Medium's 7/10 despite consuming more observable resources. It produced one Max-only win (K04), but also two Medium-only wins (K02 and H03), and the H02 and H05 pairs failed for both conditions. The pattern is therefore mixed rather than a monotonic effort advantage.

These are associations in ten paired cases. Observable steps, tool calls, tokens, wall time, patches, and evaluator outcomes are not internal reasoning, and the sample does not support significance testing, causality, or a general model-capability conclusion. Cost, usage, and ACUs were unavailable.

## Reproducibility, privacy, and validation

- The 20 run IDs occurred exactly once in the frozen order, with 10 Medium and 10 Max assignments and each of the 10 cases represented once per condition.
- The freeze image digest, configuration, run-order manifest, prompts, case hashes, and resource limits were preflight-verified; all 20 post-session audits passed.
- Evaluator access occurred only after session close. Private evaluator/reference inputs, credentials, hidden reasoning, raw machine paths, and full workspaces are not published.
- The repository's E001-E004 evidence, releases, tags, and frozen E005 experimental contents remain unchanged; this publication adds only E005 results and analysis artifacts.
- No GitHub release or website article was created.

Published outputs:

- [`reports/experiment-005-results.md`](experiment-005-results.md)
- [`results/experiment-005-summary.json`](../results/experiment-005-summary.json)
- [`results/experiment-005-ledger.json`](../results/experiment-005-ledger.json)
- [`results/experiment-005-paired.csv`](../results/experiment-005-paired.csv)
- [`artifacts/experiment-005/`](../artifacts/experiment-005/)
