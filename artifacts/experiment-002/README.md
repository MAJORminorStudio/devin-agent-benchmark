# Experiment 002 public artifacts

Experiment 002 is the isolated autonomous execution experiment. All ten frozen runs used the disposable linux/arm64 Docker path with dangerous permission mode / effective Bypass, read-only root, dropped capabilities, no-new-privileges, no Docker socket, no host/control-repository mounts, a single sanitized workspace, and the restricted egress proxy. Fusion was disabled and there were no substantive interventions or retries.

Each run directory publishes the frozen prompt, model/effort, session/timing metadata, sanitized tool timeline and session export, stdout/stderr, patch, evaluator result, source-only diff statistics, workspace-change classification, and hashes. The full generated workspaces and unchanged raw runner/session files remain local because they contain machine-specific paths or excessive dependency/bytecode data; exclusions and hashes are documented per run.

This experiment scored Medium 5/5 and Max 4/5. The sole failure was E002-C04-X (tqdm): public and regression checks passed, but the held-out sized-iterable behavior remained incorrect.

Run order:

1. E002-C02-M
2. E002-C04-X
3. E002-C01-M
4. E002-C05-X
5. E002-C03-M
6. E002-C01-X
7. E002-C04-M
8. E002-C02-X
9. E002-C05-M
10. E002-C03-X
