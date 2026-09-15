# Experiment 003 Protocol

Status: frozen and validated; no Devin run has started.

## Question

The primary question is:

> Does the Medium-versus-Max reasoning-effort pattern observed on five historical BugsInPy repairs replicate on five newly constructed software defects that were withheld from Devin before execution?

This is a paired replication on five new cases, not a replacement or reinterpretation of E001 or E002.

## Design

Five compact, deterministic Python maintenance projects are evaluated once
with SWE-2 Medium and once with SWE-2 Max. The cases cover filesystem/path
semantics, stateful cache invalidation, nested data transformation,
asynchronous lifecycle behavior, and a protocol/parser state machine. Each
pair uses the same byte-identical prompt, case source, visible tests, and
execution configuration. The interleaved order and seed are frozen in
`manifests/experiment-003-runs.json`.

The agent receives only a sanitized copy of the buggy project and its visible
test. Fixed source, reference patches, held-out tests, evaluator metadata,
other runs, and control-repository history remain outside its workspace.

## Conditions and intervention policy

- Medium: `swe-2-medium`.
- Max: `swe-2-max`.
- Fusion is disabled.
- There is no substantive human or Codex assistance.
- Ordinary agent failures are retained as results; retries are not allowed.
- The session is closed before evaluator-side files or results are accessed.

The execution boundary inherits E002: disposable Linux/arm64 Docker, effective
Bypass only inside the container, read-only root, dropped capabilities,
no-new-privileges, no Docker socket, no host or control-repository mounts, one
workspace, minimum Devin credentials, and restricted Devin-service egress.

## Resource limits and capture

The per-run wall-clock ceiling is 3,600 seconds. This is deliberately broad
relative to E002's observed runs, including Max runs over 1,000 seconds. There
is no frozen agent step or token limit because the existing Devin interface
does not expose a stable controllable limit in this harness. When available,
the runner records steps, tool calls, prompt/completion tokens, usage, cost,
and ACUs, alongside timestamps, raw output, session export, termination reason,
patch, source/generated churn, and evaluator output.

## Evaluation and scoring

Each case contains one visible failing test and evaluator-side behavioral tests
covering the target contract plus an adjacent regression check. The evaluator
runs after session closure:

1. visible/public test;
2. held-out behavioral test unavailable to the agent;
3. practical regression subset.

`TASK_SUCCESS = 1` only when all three pass. An evaluator infrastructure
failure is `EVALUATION_ERROR`, not an agent failure and not a silent fail.
The eventual analysis will report E003 separately, followed by a descriptive
E002+E003 analysis over ten unique cases. No post-hoc metric or scoring change
is permitted.

## Novelty and embargo

The defensible novelty claim is limited to this: the E003 benchmark instances,
defect implementations, prompts, reference fixes, and held-out behavioral
evaluations were newly constructed for this experiment and withheld from Devin
until the protocol was frozen and execution began. The absence of training-data
exposure cannot be proved and is not claimed.

Private case material stays outside the public repository until all ten runs
are closed. The public freeze manifest records hashes and configuration, not
source, fixes, evaluator contents, or solution metadata.

## Frozen artifacts

- `manifests/experiment-003-config.json`
- `manifests/experiment-003-runs.json`
- `manifests/experiment-003-freeze.json`
- `docs/experiment-003-novelty-and-provenance.md`
- `docs/experiment-003-case-design.md`
- `docs/experiment-003-evaluation-plan.md`
- `docs/experiment-003-isolation.md`

No Devin invocation is part of this freeze task.
