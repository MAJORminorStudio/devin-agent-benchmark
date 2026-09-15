# Devin bug evaluation harness

A small, reproducible harness for evaluating autonomous coding agents on real Python bugs from [BugsInPy](https://github.com/reproducing-research-projects/BugsInPy).

This repository is intentionally isolated from the Major Minor research infrastructure. It has no database, Obsidian, Supabase, pipeline, or production repository integration. BugsInPy is referenced as an external source checkout; its repository is not vendored here.

## Published experiment results

The five-case × two-condition protocol and its isolated execution design are
documented and frozen. Experiment 001 is retained as invalid capability
provenance because noninteractive permission gating produced empty patches;
Experiment 002 is the completed autonomous result. The primary reports and
sanitized public artifacts are linked here:

- [Experiment 001 report](reports/experiment-001-results.md) — invalid capability comparison
- [Experiment 002 report](reports/experiment-002-results.md) — completed 5×2 evaluation
- [Experiment 002 forensic analysis](reports/experiment-002-forensic-analysis.md) — observable tool behavior, source-only patch metrics, and paired analysis
- [Experiment 001 public artifacts](artifacts/experiment-001/README.md)
- [Experiment 002 public artifacts](artifacts/experiment-002/README.md)

The Devin runner remains dry-run by default. No Experiment 003 has been
started. See [docs/candidate-bugs.md](docs/candidate-bugs.md),
[docs/methodology.md](docs/methodology.md),
[docs/devin-cli-integration.md](docs/devin-cli-integration.md), and
[docs/experiment-002-protocol.md](docs/experiment-002-protocol.md) for the
method and isolation boundary.

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

After a validated run root exists, export an agent-only workspace to a
directory outside this control repository. The external BugsInPy checkout is
required for the reference-aware leak audit:

```sh
python3 scripts/export_case.py \
  --manifest manifests/experiment-001.json \
  --case-id black-16 \
  --run-root results/runs/phase-1/black-16 \
  --source-dir /tmp/bugsinpy-source \
  --destination /tmp/devin-case-black-16
```

The exporter also writes evaluator-only baseline/audit sidecars next to the
destination. A Devin plan can be inspected without invoking Devin:

```sh
python3 scripts/devin_runner.py \
  --run-id E001-C03-M \
  --workspace /tmp/devin-case-E001-C03-M \
  --output-dir results/runs/experiment-001/E001-C03-M
```

The `--execute --confirm-paid` flags are both required for a real invocation.
Do not use them until the human subscription/credit checkpoint is approved.

The sanitized case workspaces are packaged separately from this control
repository. The requested GitHub organization repository could not be created
with the authenticated account because it lacks organization repository-create
permission; the case package is retained in a separate local external
directory until that permission is available.

The committed manifest contains reference commits and expected outcomes for reproduction. It must remain outside any future Devin workspace.
