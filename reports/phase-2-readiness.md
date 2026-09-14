# Experiment 001 Phase 2 readiness

Validated on 2026-09-14 without starting Devin or spending external credits.

## Built

- `scripts/export_case.py` creates an agent-only workspace from a validated
  Phase 1 run root.
- `scripts/devin_runner.py` builds the inspected local Devin CLI invocation,
  defaults to a no-call dry run, and requires `--execute --confirm-paid` for a
  real call.
- `scripts/evaluate_run.py` captures the agent patch, public tests, optional
  evaluator-side hidden tests, regression status, and non-content reference
  metrics after a session closes.
- `scripts/smoke_test.py` exercises export, audit, dry-run planning, hidden
  test isolation, patch capture, and evaluation with a disposable toy case.
- `manifests/experiment-001-config.json` freezes the case IDs, `swe-2-medium`,
  Fusion exclusion, local/noninteractive mode, and zero substantive
  intervention policy.

## Isolation validation

The five sanitized exports for E001-C01 through E001-C05 each passed the
reference-aware leak audit. The audit checks fixed hashes, reference-patch
fragments absent from the buggy baseline, hidden-test names, ground-truth
filenames, control-repository tokens, symlink targets, and Git history. The
export branches contain only the buggy source tree, public regression tests,
and safe task/setup metadata.

The local case package is `/Volumes/Research/devin-agent-benchmark-cases` with
branches `E001-C01` through `E001-C05`. Creation of the requested private
`MAJORminorStudio/devin-agent-benchmark-cases` repository was blocked by the
authenticated GitHub account's lack of organization repository-create
permission. No fallback public or personal repository was used.

## Readiness and remaining checkpoints

The smoke test passed with `devin_invoked: false`. The actual runner path is
ready but must stop for human confirmation of subscription/credit budget. The
installed CLI does not expose a general cloud task/handoff, stable session
URL, usage/cost/ACU report, repository branch option, or PR creation flag;
those remain manual/provider checkpoints. Before Experiment 001, resolve the
private case-repository permission and decide how the case-specific legacy
Python environments will be provisioned and recorded.
