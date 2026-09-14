# Cases

Prepared case directories are runtime artifacts and should not be committed
here. The evaluator manifest is under `manifests/`; future agent workspaces are
created under a run root and are deliberately separate from fixed verification
trees.

Phase 2 exports belong in the separate private case repository, one immutable
branch per case. The exporter writes evaluator-only baseline and audit sidecars
outside the agent-visible directory; neither sidecar is part of a case branch.
