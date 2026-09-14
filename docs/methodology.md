# Methodology

## Scope and isolation

This is a standalone benchmark harness. It does not read, modify,
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
artifact names, and the fixed commit hash. The Phase 2 exporter then copies
only that validated workspace into a destination outside the control
repository, adds `TASK.md`, `SETUP.md`, and a safe `CASE.json`, and fails closed
if the export contains fixed hashes, reference-patch fragments that were not
already in the buggy baseline, hidden-test names, ground-truth filenames,
control paths, escaping symlinks, or source/reference Git history. Its baseline,
audit report, and export record are evaluator-side siblings, never agent input.

The sanitized case repository is a separate packaging layer. Each immutable
`E001-C01` through `E001-C05` branch contains one case workspace at its root;
the control repository and the fixed verification tree are not remotes or
history in those branches. The requested private organization repository is
pending GitHub organization repository-create permission.

## Reproduction protocol

1. Fetch the pinned BugsInPy dataset into a dedicated external directory.
2. Survey candidate metadata without modifying the benchmark repository.
3. Prepare a selected case into a fresh run root.
4. Run the buggy verification workspace and confirm the expected failure.
5. Run the fixed verification workspace separately and confirm the expected pass.
6. Preserve the resulting command output and status in `reproducibility.json`.
7. Export one case and inspect its passing leak audit.
8. Give only the sanitized export plus its standardized task prompt to Devin
   in a future phase.
9. Capture Devin's patch and run public and evaluator-controlled tests in a
   separate environment. Hidden tests and the human/reference patch are never
   shown to Devin.

The harness does not install dependencies implicitly. Environment creation
belongs in a disposable, case-specific runner (for example a pinned Python
container or virtual environment) and should be recorded with the result.
This prevents a reproduction attempt from changing the host Python environment.

## Experiment 001 frozen runner and intervention policy

The runner uses the installed local CLI's inspected flags: exact
`--model swe-2-medium` or `--model swe-2-max`, `--print`, `--prompt-file`, `--export`,
`--permission-mode accept-edits`, and `--respect-workspace-trust false`.
Fusion is locked out by model-ID validation because this CLI exposes no
separate Fusion-off switch. The default runner operation writes a plan and
does not call Devin; a real call requires both `--execute` and
`--confirm-paid`. The CLI's model list currently labels both selected SWE-2
models `[Free]`, but promotional duration and account-side billing terms are
not independently verified.

The CLI accepts an isolated local workspace as its positional path, so the
unavailable private GitHub case repository is not required for Experiment 001.
Each run uses a fresh local exporter output and a run-specific ID from the
frozen interleaved order.

Experiment 001 allows zero substantive human interventions. Only unrelated
environment/authentication correction or harness recovery is permitted, and
every such event must be logged with timestamp, reason, and action. No one may
provide debugging hints, point to implementation files, suggest an approach,
explain failures, or explain why a patch is wrong.

The post-session evaluator records the public test result, optional hidden
evaluator result, changed files, patch hash, line counts, regression status,
and optional non-content reference metrics. It accepts hidden commands and a
reference patch only through evaluator-side paths after the session is closed.
The reference content is never copied into the agent workspace or result
notes.

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

Cost and usage fields are nullable because availability depends on the agent
interface. No Devin task was invoked during Phase 2 validation. The runner is
prepared for the explicitly approved future invocation, but provider fields
that the installed CLI does not expose—stable cloud IDs/URLs, usage/cost/ACUs,
branch, and PR URL—remain nullable/manual checkpoints.
