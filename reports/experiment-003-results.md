# Experiment 003 Results

## Question

Does the Medium-versus-Max reasoning-effort pattern observed on five historical BugsInPy repairs replicate on five newly constructed software defects that were withheld from Devin before execution?

## Methodology

E003 is a five-case paired pilot using newly constructed, withheld defects. Each case was run once with `swe-2-medium` and once with `swe-2-max` in the frozen interleaved order. Devin received only the sanitized buggy workspace and byte-identical case prompt. Evaluation occurred after the disposable session closed and required public, held-out, and regression suites to pass.

The execution boundary used the frozen Linux/arm64 Docker image, dangerous/Bypass mode inside the container, read-only root, dropped capabilities, no-new-privileges, no host or control-repository mounts, no Docker socket, one read-only credential mount, and the restricted allowlist proxy. There were no retries or substantive interventions.

## Hypotheses

The primary hypothesis was deliberately non-directional: the Medium-versus-Max pattern observed in E002 might replicate, differ, or tie on the novel cases. Secondary measurements were success, public-versus-held-out agreement, wall time, observable activity, token usage, and patch size.

## Results

Medium solved 5/5; Max solved 5/5. Every run passed public, held-out, and regression evaluation. There were no visible-versus-held-out disagreements.

| Run | Case | Condition | Success | Public | Held-out | Regression | Wall s | Steps | Tool calls | Prompt tokens | Completion tokens | Patch |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| E003-N01-X | E003-N01 | X | 1 | pass | pass | pass | 125.088 | 15 | 9 | 108522 | 1858 | +1/-1 |
| E003-N03-M | E003-N03 | M | 1 | pass | pass | pass | 103.854 | 15 | 9 | 106432 | 875 | +3/-1 |
| E003-N02-X | E003-N02 | X | 1 | pass | pass | pass | 92.476 | 15 | 12 | 108023 | 1109 | +1/-0 |
| E003-N04-X | E003-N04 | X | 1 | pass | pass | pass | 241.778 | 16 | 13 | 156732 | 8459 | +9/-6 |
| E003-N05-X | E003-N05 | X | 1 | pass | pass | pass | 111.636 | 16 | 13 | 125937 | 1860 | +1/-2 |
| E003-N03-X | E003-N03 | X | 1 | pass | pass | pass | 113.501 | 16 | 13 | 125911 | 1749 | +1/-1 |
| E003-N05-M | E003-N05 | M | 1 | pass | pass | pass | 91.106 | 14 | 9 | 94163 | 914 | +1/-2 |
| E003-N02-M | E003-N02 | M | 1 | pass | pass | pass | 90.609 | 15 | 9 | 106106 | 793 | +1/-0 |
| E003-N04-M | E003-N04 | M | 1 | pass | pass | pass | 109.616 | 16 | 10 | 121566 | 1601 | +3/-5 |
| E003-N01-M | E003-N01 | M | 1 | pass | pass | pass | 103.726 | 17 | 10 | 132479 | 1104 | +1/-1 |

### Aggregate metrics

| Condition | Success | Wall total / mean / median (s) | Steps total / mean | Tool calls total / mean | Prompt tokens | Completion tokens | Source patch lines |
|---|---:|---:|---:|---:|---:|---:|---:|
| Medium | 5/5 | 498.911 / 99.782 / 103.726 | 77 / 15.40 | 47 / 9.40 | 560746 | 5287 | +9/-9 |
| Max | 5/5 | 684.480 / 136.896 / 113.501 | 78 / 15.60 | 60 / 12.00 | 625125 | 15035 | +13/-10 |

Max used more wall time in all five pairs. It used more tool calls in four pairs, fewer in N01, and more steps in two pairs, fewer in one, and tied in two. Aggregate prompt and completion tokens were higher for Max. Generated/environment churn was zero in all ten final diffs; each run changed only one source file.

## Per-case results and pair comparison

| Case | Outcome | Max minus Medium wall s | Steps | Tool calls | Prompt tokens | Completion tokens | Same source patch |
|---|---|---:|---:|---:|---:|---:|---:|
| E003-N01 | both success | 21.362 | -2 | -1 | -23957 | +754 | yes |
| E003-N02 | both success | 1.868 | +0 | +3 | +1917 | +316 | yes |
| E003-N03 | both success | 9.647 | +1 | +4 | +19479 | +874 | no |
| E003-N04 | both success | 132.163 | +0 | +3 | +35166 | +6858 | no |
| E003-N05 | both success | 20.529 | +2 | +4 | +31774 | +946 | yes |

All five cases were solved by both conditions. N01, N02, and N05 produced byte-identical source patches across conditions; N03 and N04 used different but behaviorally correct implementations. Human reference comparison was performed only after each pair closed. Agent correctness was determined behaviorally, not by patch identity.

## Failures and anomalies

There were no task failures, evaluator errors, infrastructure incidents, retries, or protocol deviations. The only notable result is a complete success tie despite materially different resource use. No public-versus-held-out disagreement occurred.

## E002 comparison

E002 used five historical BugsInPy cases and scored Medium 5/5 and Max 4/5. E003 used five newly constructed, withheld cases and scored Medium 5/5 and Max 5/5. Descriptively, E003 did not reproduce E002's Max failure: the novel set was a 5/5 tie. This does not establish a general model-effort effect.

## Limitations

This is an exploratory n=5 paired pilot. It is not a statistically powered comparison. The cases are newly constructed but no claim is made about absence from model training data. Costs and ACUs were unavailable. Observable activity is not internal reasoning, and the compact standard-library cases may not represent historical OSS maintenance broadly.

## Conclusions

Observed: both conditions completed all five novel repairs, while Max used more wall time in every pair and more aggregate prompt/completion tokens. Suggestive: on this small novel set, higher effort did not improve final behavioral success. Not established: that Medium is generally superior to Max, or that the E002 pattern fails or holds outside these ten paired observations.

## Reproducibility

The frozen configuration is in `manifests/experiment-003-config.json`; the randomized order is in `manifests/experiment-003-runs.json`; freeze hashes are in `manifests/experiment-003-freeze.json`; the evaluator and container runner are versioned under `scripts/`. Raw session exports remain private; sanitized run evidence is under `artifacts/experiment-003/`.

Generated from all ten closed run records. No Devin reasoning content was used or published.
