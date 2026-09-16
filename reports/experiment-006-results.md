# Experiment 006 results

> Frozen VERY-HARD capability-frontier execution; descriptive results, not a causal model comparison.

## Executive result

Experiment 006 completed **20/20 runs** in the frozen order. Medium solved **7/10 (70%)** and Max solved **9/10 (90%)**. Paired outcomes: **7 both success, 2 Max-only, 0 Medium-only, and 1 both fail**.

Max supplied unique value in this sample: two Max-only repairs and no Medium-only repairs. This is descriptive evidence, not proof that model capability caused the difference.

## Frozen protocol and execution integrity

- Control commit: `2dc707f83bb370d594633332da19d59031bd7dd7`.
- Freeze manifest SHA-256: `1fed8dab0a0c1a626fdce06d76109f8cf087f81b1e32c78bc1d9ca8f151f7c6c`; configuration SHA-256: `d8add5f6d9de64b010f5f2c8cb191a1c5ab269e8a70d8a8ad3b1b29c909154b9`; frozen run-order SHA-256: `326e8a2fd202fa712d532d5ea84f35d4178d1cfbf602aa045d4a649d6a83817c`.
- Exact image: `devin-e006:3000.10.21-r7@sha256:7557a0bc640492d8f77f271ebafc6402733fa0ba843c344f74ab613b94416699`; image ID `sha256:7557a0bc640492d8f77f271ebafc6402733fa0ba843c344f74ab613b94416699`; platform `linux/arm64`.
- Network: `e002-internal`; egress proxy `http://egress-proxy:3128`; direct internet disabled; evaluator access withheld until session close.
- Limits: 4g memory, 4 CPUs, 512 PIDs, read-only root, all capabilities dropped, no-new-privileges, 7200-second wall limit.
- Devin invocations: 20; ordinary retries: 0; substantive interventions: 0; timeouts: 0; evaluator status: 20/20 `OK`.
- One pre-invocation launcher staging incident occurred for E006-H02-M: the runner rejected a non-empty output directory before any Devin container or paid session started. The paths were quarantined and H02-M was then invoked once correctly; this is recorded separately from the scientific run ledger.

## Complete run ledger

`M` = swe-2-medium; `X` = swe-2-max. Token counts are the captured prompt, completion, and cached categories. PASS is the frozen public/held-out/regression evaluator result.

| # | Run | Cond. | Provenance | Pub | Hold | Reg | Result | Wall s | Steps | Tools | Prompt | Completion | Cached | Src | +/− |
|---:|---|:---:|---|:---:|:---:|:---:|:---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | E006-K03-M | M | historical-public | PASS | PASS | PASS | PASS | 2599.3 | 45 | 39 | 788,115 | 8,069 | 561,408 | 1 | +12/−0 |
| 2 | E006-H02-M | M | newly-constructed-withheld | PASS | PASS | PASS | PASS | 116.4 | 14 | 11 | 99,965 | 1,676 | 91,832 | 1 | +16/−8 |
| 3 | E006-H03-M | M | newly-constructed-withheld | PASS | FAIL | PASS | FAIL | 119.9 | 12 | 10 | 69,060 | 1,449 | 53,556 | 1 | +2/−2 |
| 4 | E006-H02-X | X | newly-constructed-withheld | PASS | PASS | PASS | PASS | 789.4 | 17 | 18 | 291,431 | 26,742 | 256,886 | 1 | +25/−12 |
| 5 | E006-K05-M | M | historical-public | PASS | PASS | PASS | PASS | 367.0 | 31 | 26 | 534,463 | 9,460 | 504,091 | 2 | +7/−5 |
| 6 | E006-K04-M | M | historical-public | PASS | PASS | PASS | PASS | 225.8 | 28 | 25 | 404,472 | 4,497 | 378,505 | 1 | +5/−6 |
| 7 | E006-H01-X | X | newly-constructed-withheld | PASS | PASS | PASS | PASS | 409.6 | 18 | 19 | 227,234 | 12,431 | 203,449 | 2 | +13/−8 |
| 8 | E006-H05-X | X | newly-constructed-withheld | PASS | PASS | PASS | PASS | 134.7 | 14 | 13 | 98,109 | 2,023 | 90,311 | 1 | +4/−2 |
| 9 | E006-K05-X | X | historical-public | PASS | PASS | PASS | PASS | 1365.8 | 73 | 70 | 4,002,470 | 49,444 | 3,884,714 | 2 | +9/−6 |
| 10 | E006-K02-X | X | historical-public | PASS | PASS | PASS | PASS | 177.4 | 17 | 14 | 188,263 | 3,661 | 172,521 | 1 | +1/−1 |
| 11 | E006-H04-M | M | newly-constructed-withheld | PASS | FAIL | PASS | FAIL | 105.1 | 12 | 10 | 67,898 | 1,345 | 61,031 | 2 | +7/−3 |
| 12 | E006-H03-X | X | newly-constructed-withheld | PASS | PASS | PASS | PASS | 564.3 | 18 | 18 | 266,586 | 19,519 | 237,908 | 1 | +21/−3 |
| 13 | E006-H05-M | M | newly-constructed-withheld | PASS | PASS | PASS | PASS | 93.3 | 12 | 10 | 66,620 | 751 | 52,252 | 1 | +2/−2 |
| 14 | E006-H04-X | X | newly-constructed-withheld | PASS | FAIL | PASS | FAIL | 230.9 | 14 | 15 | 110,878 | 5,795 | 99,960 | 2 | +8/−3 |
| 15 | E006-H01-M | M | newly-constructed-withheld | PASS | PASS | FAIL | FAIL | 107.9 | 14 | 12 | 100,390 | 1,362 | 84,091 | 2 | +5/−2 |
| 16 | E006-K03-X | X | historical-public | PASS | PASS | PASS | PASS | 771.2 | 53 | 52 | 1,749,247 | 24,998 | 1,694,674 | 1 | +11/−0 |
| 17 | E006-K04-X | X | historical-public | PASS | PASS | PASS | PASS | 941.2 | 67 | 70 | 2,575,863 | 32,090 | 2,511,811 | 1 | +8/−9 |
| 18 | E006-K01-M | M | historical-public | PASS | PASS | PASS | PASS | 567.0 | 40 | 58 | 1,252,164 | 18,313 | 1,200,323 | 10 | +65/−17 |
| 19 | E006-K01-X | X | historical-public | PASS | PASS | PASS | PASS | 1805.5 | 69 | 80 | 4,173,900 | 66,196 | 4,011,582 | 10 | +73/−20 |
| 20 | E006-K02-M | M | historical-public | PASS | PASS | PASS | PASS | 105.0 | 15 | 7 | 107,574 | 979 | 92,476 | 1 | +1/−1 |

## Condition aggregates

| Condition | Success | Wall mean/median s | Steps mean/median | Tools mean/median | Prompt mean | Completion mean | Cached mean | Source files mean | Source +/− lines |
|:---:|:---:|---:|---:|---:|---:|---:|---:|---:|---:|
| M | 7/10 (70%) | 440.7/118.2 | 22.3/14.5 | 20.8/11.5 | 349,072.1 | 4,790.1 | 307,956.5 | 2.2 | +12.2/−4.6 |
| X | 9/10 (90%) | 719.0/667.7 | 36.0/18.0 | 36.9/18.5 | 1,368,398.1 | 24,289.9 | 1,316,381.6 | 2.2 | +17.3/−6.4 |

Max used more mean wall time (1.63×), steps (1.61×), tools (1.77×), prompt tokens (3.92×), completion tokens (5.07×), and cached tokens (4.27×). Resource scale was not sufficient for success: H04 failed under both conditions.

## Historical versus newly constructed withheld cases

| Provenance | Medium | Max |
|---|:---:|:---:|
| Historical-public K cases (n=5) | 5/5; mean 772.8 s | 5/5; mean 1012.2 s |
| Newly constructed withheld H cases (n=5) | 2/5; mean 108.5 s | 4/5; mean 425.8 s |

The provenance split is large: all historical K cases passed under both conditions, while withheld H cases passed 2/5 under Medium and 4/5 under Max. This supports treating the withheld set as the more informative frontier signal, while keeping the split explicit.

## Paired outcomes and failure forensics

| Case | Medium | Max | Pair | Key delta (Max − Medium) |
|---|:---:|:---:|---|---:|
| E006-H01 | FAIL | PASS | Max-only | wall +301.7s; steps +4; tools +7 |
| E006-H02 | PASS | PASS | both success | wall +673.0s; steps +3; tools +7 |
| E006-H03 | FAIL | PASS | Max-only | wall +444.3s; steps +6; tools +8 |
| E006-H04 | FAIL | FAIL | both fail | wall +125.9s; steps +2; tools +5 |
| E006-H05 | PASS | PASS | both success | wall +41.4s; steps +2; tools +3 |
| E006-K01 | PASS | PASS | both success | wall +1238.5s; steps +29; tools +22 |
| E006-K02 | PASS | PASS | both success | wall +72.4s; steps +2; tools +7 |
| E006-K03 | PASS | PASS | both success | wall -1828.2s; steps +8; tools +13 |
| E006-K04 | PASS | PASS | both success | wall +715.4s; steps +39; tools +45 |
| E006-K05 | PASS | PASS | both success | wall +998.8s; steps +42; tools +44 |

- E006-H01-M: regression cycle rejection raised RecursionError rather than the required ValueError; public and held-out behavior passed.
- E006-H03-M: oversized-frame recovery did not resynchronize before the later valid command; repeated frame-too-large errors replaced the required acknowledgement. Public and regression passed.
- E006-H04-M and E006-H04-X: stable dispatch membership failed because a listener closed during dispatch was skipped instead of receiving the current event; public and regression passed.
- No public evaluator failures occurred.

## Frontier interpretation

E006 separates from the moderate comparator through lower completion, hidden-contract failures, one both-fail pair, and substantially longer historical trajectories. It is not uniformly harder than E005 on every metric: Medium matched E005 at 7/10, while Max improved from 6/10 to 9/10. H03 was Medium-hard but Max-solvable; H04 was harder in practice because both conditions failed; K05 was an easy anchor with both conditions passing.

## Cumulative primary results

| Tier | Medium | Max |
|---|:---:|:---:|
| Moderate (E002 + E004) | 10/10 | 8/10 |
| HARD (E005) | 7/10 | 6/10 |
| VERY-HARD (E006) | 7/10 | 9/10 |
| **Cumulative primary** | **24/30** | **23/30** |

Cumulative paired outcomes across E002, E004, E005, and E006: 20 both success, 4 Medium-only, 3 Max-only, and 3 both fail (30 pairs). E003 remains supplemental and is excluded from this denominator.

## Public artifacts and limitations

- [Machine-readable summary](../results/experiment-006-summary.json)
- [Complete machine-readable ledger](../results/experiment-006-ledger.json)
- [Paired comparison CSV](../results/experiment-006-paired.csv)
- [Sanitized per-run evidence](../artifacts/experiment-006/)
- [Combined E002/E004/E005/E006 analysis](experiment-002-004-005-006-combined-analysis.md)

Raw workspaces, evaluator output, private evaluator sources, and credentials remain outside the repository. Public artifacts contain sanitized metadata and evidence only. No release, website, or v4 tag was created.

The results are a fixed 10-pair descriptive sample. They do not estimate generalization beyond these cases, do not establish causal model superiority, and should be interpreted with the historical/withheld provenance split and the one pre-invocation setup incident in view.
