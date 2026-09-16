# Evaluation

This directory is reserved for evaluator-controlled tests and scoring logic.
Use `scripts/evaluate_run.py` after a session closes to capture the patch,
public-test result, optional hidden-test result, regression status, and
evaluator-only reference metrics. For frozen Experiment 001 cases, first
provision and preflight the external environments, then pass the same
`--env-root` to the evaluator:

```text
python3 scripts/provision_evaluator_envs.py \
  --env-root evaluator-envs/experiment-001
python3 scripts/evaluator_preflight.py \
  --env-root evaluator-envs/experiment-001
```

Hidden tests and the reference patch must be passed through evaluator-side
paths and are never copied into an agent workspace. Future results must
conform to [results.schema.json](results.schema.json); all usage/cost fields
remain nullable until the agent interface exposes them.

`scripts/smoke_test.py` exercises this path with a disposable toy case. It does
not invoke Devin or consume credits.
