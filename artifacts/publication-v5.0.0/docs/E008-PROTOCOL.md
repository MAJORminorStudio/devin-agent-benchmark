# E008 Protocol

E008 is a replication-drift and stability analysis of the frozen 30-case MAJOR//minor Devin SWE-2 benchmark. The primary analysis compares the historical SWE-2 Medium/Max runs with the E007 Medium/Max runs. The historical experiment and E007 records remain immutable.

## Frozen analysis sequence

1. Audit task, prompt, test, evaluator, score, model, runtime, permission, isolation, and date comparability.
2. Recompute the case-level original-versus-E007 matrix from publication-v4 machine records and E007 run records.
3. Report overall and difficulty-stratified exact agreement, outcome transitions, exact McNemar tests, and confidence intervals for agreement.
4. Inspect original and E007 evidence for every discordant case.
5. Harmonize failure types only to the level supported by evaluator evidence.
6. Compare telemetry only for common complete fields; label trace-derived counts heuristic.
7. Propose targeted repeat trials only for discordant case/effort cells.
8. Stop pending explicit user approval.

## Proposed repeat design

For each selected case/effort cell, add three independent runs, preserving the exact prompt, source snapshot, test suites, evaluator, selector, environment, isolation, and zero-intervention policy. Keep each observation separate. No stable case is selected. Before any run, verify live account/direct cost conditions and stop if projected new direct overage exceeds $50.

## Execution status

The user approved the frozen 33-slot manifest on 2026-09-26. Exactly 33 sessions were attempted across the approved 11 conditions, sequentially, with no replacements, no added conditions, and zero human interventions. The first nine E002 sessions initially hit an adapter field error before tests executed; their preserved workspaces were evaluated after adapter repair in sanitized copies, with the initial errors retained in `E008-RUNS.jsonl`. Slot 10’s completed result was recovered after a local serialization error; it was not rerun. All 33 final evaluations are valid. Actual cost is unknown because no billing evidence was exposed. See `E008-STABILITY-ANALYSIS.md` for outcomes and interpretation.
