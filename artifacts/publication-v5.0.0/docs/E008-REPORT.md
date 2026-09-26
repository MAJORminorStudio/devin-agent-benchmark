# E008 Replication and Stability Report

**Status: 33/33 approved trial slots completed.** No conditions were added and no Devin sessions were replaced. The first nine E002 evaluator attempts hit a local adapter error; the same preserved workspaces were cleanly re-evaluated after repair. One serialization error at slot 10 was recovered from the preserved runner/session/evaluator files without another session. Initial errors remain visible in the ledger. Actual cost is **unknown**.

## 1. Comparability verdict

The 30 case identities, prompts, source snapshots, held-out/regression assets, task score contract, SWE-2 Medium/Max selectors, CLI version, permissions, and isolation are identical or equivalent in frozen records. Execution dates differ (Sep 15–16 versus Sep 25, 2026); private backend deployment revision is unknown.

**A material E007 evaluator staging defect was found in the very-hard tier.** Some original E007 held-out/regression results were pytest collection errors caused by stale `.pyc` files embedding the source evaluator’s host path. We copied the frozen evaluator directories, removed only generated cache files in the copies, and re-evaluated all 30 existing E007 very-hard workspaces using the same pinned runtime and tests. No agent sessions were run and E007’s records were not changed. See `E008-E007-EVALUATOR-RECHECK.md` and its machine-readable outputs.

| Effort | E007 recorded score | E007 after clean evaluator recheck |
|---|---:|---:|
| Medium | 16/30 | 22/30 |
| High | 18/30 | 24/30 |
| Max | 18/30 | 24/30 |

Each effort had six very-hard runs change from recorded failure to pass after the clean recheck; other very-hard outcomes remained failures. Therefore the recorded E007 16/18/18 triplet materially reflects evaluator cache failures in addition to agent outcomes. Clean-recheck values are E008 sensitivity results, not replacements for the historical E007 record.

## 2. Replication agreement after the clean recheck

| Effort | Original | E007 clean-recheck | Stable solve | Stable fail | Original only | E007 only | Agreement | Exact McNemar p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Medium | 24/30 | 22/30 | 20 | 4 | 4 | 2 | 24/30 (80.0%; 95% CI 62.7%–90.5%) | 0.6875 |
| Max | 23/30 | 24/30 | 21 | 4 | 2 | 3 | 25/30 (83.3%; 95% CI 66.4%–92.7%) | 1.0000 |


Intervals are Wilson 95% intervals for case-level agreement. Exact two-sided McNemar p-values use discordant pairs. These are unadjusted paired comparisons, and the 30 cases are a fixed benchmark rather than a random sample of all coding tasks.

The original benchmark reconciles to Medium 24/30 and Max 23/30. E007’s recorded scores reconcile to 16/30 Medium, 18/30 High, and 18/30 Max. After the clean E007 evaluator recheck, the Medium/High/Max totals are 22/30, 24/30, and 24/30.

## 3. Drift by difficulty

| Difficulty | Effort | Original | E007 clean recheck | Absolute change | Stable solves | Stable failures | Original only | E007 only | Agreement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Moderate | Medium | 10/10 | 7/10 | -30% | 7 | 0 | 3 | 0 | 7/10 |
| Moderate | Max | 8/10 | 8/10 | +0% | 7 | 1 | 1 | 1 | 8/10 |
| Hard | Medium | 7/10 | 7/10 | +0% | 6 | 2 | 1 | 1 | 8/10 |
| Hard | Max | 6/10 | 8/10 | +20% | 6 | 2 | 0 | 2 | 8/10 |
| Very-Hard | Medium | 7/10 | 8/10 | +10% | 7 | 2 | 0 | 1 | 9/10 |
| Very-Hard | Max | 9/10 | 8/10 | -10% | 8 | 1 | 1 | 0 | 9/10 |


Each tier has n=10. The Medium decline is concentrated in moderate cases (10→7); its hard tier is unchanged and very-hard rises 7→8 after recheck. Max is unchanged in moderate, rises 6→8 in hard, and declines 9→8 in very-hard. The sample is too small to infer a difficulty trend.

## 4. Discordant cases

There are **9 cases** and **11 case-effort disagreements** after recheck: E002-C02, E002-C05, E004-N03, E005-K04, E005-K02, E005-K01, E005-H03, E006-H03, E006-H01.

Changed effort settings: E002-C02: Medium; E002-C05: Medium, Max; E004-N03: Medium, Max; E005-K04: Medium; E005-K02: Max; E005-K01: Medium; E005-H03: Max; E006-H03: Medium; E006-H01: Max.

The original-only versus E007-only counts show disagreement runs in both directions. Per-case evaluator statuses, patch files, steps, runtime, tokens, and heuristic trace counts are in `E008-DISCORDANT-CASES.md`. That file separates observation, interpretation, and unresolved cause for every changed cell.

## 5. Failure-mode differences

| Condition | Successful | Public failure | Held-out only | Regression only | Multiple suites |
| --- | --- | --- | --- | --- | --- |
| Original Medium | 24 | 0 | 4 | 1 | 1 |
| E007 Medium | 22 | 1 | 6 | 1 | 0 |
| Original Max | 23 | 0 | 6 | 1 | 0 |
| E007 Max | 24 | 0 | 5 | 1 | 0 |


Most failed cells are held-out misses; no specific diagnosis-stage category is consistently available across parent experiments. The initial E007 score drop was substantially inflated by evaluator staging errors in the very-hard tier. After recheck, remaining failures are valid evaluator results but do not by themselves establish changed model behavior.

## 6. Behavioral differences

| Effort | Metric | Paired n | Original median | E007 median | Median Δ | Original mean | E007 mean | Mean Δ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Medium | steps | 30 | 17.0 | 16.5 | -0.5 | 26.1 | 24.5 | -1.6 |
| Medium | wall_seconds | 30 | 118.2 | 117.9 | +9.0 | 283.2 | 185.5 | -97.7 |
| Medium | tokens | 30 | 111184.0 | 134985.0 | +14798.5 | 289736.0 | 418475.0 | +128739.0 |
| Max | steps | 30 | 19.0 | 19.5 | +0.0 | 36.8 | 41.3 | +4.5 |
| Max | wall_seconds | 30 | 407.0 | 297.0 | -25.3 | 529.0 | 524.9 | -4.0 |
| Max | tokens | 30 | 174535.5 | 369133.5 | +101550.5 | 907169.9 | 1851498.1 | +944328.2 |


Heuristic trace-derived telemetry across all cases:

| Effort | Trace metric | Original n | E007 n | Original median | E007 median | Original mean | E007 mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Medium | tool_calls | 30 | 30 | 14.5 | 13.5 | 24.4 | 20.7 |
| Medium | exploration_calls_heuristic | 30 | 30 | 11.5 | 12.5 | 17.8 | 15.9 |
| Medium | edit_calls_heuristic | 30 | 30 | 2.0 | 3.0 | 3.9 | 3.9 |
| Medium | test_calls_heuristic | 30 | 30 | 3.0 | 3.5 | 4.9 | 4.6 |
| Medium | first_edit_step_heuristic | 30 | 30 | 12.0 | 11.5 | 14.2 | 14.0 |
| Medium | source_files_changed_heuristic | 30 | 5 | 1.0 | 1.0 | 1.7 | 1.2 |
| Max | tool_calls | 30 | 30 | 27.0 | 25.5 | 40.1 | 47.2 |
| Max | exploration_calls_heuristic | 30 | 30 | 23.5 | 20.5 | 27.4 | 31.4 |
| Max | edit_calls_heuristic | 30 | 30 | 3.0 | 3.0 | 6.5 | 9.1 |
| Max | test_calls_heuristic | 30 | 30 | 3.0 | 3.0 | 4.7 | 7.0 |
| Max | first_edit_step_heuristic | 30 | 30 | 15.0 | 15.0 | 19.5 | 18.8 |
| Max | source_files_changed_heuristic | 30 | 5 | 1.0 | 1.0 | 1.7 | 1.0 |


The medians show similar step counts and wall times; token medians are higher in E007, especially for Max. Means are skewed by a few unusually large sessions. All three metrics have 30 paired observations and no missing values. Trace metrics use a common heuristic parser, with available n and missingness shown; exact files inspected and private planning/reasoning cannot be compared. These observations do not identify a private model change.

## 7. What explains the difference?

The strongest concrete explanation is **evaluator/tooling error**, not a model capability change: six recorded E007 failures in each effort’s very-hard tier pass when the same existing workspaces are evaluated with clean copies of the frozen tests. With that correction, original-to-E007 solve-count changes shrink from the recorded differences to Medium −2 cases and Max +1 case, and the sign of the aggregate Medium-versus-Max comparison changes across experiments.

Among the corrected outcomes, ordinary stochastic variance remains plausible because single runs disagree on 11 cells. Systematic temporal model/backend drift remains possible because the dates differ and no deployment revision is exposed. The records cannot distinguish the two.

E008 repeats show mixed outcomes in 5 of 11 selected conditions and unanimous results in 6. Because the sample was selected for historical discordance, the effort sets are unequal, and only three repeats were run per condition, this does not estimate population-level reliability. Backend drift remains unresolved.

## 8. Completed targeted repeat analysis

Exactly **33 planned sessions** were attempted and evaluated; all 33 final outcomes are valid. The first nine E002 sessions’ adapter failures and the slot-10 serialization incident are documented alongside their recovered or adjudicated results. No retries or replacement sessions occurred. Full five-outcome sequences, repeat-only stability, telemetry ranges, suite failures, and limits are in `E008-STABILITY-ANALYSIS.md`.

The 11 five-observation sequences contain **30/55 solves** across a discordance-selected sample. New repeats yielded **19/33 passes**. Six conditions were unanimous over three new trials and five were mixed. Medium and Max were similar on the proportion of unanimous selected conditions (3/6 vs 3/5); the design does not establish one effort as more stable. Mixed outcomes appeared in 1/5 moderate, 2/4 hard, and 2/2 very-hard conditions, which is descriptive only.

Only E004-N03 has both efforts repeated: its Medium repeats were 0/3 and Max repeats 3/3. This one case does not overturn the original 24/30 vs 23/30 near-tie, nor establish a general effort effect. High was not repeated, so E007’s corrected High/Max tie is not assessed by this rerun. The observed repeat variation does not distinguish stochastic runs from temporal/backend drift.

Actual direct cost is **UNKNOWN**; no billing evidence was exposed. The earlier catalog-only estimate is not an actual-cost claim. The session ledger and evaluator adjudications are preserved separately, and E007’s historical records and scores remain unchanged.

**Publication readiness:** suitable as a transparently documented targeted descriptive stability report; not sufficient to claim a general effort-level reliability gap or identify backend drift.

## Artifact index

- `E008-COMPARABILITY-AUDIT.md`
- `E008-REPLICATION-MATRIX.csv` and `.json`
- `E008-DISCORDANT-CASES.md`
- `E008-FAILURE-TAXONOMY.md`
- `E008-BEHAVIORAL-DRIFT.md`
- `E008-RERUN-PLAN.md` and `E008-RERUN-MANIFEST.json`
- `E008-E007-EVALUATOR-RECHECK.md` and machine-readable evaluator results
- `E008-STABILITY-ANALYSIS.md` and `.json`, `E008-RUNS.jsonl`, `E008-E002-ADJUDICATION.json`, `E008-EXECUTION-SUMMARY.json`, `E008-RERUN-MANIFEST-APPROVED-FROZEN.json`, and `charts/`
- Repeat charts: `07-five-outcome-sequences.png`, `08-three-repeat-frequencies.png`, and `09-repeat-telemetry-ranges.png`
