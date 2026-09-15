# Experiment 001 evaluator infrastructure correction

This document records the evaluator provisioning incident before Experiment
001 resumed. It does not change the frozen experiment question, cases,
prompts, model assignments, run order, held-out semantics, scoring rule, or
intervention policy.

## Incident

The first `E001-C03-M` Devin session was valid and completed in 27.138 seconds.
Its preserved workspace, session export, runner record, and empty agent patch
are canonical. The original evaluator invocation was invalid because it used
the host Python: `pytest` was unavailable and `six` was not installed. No
held-out test actually ran, so that evaluation is retained only as
`evaluation-result.infrastructure-error.json` and is not an agent failure.

The corrected evaluator uses one external virtual environment per case. The
environment root is outside this control repository and outside all Devin
workspaces:

```text
/Volumes/Research/devin-agent-benchmark-evaluator-envs/experiment-001
```

Provisioning is reproducible with:

```text
python3 scripts/provision_evaluator_envs.py \
  --env-root /Volumes/Research/devin-agent-benchmark-evaluator-envs/experiment-001 \
  --force
```

Each environment records its exact requested Python version, resolved Python
version, direct frozen install pins, provisioning commands, installation
output, and `uv pip freeze` output in an external `.evaluator-environment.json`
record. The evaluator prepends only the selected case environment to `PATH`,
sets `VIRTUAL_ENV`, and adds the selected source tree to `PYTHONPATH`.

## Environment specifications and preflight

| Case | Evaluator Python | Direct evaluator pins | Buggy public / held-out / regression | Fixed public / held-out / regression |
|---|---|---|---|---|
| Black 16 | 3.8.20 | appdirs 1.4.3, attrs 19.3.0, click 7.0, pathspec 0.7.0, regex 2020.2.20, toml 0.10.0, typed-ast 1.4.0, pytest 5.4.3 | fail / fail / pass | pass / pass / pass |
| FastAPI 3 | 3.8.20 | FastAPI 0.55.1, Pydantic 1.5.1, Starlette 0.13.2, requests 2.23.0, pytest 5.4.3, typing-extensions 3.7.4.2, uvicorn 0.11.5 | fail / fail / pass | pass / pass / pass |
| Scrapy 3 | 3.8.20 | Scrapy 2.1.0, pytest 5.4.2, six 1.15.0, testfixtures 6.14.1 | fail / fail / pass | pass / pass / pass |
| tqdm 5 | 3.8.20 | pytest 5.4.3, nose 1.3.7, six 1.15.0 | fail / fail / pass | pass / pass / pass |
| Tornado 13 | 3.9.25 | none; source is selected through `PYTHONPATH` | fail / fail / pass | pass / pass / pass |

The full command and output record is evaluator-only at
`evaluation/experiment-001/preflight.json`. It was produced with:

```text
python3 scripts/evaluator_preflight.py \
  --env-root /Volumes/Research/devin-agent-benchmark-evaluator-envs/experiment-001 \
  --output evaluation/experiment-001/preflight.json
```

Every case passed readiness, reproduced its intended buggy public and held-out
failure, passed the held-out suite on the fixed tree, and passed the frozen
regression subset on both trees.

## Corrected evaluation of E001-C03-M

The existing Scrapy Medium workspace was evaluated after provisioning, with
no Devin invocation. The exact preserved agent patch was used; it is empty
and the agent changed no source files.

| Field | Corrected result |
|---|---|
| Devin run | valid, completed, 27.138 seconds |
| Public test | fail on the preserved buggy workspace |
| Held-out test | fail |
| Regression suite | pass |
| `TASK_SUCCESS` | false |
| Evaluation status | `OK` |
| Patch | empty; 0 additions, 0 deletions |

The original invalid evaluator result remains preserved as
`results/runs/experiment-001/E001-C03-M/evaluation-result.infrastructure-error.json`.
The corrected result is
`results/runs/experiment-001/E001-C03-M/evaluation-result.json`.

Evaluator-generated Python caches were removed from the preserved workspace
after scoring so they cannot be mistaken for agent changes. The original Devin
session was not rerun.

## Fail-fast protection and resume point

`scripts/devin_runner.py` now requires `--evaluator-env-root` for a real frozen
invocation and checks the exact case environment, Python version, environment
record digest, and all command tools before starting Devin. Missing evaluator
dependencies therefore stop before any future Devin session exists.

`scripts/evaluate_run.py` requires the same external environment root for
frozen cases and uses that environment for public, held-out, and regression
commands. Synthetic cases without held-out suites retain their existing host
environment behavior.

No agent-visible workspace, prompt, case, model, run order, held-out test, or
scoring content was changed. Subject to the final leak and security checks,
the next permitted experiment point is `E001-C01-X`; this correction stops
before invoking it.
