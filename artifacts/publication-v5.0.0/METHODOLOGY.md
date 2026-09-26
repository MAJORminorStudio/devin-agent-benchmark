# Methodology

## E007: effort-level replication

E007 used 30 frozen cases—10 moderate, 10 hard, and 10 very-hard—with SWE-2 Medium, High, and Max. One Devin session was run for each case/effort cell, for 90 agent sessions. Tasks, prompts, source snapshots, evaluator contracts, and the scoring rule were frozen before execution. The binary outcome is the experiment's existing success contract over public, held-out, and regression evaluation; a test collection/infrastructure error was historically recorded as a failure before the cache defect was discovered.

The original-vs-E007 comparison uses the same 30 task identities. The E007 historical record remains the initially evaluated run ledger. The clean-recheck series separately evaluates the preserved E007 very-hard workspaces after copying the frozen evaluator directories and deleting generated Python cache files from the staged copies. Agent workspaces, code changes, and session results were not rerun or altered. Cases outside the affected very-hard tier retain their E007 result. The individual clean outcomes are provided in `data/e007_clean_rechecked_case_outcomes.csv`.

Effort comparisons are paired by case because every effort ran on each of the same 30 cases. Aggregate rates, difficulty-specific rates, transitions, and resource telemetry are descriptive. Existing E007 statistical analyses are retained in the source report; no additional significance testing was introduced for publication.

## E008: targeted repeated trials

E008 compared original results with the clean-rechecked E007 outcomes, then selected only unresolved case/effort disagreements. Nine cases contributed 11 condition cells. Each selected cell was run three times, for 33 new sessions. The process did not repeat the complete benchmark. Three repetitions are reported individually; a condition is described as unanimous if all three outcomes agree and mixed otherwise.

Each five-observation sequence is ordered: original execution, E007 clean recheck, E008 repetition 1, repetition 2, repetition 3. These observations are repeated measurements of the same selected task condition. They are not independent benchmark tasks. The five-outcome totals and the 33-repeat totals are descriptive and are not generalized to the full case set.

## Telemetry and data construction

Agent session counts, outcomes, suite results, steps, durations, and token counts are extracted from the saved machine records. The public E007 run table omits raw session exports, provider session names, commands, host paths, prompt hashes, and private trace content. E008 run data similarly omits private paths, run commands, session IDs, exports, and traces. Cost fields are represented as unknown because no billing evidence was available.

Durations are shown only when present in source records. E007's High effort has one missing wrapper duration, so duration summaries use n=29; Medium and Max use n=30. No duration is imputed. Token counts are provider/session counters and must not be interpreted as dollar costs. Heuristic trace metrics are identified as heuristics in the original analysis and are not claims about hidden reasoning.

## Source artifacts

- E007 execution and original scores: `docs/E007-PROTOCOL.md`, `docs/E007-PREREGISTRATION.md`, and source `E007-RESULTS.json` / `E007-RUNS.jsonl`.
- Evaluator correction and recheck: `docs/E008-EVALUATOR-RECHECK.md` and source `E008-E007-EVALUATOR-RECHECK.json` / `.jsonl`.
- Original-to-clean comparison: `data/case_level_replication.csv`, built from `E008-REPLICATION-MATRIX.json` and joined to the preserved E007 ledger.
- Targeted repeats: `data/e008_targeted_runs_sanitized.csv` and `data/five_observation_sequences.csv`, built from the E008 ledger and stability record.
