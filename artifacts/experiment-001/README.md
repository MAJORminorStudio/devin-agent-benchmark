# Experiment 001 public artifacts

Experiment 001 is preserved here as important provenance, but is **INVALID AS A CAPABILITY COMPARISON**. It used noninteractive `accept-edits`; required tool calls were rejected, so all ten agent patches were empty. The corrected evaluator result for E001-C03-M and the original evaluator infrastructure error are both published.

Each run directory contains the frozen prompt, model/condition/timing metadata, exact permission warning, rejected or canceled tool-call records, sanitized session evidence, evaluator result, empty-patch proof, and SHA-256 hashes. System boilerplate and private machine paths are omitted or standardized; benchmark commands, source observations, failures, rejected calls, and outcomes are retained.

The unchanged raw records remain local under the ignored `results/runs/experiment-001/` directory because they contain machine-specific paths. Their hashes and public replacements are documented in every run's `artifact-hashes.json`.

Run order:

1. E001-C03-M
2. E001-C01-X
3. E001-C05-M
4. E001-C02-X
5. E001-C04-M
6. E001-C03-X
7. E001-C01-M
8. E001-C05-X
9. E001-C02-M
10. E001-C04-X

## Run evidence

Each run directory exposes the sanitized prompt, session export, observable
tool timeline, empty patch, evaluator result, and metadata. The rejected
tool-call records are retained as operational evidence.

| Run | Case / condition | Evidence |
|---|---|---|
| E001-C03-M | Scrapy 3 / Medium | [run metadata](E001-C03-M/run-metadata.json) · [prompt](E001-C03-M/prompt.md) · [session](E001-C03-M/devin-session-export.sanitized.json) · [timeline](E001-C03-M/tool-timeline.json) · [patch](E001-C03-M/agent.patch) · [evaluation](E001-C03-M/evaluation-result.json) |
| E001-C01-X | Black 16 / Max | [run metadata](E001-C01-X/run-metadata.json) · [prompt](E001-C01-X/prompt.md) · [session](E001-C01-X/devin-session-export.sanitized.json) · [timeline](E001-C01-X/tool-timeline.json) · [patch](E001-C01-X/agent.patch) · [evaluation](E001-C01-X/evaluation-result.json) |
| E001-C05-M | Tornado 13 / Medium | [run metadata](E001-C05-M/run-metadata.json) · [prompt](E001-C05-M/prompt.md) · [session](E001-C05-M/devin-session-export.sanitized.json) · [timeline](E001-C05-M/tool-timeline.json) · [patch](E001-C05-M/agent.patch) · [evaluation](E001-C05-M/evaluation-result.json) |
| E001-C02-X | FastAPI 3 / Max | [run metadata](E001-C02-X/run-metadata.json) · [prompt](E001-C02-X/prompt.md) · [session](E001-C02-X/devin-session-export.sanitized.json) · [timeline](E001-C02-X/tool-timeline.json) · [patch](E001-C02-X/agent.patch) · [evaluation](E001-C02-X/evaluation-result.json) |
| E001-C04-M | tqdm 5 / Medium | [run metadata](E001-C04-M/run-metadata.json) · [prompt](E001-C04-M/prompt.md) · [session](E001-C04-M/devin-session-export.sanitized.json) · [timeline](E001-C04-M/tool-timeline.json) · [patch](E001-C04-M/agent.patch) · [evaluation](E001-C04-M/evaluation-result.json) |
| E001-C03-X | Scrapy 3 / Max | [run metadata](E001-C03-X/run-metadata.json) · [prompt](E001-C03-X/prompt.md) · [session](E001-C03-X/devin-session-export.sanitized.json) · [timeline](E001-C03-X/tool-timeline.json) · [patch](E001-C03-X/agent.patch) · [evaluation](E001-C03-X/evaluation-result.json) |
| E001-C01-M | Black 16 / Medium | [run metadata](E001-C01-M/run-metadata.json) · [prompt](E001-C01-M/prompt.md) · [session](E001-C01-M/devin-session-export.sanitized.json) · [timeline](E001-C01-M/tool-timeline.json) · [patch](E001-C01-M/agent.patch) · [evaluation](E001-C01-M/evaluation-result.json) |
| E001-C05-X | Tornado 13 / Max | [run metadata](E001-C05-X/run-metadata.json) · [prompt](E001-C05-X/prompt.md) · [session](E001-C05-X/devin-session-export.sanitized.json) · [timeline](E001-C05-X/tool-timeline.json) · [patch](E001-C05-X/agent.patch) · [evaluation](E001-C05-X/evaluation-result.json) |
| E001-C02-M | FastAPI 3 / Medium | [run metadata](E001-C02-M/run-metadata.json) · [prompt](E001-C02-M/prompt.md) · [session](E001-C02-M/devin-session-export.sanitized.json) · [timeline](E001-C02-M/tool-timeline.json) · [patch](E001-C02-M/agent.patch) · [evaluation](E001-C02-M/evaluation-result.json) |
| E001-C04-X | tqdm 5 / Max | [run metadata](E001-C04-X/run-metadata.json) · [prompt](E001-C04-X/prompt.md) · [session](E001-C04-X/devin-session-export.sanitized.json) · [timeline](E001-C04-X/tool-timeline.json) · [patch](E001-C04-X/agent.patch) · [evaluation](E001-C04-X/evaluation-result.json) |

`artifact-hashes.json` in each directory documents the sanitized public
replacement and integrity status for the corresponding raw record.
