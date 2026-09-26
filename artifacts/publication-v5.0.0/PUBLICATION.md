# Replication, evaluator hygiene, and run-to-run stability in a 123-session SWE-2 benchmark

## Abstract

We began by asking how Devin SWE-2 reasoning effort related to software-repair success across 30 frozen benchmark cases. E007 executed Medium, High, and Max once per case: 90 agent sessions in total. Its historical evaluator totals were 16/30, 18/30, and 18/30. E008 later found that stale Python bytecode in evaluator staging caused pytest collection errors on some very-hard E007 cases. Clean re-evaluation of the preserved E007 workspaces corrected 18 of the 90 recorded outcomes, six at each effort level, without rerunning Devin. The clean recheck totals were 22/30, 24/30, and 24/30; these are corrected evaluations of existing sessions, not 90 new sessions and not replacements for the historical record.

The clean recheck still disagreed with the original benchmark on individual cases. Medium agreed on 24/30 cases and Max on 25/30. We selected the nine cases with remaining disagreements, comprising 11 case/effort conditions, and ran three new trials for each. All 33 planned sessions produced valid final evaluations; 19 passed. Across the 11 selected five-observation sequences—original, E007 clean recheck, and three E008 trials—30 of 55 observations passed. These selected observations are not a new 55-case benchmark. Six conditions were unanimous across the three new trials and five were mixed.

The evidence supports a narrow conclusion: this benchmark showed case-level outcome changes across executions, and evaluator hygiene materially changed reported results. It does not establish that one effort setting is generally more reliable, or whether the remaining run-to-run variation reflects stochastic behavior or temporal/backend change.

## How the question changed

E007 was designed to test the effect of reasoning effort: do Medium, High, and Max produce different success patterns as repair tasks become harder? The first 90 runs produced a small aggregate separation: Medium recorded 16/30 solves, while High and Max each recorded 18/30. The tier table showed 2/10 very-hard solves at every effort level.

When E008 compared those outcomes with prior runs, the very-hard evaluator results raised a methodological question. E007's preserved workspaces and evaluator logs allowed us to investigate evaluation separately from agent execution. That investigation found stale `.pyc` artifacts that carried an evaluator source-host path into a different staging location. Pytest could not collect tests in some staged environments; those collection errors had initially been counted as task failures. We copied the frozen evaluator inputs, removed generated cache files only in the copies, and evaluated the existing workspaces again. Clean re-evaluation of the preserved E007 workspaces corrected 18 of the 90 recorded outcomes, six at each effort level, without rerunning Devin. Historical E007 totals remain 16/30, 18/30, and 18/30; the subsequent clean recheck is 22/30, 24/30, and 24/30. Historical tier outcomes were 7/10, 8/10, 8/10 at moderate; 7/10, 8/10, 8/10 at hard; and 2/10 for every effort at very-hard. After clean recheck, very-hard results were 8/10 at all effort levels.

The correction changed the size of the original-to-E007 aggregate gap, but aggregate totals did not answer whether the same repairs succeeded. The original aggregate was 24/30 for Medium and 23/30 for Max; clean E007 was 22/30 and 24/30. Original-to-clean-E007 agreement was 24/30 for Medium and 25/30 for Max. For Medium, 20 cases were stable solves, four stable failures, four original-only solves, and two clean-E007-only solves. For Max, the corresponding counts were 21, four, two, and three. E008's existing exact McNemar p-values were 0.6875 for Medium and 1.0000 for Max, with Wilson 95% agreement intervals of 62.7%–90.5% and 66.4%–92.7%. These paired analyses are for the same fixed 30 cases; no additional tests were introduced. A close aggregate count can coexist with different case outcomes.

Rather than rerunning all 30 tasks at every effort, E008 isolated the nine cases that still disagreed and the 11 case/effort cells involved. Three new sessions were run per selected condition. The five observations are presented condition by condition in Figure 5 and `data/five_observation_sequences.csv`. Five of the eleven new three-trial sequences were mixed; six were unanimous. This is evidence of observed variation in this selected benchmark sample, not a general reliability estimate.

## Results

### Effort-level outcomes

The E007 clean recheck scored Medium 22/30, High 24/30, and Max 24/30. By difficulty tier, Medium scored 7/10 moderate, 7/10 hard, and 8/10 very-hard; High scored 8/10, 8/10, and 8/10; Max scored 8/10, 8/10, and 8/10. Each tier contains ten fixed cases. High and Max had identical clean-recheck aggregate scores. Medium was two cases below both. These are descriptive outcomes from one session per cell; they do not establish an optimal setting or an inherent reliability difference.

Across the 30 paired cases in the E007 execution, effort transitions were limited: Medium-to-High changed two failures to passes and no passes to failures; High-to-Max changed one failure to a pass and one pass to a failure. Only E004-N03 was solved exclusively by one effort in E007, by Max. More detail on paired outcomes, steps, tokens, and observed duration is included in the machine-readable tables and figures. One High run lacks wrapper timing metadata; its duration is excluded, leaving n=29 for High timing and n=30 for Medium and Max. We do not impute the missing time. Monetary cost is unknown.

### Replication and targeted repeats

The original-to-clean-E007 case agreement was 80.0% (24/30) for Medium and 83.3% (25/30) for Max. Agreement and aggregate solve rate answer different questions: agreement measures whether the same cases had the same binary outcome, while solve rate counts passes within one set of 30 case executions.

E008 targeted repeats yielded 19/33 passes. This denominator is 33 sessions on 11 selected case/effort conditions, with three runs per condition; it is not 33 independent benchmark tasks. The combined 30/55 pass count is descriptive across five recorded observations on those same 11 selected conditions, not a benchmark-wide success rate. The selected sample was defined by prior disagreement, so neither figure estimates performance on all 30 cases.

### What telemetry can and cannot show

The E007 observations show that effort settings differed in measured session steps and token use, and observed wall time increased across the effort labels in the aggregate. These are descriptive telemetry summaries, not evidence that additional reasoning caused a success change. A missing wrapper record limits High duration to 29 observed runs. Session token counters are not billing records; actual monetary costs are unknown. The trace-derived behavior metrics use a heuristic parser and do not expose private planning or cognition.

## Interpretation

Two methodological findings now qualify the original effort comparison. First, stale evaluator cache artifacts materially affected recorded E007 outcomes, especially on the very-hard tier. Second, even after clean evaluation, case-level outcomes were not perfectly reproduced, and some selected conditions continued to vary across new trials. The repeated observations cannot distinguish ordinary stochastic agent behavior from changes in an unavailable provider backend or deployment revision.

The results do not show that High is optimal, that Max is worse than High, that Medium is more reliable, that more reasoning does not help, or that software-agent benchmarks are invalid. They show that in this benchmark the evaluator environment affected scores and single-run outcomes on some cases did not reproduce consistently. That is a reason to preserve workspaces, separate execution from evaluation, clean evaluator staging, retain machine-readable outputs, distinguish infrastructure failures from task failures, publish case-level results, and use repeats when disagreements merit investigation. This study does not imply that every task in every benchmark requires five trials.

## Reproducibility and sources

The release retains the frozen E007 preregistration/protocol, E008 protocol and comparability audit, evaluator-recheck documentation, targeted rerun plan, sanitized session-level tables, case-level replication matrix, five-observation table, and selected charts. The package's `data/` files were built from E007's machine-readable results and run ledger and E008's machine-readable recheck, replication, and stability records. The original source trees remain unmodified.

### Claim-to-source map

- E007 historical scores and difficulty results: `data/e007_runs_sanitized.csv`, `data/publication_summary.json`, and `docs/E007-REPORT-HISTORICAL.md`.
- Clean E007 totals and difficulty outcomes: `data/e007_clean_rechecked_case_outcomes.csv`; evaluator-staging defect and procedure: `docs/E008-EVALUATOR-RECHECK.md` and `docs/E008-COMPARABILITY-AUDIT.md`.
- Original-to-clean case agreement and stable/directional transitions: `data/case_level_replication.csv` and `data/publication_summary.json`.
- E008 selection rationale and count: `data/e008_sanitized_manifest.json` and `docs/E008-RERUN-PLAN.md`.
- New-run outcomes, suite statuses, and telemetry: `data/e008_targeted_runs_sanitized.csv` and `docs/E008-STABILITY-ANALYSIS.md`.
- Five-observation sequences and repeat-consistency labels: `data/five_observation_sequences.csv`.
- Historical budget assumptions versus actual-cost evidence: the frozen E007 preregistration and E008 execution record say the actual direct cost is unknown; see the contextual notes at the top of the public E007 protocol/preregistration copies and `data/publication_summary.json`.
- Limits on attributing residual variation to stochastic behavior or backend change: `LIMITATIONS.md` and `docs/E008-STABILITY-ANALYSIS.md`.

The counted total of 123 refers only to 90 E007 agent sessions plus 33 E008 agent sessions. E008's clean re-evaluations are not agent sessions and are not included in that total.
