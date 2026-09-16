# Experiment 002 disposable container

Build the pinned Linux/arm64 Devin image from `Dockerfile`. The container
runner in `scripts/experiment_002_container.py` is plan-only unless both
`--execute` and `--confirm-paid` are supplied.

The image is not an E001 artifact and must never receive the control
repository or evaluator-only tests as a mount.
