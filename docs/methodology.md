# Methodology

## Scope and isolation

This is a standalone Phase 1 benchmark harness. It does not read, modify,
import from, or connect to Major Minor research databases, Obsidian vaults,
Supabase projects, research pipelines, or production repositories. The only
external source in scope is the public BugsInPy Git repository named in
[sources/bugsinpy.json](../sources/bugsinpy.json).

BugsInPy is kept as an external checkout. The harness requires its path to be
outside this repository and reads only project metadata and source revisions
needed for a selected case. It never vendors the dataset into this repository.

## Case lifecycle

The intended lifecycle is:

```text
external BugsInPy metadata
        |
        v
clone original OSS project -> archive buggy revision -> overlay regression tests
        |                                      |
        |                                      +--> agent-workspace (no .git history)
        v
archive fixed revision -> verification/fixed (evaluator-only)
        |
        v
run expected failing and expected passing commands -> reproducibility.json
```

`manifests/experiment-001.json` is evaluator-only ground truth. It includes the
buggy and fixed commits, expected outcomes, and standardized task prompts. The
agent workspace is made from a buggy commit archive, not a Git clone, so the
agent cannot inspect later commits or the reference patch through `.git`.
Only the regression-test files listed by BugsInPy are overlaid from the fixed
revision. `bug_patch.txt`, `bug_buggy.txt`, `bug_fixed.txt`, `bug.info`, and all
other evaluator metadata stay outside `agent-workspace/`.

The preparation script audits the agent workspace for Git history, forbidden
artifact names, and the fixed commit hash. It fails closed if any are present.

## Reproduction protocol

1. Fetch the pinned BugsInPy dataset into a dedicated external directory.
2. Survey candidate metadata without modifying the benchmark repository.
3. Prepare a selected case into a fresh run root.
4. Run the buggy verification workspace and confirm the expected failure.
5. Run the fixed verification workspace separately and confirm the expected pass.
6. Preserve the resulting command output and status in `reproducibility.json`.
7. Give only `agent-workspace/` plus the standardized task prompt to Devin in a
   future phase.
8. Capture Devin's patch and run evaluator-controlled tests in a separate
   environment. The human/reference patch is never shown to Devin.

The harness does not install dependencies implicitly. Environment creation
belongs in a disposable, case-specific runner (for example a pinned Python
container or virtual environment) and should be recorded with the result.
This prevents a reproduction attempt from changing the host Python environment.

## Future results schema

Future agent runs should append records shaped like:

```json
{
  "experiment_id": "experiment-001",
  "case_id": "black-16",
  "agent": {
    "name": "Devin",
    "configuration": "",
    "model": "",
    "subscription_or_usage": {"available": false, "amount": null, "currency": null}
  },
  "prompt": "",
  "started_at": "",
  "ended_at": "",
  "elapsed_seconds": null,
  "interventions": [],
  "patch": {"format": "unified-diff", "path": "", "sha256": ""},
  "tests_before": {"command": "", "status": ""},
  "tests_after": {"command": "", "status": ""},
  "pass": null,
  "regression_status": "not-run",
  "evaluator_notes": ""
}
```

Cost and usage fields are nullable because availability depends on the future
agent interface. No Devin integration is part of Phase 1.
