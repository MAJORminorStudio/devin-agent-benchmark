# Experiment 005 Protocol

Status: frozen and validated; no Devin or SWE-2 run has started.

## Primary question

> How do SWE-2 Medium and Max compare when newly constructed, withheld
> software-repair tasks are intentionally pushed beyond the difficulty of the
> earlier benchmark cases?

This is a paired stress test of five new cases. Each case is run once with
`swe-2-medium` and once with `swe-2-max`; Fusion is excluded. E001-E004
canonical evidence and E004 staging are outside this experiment's write scope.

## Design and intervention policy

The ten runs use byte-identical prompts and fresh sanitized buggy workspaces
within each pair. There is no substantive human or Codex assistance and no
retry for an ordinary agent failure. The session is closed before evaluator
files or results are accessed.

`TASK_SUCCESS` is frozen as public + held-out behavioral + regression passing.
The five instances are newly constructed, deterministic, local Python
projects. Their source, fixes, tests, evaluator, and construction metadata are
kept in E005-specific private staging.

## Resource and termination policy

Each run has a 5,400-second wall-clock ceiling. This is 50% longer than the
3,600-second E002/E003 ceiling and comfortably exceeds E002's longest observed
1,380.464-second run. Devin exits terminate the run normally. A watchdog or
service timeout is infrastructure-only when the harness or service is at
fault; an agent that reaches the ceiling is an agent outcome. There are no
in-run retries and runs are sequential (`parallel_runs = 1`).

The existing Devin runner does not expose a stable agent step or token limit,
so those fields remain null. Observable steps, tool calls, tokens, usage, cost,
ACUs, timestamps, output, termination reason, patch, churn, and evaluator
status are captured when available.

## Frozen run order

`manifests/experiment-005-runs.json` records Python `random.Random.shuffle`
with seed `20260917`:

| # | Run | Condition | Model |
|---:|---|---|---|
| 1 | E005-H04-M | M | swe-2-medium |
| 2 | E005-H03-X | X | swe-2-max |
| 3 | E005-H02-X | X | swe-2-max |
| 4 | E005-H01-M | M | swe-2-medium |
| 5 | E005-H01-X | X | swe-2-max |
| 6 | E005-H04-X | X | swe-2-max |
| 7 | E005-H05-M | M | swe-2-medium |
| 8 | E005-H03-M | M | swe-2-medium |
| 9 | E005-H02-M | M | swe-2-medium |
| 10 | E005-H05-X | X | swe-2-max |

## Pre-freeze gates

Before any future execution, the private validator must remain green for
buggy/fixed behavior, deterministic repeats, leak audits, source/fixed tree
hashes, and reference patch hashes. The public repository must pass its test
suite, `git diff --check`, and security/privacy review. Any change to case
content, prompts, evaluator, configuration, isolation, or run order invalidates
the freeze and requires a new freeze record.

No execution is part of this protocol. After this freeze, stop until a
separately authorized launch.
