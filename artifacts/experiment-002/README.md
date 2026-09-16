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

## Run evidence

Each run directory exposes the sanitized prompt, session export, observable
tool timeline, patch, evaluator result, and metadata. Start from the run
directory, then follow the filenames listed below for a complete public audit.

| Run | Case / condition | Evidence |
|---|---|---|
| E002-C02-M | FastAPI 3 / Medium | [run metadata](E002-C02-M/run-metadata.json) · [prompt](E002-C02-M/prompt.md) · [session](E002-C02-M/devin-session-export.sanitized.json) · [timeline](E002-C02-M/tool-timeline.json) · [patch](E002-C02-M/agent.patch) · [evaluation](E002-C02-M/evaluation-result.json) |
| E002-C04-X | tqdm 5 / Max | [run metadata](E002-C04-X/run-metadata.json) · [prompt](E002-C04-X/prompt.md) · [session](E002-C04-X/devin-session-export.sanitized.json) · [timeline](E002-C04-X/tool-timeline.json) · [patch](E002-C04-X/agent.patch) · [evaluation](E002-C04-X/evaluation-result.json) |
| E002-C01-M | Black 16 / Medium | [run metadata](E002-C01-M/run-metadata.json) · [prompt](E002-C01-M/prompt.md) · [session](E002-C01-M/devin-session-export.sanitized.json) · [timeline](E002-C01-M/tool-timeline.json) · [patch](E002-C01-M/agent.patch) · [evaluation](E002-C01-M/evaluation-result.json) |
| E002-C05-X | Tornado 13 / Max | [run metadata](E002-C05-X/run-metadata.json) · [prompt](E002-C05-X/prompt.md) · [session](E002-C05-X/devin-session-export.sanitized.json) · [timeline](E002-C05-X/tool-timeline.json) · [patch](E002-C05-X/agent.patch) · [evaluation](E002-C05-X/evaluation-result.json) |
| E002-C03-M | Scrapy 3 / Medium | [run metadata](E002-C03-M/run-metadata.json) · [prompt](E002-C03-M/prompt.md) · [session](E002-C03-M/devin-session-export.sanitized.json) · [timeline](E002-C03-M/tool-timeline.json) · [patch](E002-C03-M/agent.patch) · [evaluation](E002-C03-M/evaluation-result.json) |
| E002-C01-X | Black 16 / Max | [run metadata](E002-C01-X/run-metadata.json) · [prompt](E002-C01-X/prompt.md) · [session](E002-C01-X/devin-session-export.sanitized.json) · [timeline](E002-C01-X/tool-timeline.json) · [patch](E002-C01-X/agent.patch) · [evaluation](E002-C01-X/evaluation-result.json) |
| E002-C04-M | tqdm 5 / Medium | [run metadata](E002-C04-M/run-metadata.json) · [prompt](E002-C04-M/prompt.md) · [session](E002-C04-M/devin-session-export.sanitized.json) · [timeline](E002-C04-M/tool-timeline.json) · [patch](E002-C04-M/agent.patch) · [evaluation](E002-C04-M/evaluation-result.json) |
| E002-C02-X | FastAPI 3 / Max | [run metadata](E002-C02-X/run-metadata.json) · [prompt](E002-C02-X/prompt.md) · [session](E002-C02-X/devin-session-export.sanitized.json) · [timeline](E002-C02-X/tool-timeline.json) · [patch](E002-C02-X/agent.patch) · [evaluation](E002-C02-X/evaluation-result.json) |
| E002-C05-M | Tornado 13 / Medium | [run metadata](E002-C05-M/run-metadata.json) · [prompt](E002-C05-M/prompt.md) · [session](E002-C05-M/devin-session-export.sanitized.json) · [timeline](E002-C05-M/tool-timeline.json) · [patch](E002-C05-M/agent.patch) · [evaluation](E002-C05-M/evaluation-result.json) |
| E002-C03-X | Scrapy 3 / Max | [run metadata](E002-C03-X/run-metadata.json) · [prompt](E002-C03-X/prompt.md) · [session](E002-C03-X/devin-session-export.sanitized.json) · [timeline](E002-C03-X/tool-timeline.json) · [patch](E002-C03-X/agent.patch) · [evaluation](E002-C03-X/evaluation-result.json) |

`artifact-hashes.json`, `source-diff-stat.json`, and
`workspace-change-summary.json` in each directory provide the integrity and
source-versus-generated-file metadata for that run.
