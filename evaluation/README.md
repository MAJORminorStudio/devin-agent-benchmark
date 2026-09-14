# Evaluation

This directory is reserved for evaluator-controlled tests and scoring logic.
Use `scripts/evaluate_run.py` after a session closes to capture the patch,
public-test result, optional hidden-test result, regression status, and
evaluator-only reference metrics. Hidden tests and the reference patch must be
passed through evaluator-side paths and are never copied into an agent
workspace. Future results must conform to [results.schema.json](results.schema.json);
all usage/cost fields remain nullable until the agent interface exposes them.

`scripts/smoke_test.py` exercises this path with a disposable toy case. It does
not invoke Devin or consume credits.
