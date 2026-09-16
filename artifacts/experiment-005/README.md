# Experiment 005 public artifacts

Experiment 005 is the balanced HARD-tier paired execution: five historical/public BugsInPy defects and five newly constructed withheld defects, each run once with SWE-2 Medium and once with SWE-2 Max in the frozen interleaved order.

The public derivatives include sanitized prompts, source patches, evaluator statuses, observable tool timelines, session summaries, sanitized session exports with hidden reasoning omitted, stdout/stderr, run metadata, workspace-change summaries, and per-run SHA-256 hashes. Private evaluator source, reference fixes, credentials, raw machine paths, hidden reasoning, and full workspaces are excluded.

Medium scored 7/10 and Max scored 6/10. Paired outcomes were 5 both-success, 2 Medium-only, 1 Max-only, and 2 both-fail. See [`reports/experiment-005-results.md`](../../reports/experiment-005-results.md) and [`results/experiment-005-summary.json`](../../results/experiment-005-summary.json).

The complete sanitized record-level ledger is [`results/experiment-005-ledger.json`](../../results/experiment-005-ledger.json); paired rows are [`results/experiment-005-paired.csv`](../../results/experiment-005-paired.csv). The frozen protocol and manifests remain in [`docs/experiment-005-protocol.md`](../../docs/experiment-005-protocol.md), [`manifests/experiment-005-config.json`](../../manifests/experiment-005-config.json), [`manifests/experiment-005-runs.json`](../../manifests/experiment-005-runs.json), and [`manifests/experiment-005-freeze.json`](../../manifests/experiment-005-freeze.json).
