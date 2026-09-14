# Devin bug evaluation harness

A small, reproducible Phase 1 harness for evaluating autonomous coding agents on real Python bugs from [BugsInPy](https://github.com/reproducing-research-projects/BugsInPy).

This repository is intentionally isolated from the Major Minor research infrastructure. It has no database, Obsidian, Supabase, pipeline, or production repository integration. BugsInPy is referenced as an external source checkout; its repository is not vendored here.

## Phase 1 status

The infrastructure and candidate survey are complete. No Devin account, integration, subscription, or experiment has been configured. See [docs/candidate-bugs.md](docs/candidate-bugs.md), [docs/methodology.md](docs/methodology.md), and [reports/experiment-001-recommendation.md](reports/experiment-001-recommendation.md).

## Quick start

Use a dedicated external directory for the BugsInPy checkout. The harness rejects a source checkout located inside this repository.

```sh
SOURCE_DIR=/tmp/bugsinpy-source
python3 scripts/bugsinpy_harness.py fetch-source --source-dir "$SOURCE_DIR"
python3 scripts/bugsinpy_harness.py survey --source-dir "$SOURCE_DIR"
python3 scripts/bugsinpy_harness.py prepare --manifest manifests/experiment-001.json --case-id black-16 --source-dir "$SOURCE_DIR" --work-root results/runs/phase-1
```

Preparation creates `agent-workspace/` and separate `verification/buggy/` and `verification/fixed/` trees. Only the first is intended to be supplied to a future agent. Run verification with an environment that matches the manifest's Python version; the harness does not install dependencies implicitly.

```sh
python3 scripts/bugsinpy_harness.py verify --manifest manifests/experiment-001.json --case-id black-16 --run-root results/runs/phase-1/black-16 --side both
```

The committed manifest contains reference commits and expected outcomes for reproduction. It must remain outside any future Devin workspace.
