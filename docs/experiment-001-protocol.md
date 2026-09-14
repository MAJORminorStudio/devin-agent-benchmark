# Experiment 001 frozen protocol

## Question and design

Experiment 001 is an exploratory paired evaluation of how SWE-2 effort affects
autonomous repair of real OSS bugs with known ground truth:

```text
5 BugsInPy cases × 2 conditions = 10 independent runs
M = swe-2-medium
X = swe-2-max
```

The complete case and run records are in
`manifests/experiment-001.json` and `manifests/experiment-001-runs.json`.
Run IDs are immutable and every run starts from a fresh exporter output. No
conversation, workspace, patch, branch, output, or context is reused.

The frozen balanced interleaved order is:

1. E001-C03-M
2. E001-C01-X
3. E001-C05-M
4. E001-C02-X
5. E001-C04-M
6. E001-C03-X
7. E001-C01-M
8. E001-C05-X
9. E001-C02-M
10. E001-C04-X

Do not reorder or retry a failed run after execution begins.

## CLI and billing evidence

The inspected CLI is Devin `3000.10.21 (611c1cba)`. `devin models list`
exposes `swe-2-medium` and `swe-2-max`, and labels both `[Free]`. The account
reports Devin Pro. This does not independently establish promotional duration,
quota, or account billing terms, so the runner requires both
`--execute` and `--confirm-paid` for every real invocation.

Fusion is excluded by exact model-ID validation. No separate Fusion-off flag
was exposed by the CLI.

## Local execution

The CLI operates against a local directory through its positional workspace
argument and noninteractive `--print` mode. The unavailable private GitHub
case repository is therefore not required for Experiment 001. Use a fresh
sanitized local export from `/Volumes/Research/devin-agent-benchmark-e001-work`
or regenerate one with `scripts/export_case.py`.

The exact command that would launch frozen run #1 is:

```sh
python3 scripts/devin_runner.py \
  --run-id E001-C03-M \
  --runs-manifest manifests/experiment-001-runs.json \
  --workspace /Volumes/Research/devin-agent-benchmark-e001-work/E001-C03-M \
  --output-dir results/runs/experiment-001/E001-C03-M \
  --execute --confirm-paid
```

This command is recorded for the human checkpoint only and was not executed.
Without those final two flags the runner writes a dry-run plan and never calls
Devin.

## Intervention and scoring rules

There are zero substantive interventions. Only unrelated authentication,
environment, or harness recovery is allowed; every allowed intervention is
logged. No debugging hints, file hints, implementation suggestions, failure
explanations, or patch critiques may be sent to Devin.

`TASK_SUCCESS` is 1 only if held-out evaluation confirms the target repair and
required regression/public tests pass. The evaluator also records hidden tests,
public tests, regressions, elapsed time, observable steps, changed files, line
counts, patch size, interventions, identifiers, usage/cost/ACUs, termination
reason, patch, and evaluator notes. Reference-patch comparison is allowed only
after both conditions for a case are closed and is never returned to Devin.

## Held-out evaluator freeze

Before any Devin execution, evaluator-only held-out suites were added for all
five frozen cases. They live under `evaluation/experiment-001/` and are never
copied into sanitized workspaces. Each suite was validated against the
existing Phase 1 buggy and fixed verification trees in a pinned external
environment, with the buggy side failing for the target behavior and the
fixed side passing. Each case also has a small frozen regression subset. The
case selection, task prompts, conditions, run order, intervention policy,
experimental question, and scoring definition are unchanged.

The evaluator runs the held-out suite after the Devin session is closed and
requires all held-out, public, and configured regression checks to pass for
`TASK_SUCCESS`. Missing or unusable evaluator infrastructure is represented as
`EVALUATION_ERROR` rather than a task failure. See
`docs/experiment-001-heldout-evaluation.md` for validation evidence and the
case-by-case limitations.

`scripts/analyze_results.py` reports Medium solved X/5, Max solved X/5, paired
outcomes, case-level results, and condition-level efficiency summaries. It
makes no statistical-significance claims.
