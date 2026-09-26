# E008 Stability Analysis — Completed Targeted Repeats

## Execution and evaluation record

Exactly **33/33** frozen slots were attempted across the approved **9 cases and 11 case/effort conditions**. There were 33 distinct session IDs, zero human interventions, no High or stable conditions, and no replacement sessions.

All 33 existing workspaces now have valid final evaluations. The first nine E002 sessions initially hit a local adapter `KeyError` before tests ran; the same preserved workspaces were re-evaluated using the frozen suites after cache sanitation. The initial adapter failures remain in each ledger row, alongside the final adjudication. Slot 10’s completed session and evaluator result were recovered from preserved output after a local JSON serialization failure; that session was not rerun. No Devin trial was replaced. Historical E007 results remain unchanged.

Actual direct cost is **UNKNOWN**: no billing evidence was exposed. The old catalog-based estimate is not treated as actual cost.

## Five-observation outcome sequences

Each sequence orders the original result, E007 clean-rechecked result, and E008 repetitions 1–3. The five observations remain visible; the solve count is descriptive because the observations are dependent by case and the sample was selected for historical disagreement.

| Case | Difficulty | Effort | Five outcomes | Solves / 5 | E008 repeats | Repeat consistency |
| --- | --- | --- | --- | --- | --- | --- |
| E002-C02 | Moderate | Medium | PASS FAIL PASS FAIL PASS | 3/5 | 2/3 | mixed |
| E002-C05 | Moderate | Medium | PASS FAIL FAIL FAIL FAIL | 1/5 | 0/3 | unanimous fail |
| E002-C05 | Moderate | Max | PASS FAIL FAIL FAIL FAIL | 1/5 | 0/3 | unanimous fail |
| E004-N03 | Moderate | Medium | PASS FAIL FAIL FAIL FAIL | 1/5 | 0/3 | unanimous fail |
| E004-N03 | Moderate | Max | FAIL PASS PASS PASS PASS | 4/5 | 3/3 | unanimous pass |
| E005-K04 | Hard | Medium | FAIL PASS PASS PASS PASS | 4/5 | 3/3 | unanimous pass |
| E005-K02 | Hard | Max | FAIL PASS PASS PASS PASS | 4/5 | 3/3 | unanimous pass |
| E005-K01 | Hard | Medium | PASS FAIL FAIL PASS PASS | 3/5 | 2/3 | mixed |
| E005-H03 | Hard | Max | FAIL PASS FAIL PASS PASS | 3/5 | 2/3 | mixed |
| E006-H03 | Very-Hard | Medium | FAIL PASS PASS PASS FAIL | 3/5 | 2/3 | mixed |
| E006-H01 | Very-Hard | Max | PASS FAIL FAIL PASS PASS | 3/5 | 2/3 | mixed |

The 11 five-observation sequences sum to 30/55 solves. New repeats sum to 19/33. These are selected discordant conditions and do not estimate full-benchmark accuracy.

## Within-condition telemetry and recurring suite failures

Ranges and medians are from the three new E008 runs only. Token totals are model counters, not cost. Failure labels name evaluator suites, not root causes or individual test IDs.

| Case | Effort | Steps min–max (median) | Wall seconds min–max (median) | Tokens min–max (median) | Failed suites across 3 |
| --- | --- | --- | --- | --- | --- |
| E002-C02 | Medium | 39.0–50.0 (med 41.0) | 229.5–306.6 (med 281.3) | 767745–957195 (med 797003) | heldout:1/3, public:1/3 |
| E002-C05 | Medium | 21.0–32.0 (med 22.0) | 107.0–132.6 (med 108.4) | 221055–461955 (med 242634) | heldout:3/3 |
| E002-C05 | Max | 38.0–48.0 (med 40.0) | 226.6–259.1 (med 253.2) | 953290–1301121 (med 961525) | heldout:3/3 |
| E004-N03 | Medium | 15.0–16.0 (med 16.0) | 81.9–95.6 (med 90.7) | 113805–131595 (med 124826) | heldout:3/3 |
| E004-N03 | Max | 17.0–18.0 (med 18.0) | 112.1–151.4 (med 125.0) | 160598–185076 (med 179885) | none |
| E005-K04 | Medium | 38.0–48.0 (med 43.0) | 291.6–384.1 (med 319.2) | 1141533–1206318 (med 1205540) | none |
| E005-K02 | Max | 57.0–88.0 (med 64.0) | 468.7–570.1 (med 519.7) | 3445323–5555256 (med 3752377) | none |
| E005-K01 | Medium | 39.0–50.0 (med 39.0) | 229.1–259.1 (med 243.7) | 976878–1515715 (med 1480185) | heldout:1/3 |
| E005-H03 | Max | 14.0–18.0 (med 17.0) | 124.9–399.7 (med 223.1) | 110591–273342 (med 198922) | regression:1/3 |
| E006-H03 | Medium | 13.0–14.0 (med 14.0) | 95.0–143.2 (med 97.7) | 83628–110443 (med 100918) | heldout:1/3 |
| E006-H01 | Max | 14.0–18.0 (med 14.0) | 156.3–431.4 (med 282.1) | 122266–272221 (med 144188) | regression:1/3 |


Across new runs, failed suite counts were: heldout=12, public=1, regression=2. These categories overlap when a run fails multiple suites.

## Stability by effort and difficulty

| Effort | Conditions | New repeat solves | Unanimous conditions | Mixed conditions | Five-observation solves |
| --- | --- | --- | --- | --- | --- |
| Medium | 6 | 9/18 | 3/6 | 3/6 | 15/30 (50%) |
| Max | 5 | 10/15 | 3/5 | 2/5 | 15/25 (60%) |


| Difficulty | Conditions | New repeat solves | Unanimous | Mixed |
| --- | --- | --- | --- | --- |
| Moderate | 5 | 5/15 | 4 | 1 |
| Hard | 4 | 10/12 | 2 | 2 |
| Very-Hard | 2 | 4/6 | 0 | 2 |


Six of 11 selected conditions were unanimous across the three new runs; five were mixed. Medium had 3/6 unanimous conditions and Max 3/5. These proportions are similar and the conditions are not balanced or fully paired, so they do not establish that one effort setting is more stable. New-repeat descriptive solves were 9/18 for Medium and 10/15 for Max; do not interpret these as independent benchmark samples.

Mixed repeat outcomes occurred in 1/5 moderate, 2/4 hard, and 2/2 very-hard conditions. This suggests more observed mixing at higher difficulty in this selected sample, particularly 2/2 very-hard conditions, but the small, discordance-selected groups cannot support a general difficulty trend.

## Answers to the preregistered questions

1. **Are discordant cases unstable?** Five conditions had mixed outcomes across the three repeats; six were unanimous. E008-C02 Medium, E005-K01 Medium, E005-H03 Max, E006-H03 Medium, and E006-H01 Max were mixed. Three repeats are a small descriptive check, not a reliability estimate.
2. **Is one effort more stable?** No clear difference: 3/6 Medium and 3/5 Max conditions were unanimous. The selected condition sets differ.
3. **Is within-condition variance comparable to the effort gap?** Only E004-N03 has both effort settings in this rerun. Its Medium repeats were 0/3 and Max 3/3, while each setting was internally unanimous. This one 100-point contrast shows a possible effort difference on that case, not a population-level comparison. Other selected conditions have only one effort, so broad within-versus-between variance is not estimable.
4. **Does instability concentrate by difficulty?** Mixed conditions were 1/5 moderate, 2/4 hard, and 2/2 very-hard. This is suggestive only; the very-hard denominator is two.
5. **Does the original Medium-vs-Max interpretation survive?** The original full benchmark difference was one case (24/30 Medium vs 23/30 Max). This targeted sample is not a fresh full-benchmark comparison. E004-N03 favors Max in repeats, while most cases do not have both efforts repeated. The original near-tie is neither confirmed nor overturned.
6. **Does E007 High/Max tie remain meaningful?** Not tested: High was not included in the approved repeat manifest. E007’s clean-rechecked High and Max scores were both 24/30, but this design cannot estimate High run variance.
7. **Is there evidence of temporal/backend drift?** No distinguishing evidence. New sessions were run Sep 26, after E007; provider deployment revision and per-session backend identity are unavailable. The observed mixed repeats demonstrate run-to-run variation, but do not separate stochastic execution from temporal/backend change.

## Publication readiness and remaining uncertainty

The run ledger, preserved session exports, corrected E002 evaluator results, exact five-outcome sequences, suite statuses, telemetry ranges, and checksums support an auditable technical report. The results are **not ready for a publication claim that SWE-2 effort levels differ reliably or that temporal model drift caused the historical change**. The repeat sample is small and selected, High was not repeated, and actual cost is unknown. A paper can report this as a targeted descriptive stability study with these limits explicit.
