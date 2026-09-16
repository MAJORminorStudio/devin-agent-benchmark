# Experiment 004 Results

## Question

Does the Medium-versus-Max reasoning-effort pattern observed in E002 replicate on five newly constructed software defects calibrated to the E002 difficulty envelope?

## Methodology

E004 was executed once per condition for five newly constructed, withheld cases in the frozen order. Devin received only a fresh sanitized buggy workspace and the byte-identical case prompt. Each disposable Linux/arm64 session used the frozen E002 image, internal network, restricted proxy, read-only root, dropped capabilities, no-new-privileges, no Docker socket, no control-repository or evaluator mounts, one read-only credential mount, 4 GiB memory, 4 CPUs, a 512-process limit, a 3,600-second maximum, sequential execution, and zero retries or substantive interventions. The evaluator ran only after each container closed.

The [frozen protocol](../docs/experiment-004-protocol.md), [configuration](../manifests/experiment-004-config.json), [run order](../manifests/experiment-004-runs.json), and [freeze manifest](../manifests/experiment-004-freeze.json) were byte-verified before execution.

## Results

Medium solved 5/5; Max solved 4/5. Nine runs passed public, held-out, and regression evaluation. `E004-N03-X` passed public and regression but failed the held-out behavioral suite, producing the only visible-versus-held-out disagreement. All ten containers exited normally; there were no retries, substantive interventions, or infrastructure incidents.

| Run | Case | Condition | TASK_SUCCESS | Public | Held-out | Regression | Wall s | Steps | Tool calls | Prompt tokens | Completion tokens | Source patch | Generated files |
|---|---|---:|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| E004-N05-X | E004-N05 | X | 1 | pass | pass | pass | 141.470 | 17 | 26 | 163640 | 5410 | +0/-2 | 0 |
| E004-N04-M | E004-N04 | M | 1 | pass | pass | pass | 90.619 | 16 | 8 | 125364 | 1204 | +1/-1 | 0 |
| E004-N01-M | E004-N01 | M | 1 | pass | pass | pass | 74.312 | 15 | 10 | 112832 | 983 | +9/-3 | 0 |
| E004-N04-X | E004-N04 | X | 1 | pass | pass | pass | 175.100 | 20 | 27 | 226494 | 6172 | +1/-1 | 0 |
| E004-N05-M | E004-N05 | M | 1 | pass | pass | pass | 81.518 | 18 | 16 | 158632 | 1317 | +0/-2 | 0 |
| E004-N01-X | E004-N01 | X | 1 | pass | pass | pass | 105.520 | 16 | 14 | 133867 | 2232 | +9/-3 | 0 |
| E004-N02-M | E004-N02 | M | 1 | pass | pass | pass | 84.619 | 16 | 15 | 132236 | 1233 | +4/-2 | 0 |
| E004-N03-M | E004-N03 | M | 1 | pass | pass | pass | 81.421 | 16 | 12 | 123813 | 1152 | +3/-2 | 0 |
| E004-N02-X | E004-N02 | X | 1 | pass | pass | pass | 103.594 | 18 | 27 | 177160 | 2861 | +3/-0 | 0 |
| E004-N03-X | E004-N03 | X | 0 | pass | fail | pass | 119.363 | 17 | 21 | 156183 | 3977 | +2/-1 | 0 |

## Aggregate metrics

| Condition | Success | Wall total / mean / median s | Steps total / mean | Tool calls total / mean | Prompt tokens | Completion tokens | Cached tokens | Source patch | Generated/environment files |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| M | 5/5 | 412.489 / 82.498 / 81.518 | 81 / 16.20 | 61 / 12.20 | 652877 | 5889 | 588096 | +17/-10 | 0 |
| X | 4/5 | 645.047 / 129.009 / 119.363 | 88 / 17.60 | 115 / 23.00 | 857344 | 20652 | 791552 | +15/-7 | 0 |

## Paired outcomes

| Case | Outcome | Max−Medium wall s | Steps | Tool calls | Prompt tokens | Completion tokens | Cached tokens | Same source patch | Visible/held-out disagreement |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| E004-N01 | both success | +31.209 | +1 | +4 | +21035 | +1249 | +38528 | no | no |
| E004-N02 | both success | +18.975 | +2 | +12 | +44924 | +1628 | +25984 | no | no |
| E004-N03 | Medium-only | +37.942 | +1 | +9 | +32370 | +2825 | +27776 | no | yes |
| E004-N04 | both success | +84.481 | +4 | +19 | +101130 | +4968 | +103296 | no | no |
| E004-N05 | both success | +59.952 | -1 | +10 | +5008 | +4093 | +7872 | yes | no |

The paired outcome counts were 4 both-success pairs, 1 Medium-only pair, 0 Max-only pairs, and 0 both-fail pairs. Max used more wall time in all five pairs and more tool calls in all five; it used more steps in four pairs. Max also used more aggregate prompt, completion, and cached tokens. Each run changed one source file and produced zero generated/environment-file churn.

## Visible-versus-held-out disagreement

Only `E004-N03-X` disagreed: public passed, held-out failed, and regression passed. Its patch deep-copied transaction snapshots but retained a shallow copy in `replace`, leaving caller-owned nested values shared. The Medium paired run passed the held-out suite. This is an evaluator observation, not an inference about hidden reasoning.

## Comparison with E002 and E003

E002 historical scored Medium 5/5 and Max 4/5. E003 novel/easier scored Medium 5/5 and Max 5/5. E004 novel/E002-calibrated scored Medium 5/5 and Max 4/5. On the small-sample outcome pattern, E004 therefore behaved more like E002 than E003: it reproduced one Medium-only pair rather than an all-success tie.

The raw workload was lighter than E002: E004 averaged 82.498 seconds for Medium and 129.009 seconds for Max, versus E002 historical means of approximately 363.262 and 729.956 seconds. That difference is consistent with the smaller synthetic projects and means E004 did not establish full E002 workload equivalence.

## Intended difficulty assessment

E004 partially achieved its intended apparent difficulty in practice. The one held-out Max miss and the E002-like paired outcome provide a difficulty signal, while the much shorter sessions and compact one-file patches show that the benchmark was operationally lighter than E002. With five pairs, this is descriptive evidence only; no causal or statistical-significance claim is warranted.

## Validation and reproducibility

- All ten frozen run IDs occurred exactly once in the specified order.
- Every run used the frozen model assignment and resource limits; all containers recorded normal completion.
- The E004 freeze manifest, case hashes, prompt hashes, run order, and workspace staging were verified before execution.
- Private E004 evaluator results were generated after container closure and were not mounted into subsequent runs.
- All source patches, evaluator statuses, session IDs, wall times, steps, tool calls, token totals, termination states, and churn metrics were captured.
- The repository’s pre-existing E001/E002/E003 evidence and E005 experimental contents were not modified.
- Sanitized artifacts are under [`artifacts/experiment-004/`](../artifacts/experiment-004/). Raw session exports and private evaluator inputs remain outside the repository.

## Limitations

This is an exploratory n=5 paired comparison. Observable activity is not internal reasoning. Costs and ACUs were unavailable. The cases are newly constructed and no claim is made about absence from training data. The two pre-execution checker corrections were confined to validation logic; no E004 case reached Devin until the final preflight passed.

## Conclusion

E004 produced 5/5 Medium and 4/5 Max, matching E002’s aggregate success pattern and differing from E003’s 5/5 tie. The result is suggestive that the E004 set was more discriminating than E003, but it does not support a general claim about model effort or difficulty equivalence.
