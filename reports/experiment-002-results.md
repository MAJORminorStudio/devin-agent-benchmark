# Experiment 002 results

Exploratory paired evaluation of five BugsInPy repairs under isolated Devin SWE-2 Medium and Max conditions. n=5 pairs; no statistical-significance claims are made.

All 10 frozen runs completed in the requested order. Every session used the frozen disposable linux/arm64 Docker path with dangerous permission mode / effective Bypass, and every evaluator returned `OK`.

Forensic follow-up: the patch counts below are preserved all-file workspace
records and may include generated virtualenv/bytecode churn. See the
[forensic analysis](experiment-002-forensic-analysis.md) and its
source-only/tool-metric outputs for the separated source-diff and observable
tool-behavior analysis.

## Condition summary

| Condition | Solved | Total | Total wall (s) | Mean wall (s) | Median wall (s) | Mean steps | Prompt tokens | Completion tokens | Cached tokens |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Medium | 5 | 5 | 1816.309 | 363.262 | 299.332 | 39.8 | 4,120,476 | 52,313 | 3,968,909 |
| Max | 4 | 5 | 3649.780 | 729.956 | 405.290 | 54.8 | 11,740,951 | 164,983 | 11,408,875 |

Reported monetary cost and ACUs were unavailable for all ten runs.

## Complete run table

| # | Run | Case | Model | TASK_SUCCESS | Public | Held-out | Regression | Wall (s) | Steps | Tokens P/C/cache | Files | +/- lines | Failure classification |
|---:|---|---|---|---|---|---|---|---:|---:|---|---:|---:|---|
| 1 | E002-C02-M | fastapi-3 | swe-2-medium | 1 | pass | pass | clean | 299.332 | 35 | 599,955/9,374/568,967 | 2 | +26/-7 | successful repair |
| 2 | E002-C04-X | tqdm-5 | swe-2-max | 0 | pass | fail | clean | 405.290 | 42 | 814,278/11,151/774,656 | 11 | +12/-0 | partial fix / correct target but incomplete implementation |
| 3 | E002-C01-M | black-16 | swe-2-medium | 1 | pass | pass | clean | 366.269 | 47 | 903,193/10,310/873,193 | 13 | +22/-1 | successful repair |
| 4 | E002-C05-X | tornado-13 | swe-2-max | 1 | pass | pass | clean | 326.457 | 36 | 783,919/9,317/756,333 | 36 | +36/-1 | successful repair |
| 5 | E002-C03-M | scrapy-3 | swe-2-medium | 1 | pass | pass | clean | 817.861 | 62 | 1,960,369/26,800/1,896,201 | 29 | +34/-2 | successful repair |
| 6 | E002-C01-X | black-16 | swe-2-max | 1 | pass | pass | clean | 399.819 | 36 | 591,544/10,720/566,965 | 1512 | +1517/-1 | successful repair |
| 7 | E002-C04-M | tqdm-5 | swe-2-medium | 1 | pass | pass | clean | 157.312 | 22 | 220,679/2,343/208,403 | 10 | +15/-0 | successful repair |
| 8 | E002-C02-X | fastapi-3 | swe-2-max | 1 | pass | pass | clean | 1137.750 | 69 | 3,504,981/60,615/3,400,046 | 1 | +25/-7 | successful repair |
| 9 | E002-C05-M | tornado-13 | swe-2-medium | 1 | pass | pass | clean | 175.535 | 33 | 436,280/3,486/422,145 | 31 | +31/-1 | successful repair |
| 10 | E002-C03-X | scrapy-3 | swe-2-max | 1 | pass | pass | clean | 1380.464 | 91 | 6,046,229/73,180/5,910,875 | 1663 | +1662/-1 | successful repair |

## Paired outcomes and Medium versus Max

| Case | Outcome | Exploration | Diagnosis / test strategy | Edit / verification |
|---|---|---|---|---|
| black-16 | both succeeded | Max used -11 steps versus Medium and took +33.550s wall time. | Both conditions produced a source edit overlapping the reference target file; correctness is established by evaluator behavior, not implementation identity. Both conditions passed public, held-out, and regression checks. | Max changed +1499 total filesystem entries versus Medium; source-file overlap was 1 for Medium and 1 for Max. Both conditions passed public, held-out, and regression checks. |
| fastapi-3 | both succeeded | Max used +34 steps versus Medium and took +838.418s wall time. | Both conditions produced a source edit overlapping the reference target file; correctness is established by evaluator behavior, not implementation identity. Both conditions passed public, held-out, and regression checks. | Max changed -1 total filesystem entries versus Medium; source-file overlap was 1 for Medium and 1 for Max. Both conditions passed public, held-out, and regression checks. |
| scrapy-3 | both succeeded | Max used +29 steps versus Medium and took +562.603s wall time. | Both conditions produced a source edit overlapping the reference target file; correctness is established by evaluator behavior, not implementation identity. Both conditions passed public, held-out, and regression checks. | Max changed +1634 total filesystem entries versus Medium; source-file overlap was 1 for Medium and 1 for Max. Both conditions passed public, held-out, and regression checks. |
| tqdm-5 | Medium only | Max used +20 steps versus Medium and took +247.978s wall time. | Max reached the disabled-state area, but its implementation missed the held-out sized-iterable behavior; Medium passed it. Medium passed public, held-out, and regression checks; Max passed public/regression but failed held-out. | Max changed +1 total filesystem entries versus Medium; source-file overlap was 1 for Medium and 1 for Max. Medium passed public, held-out, and regression checks; Max passed public/regression but failed held-out. |
| tornado-13 | both succeeded | Max used +3 steps versus Medium and took +150.922s wall time. | Both conditions produced a source edit overlapping the reference target file; correctness is established by evaluator behavior, not implementation identity. Both conditions passed public, held-out, and regression checks. | Max changed +5 total filesystem entries versus Medium; source-file overlap was 1 for Medium and 1 for Max. Both conditions passed public, held-out, and regression checks. |

The strongest overall pattern is that Max did not improve the final score: Medium solved 5/5 while Max solved 4/5. Max used more wall time in every pair and more steps in four of five pairs. Two Max runs also created large `.venv`-related workspace churn, so total filesystem patch size is not a clean proxy for source-edit complexity.

## Failure classifications

- `E002-C04-X`: partial fix / correct target but incomplete implementation. Public and regression checks passed, but the held-out sized-iterable assertion failed (`total` remained `None`).
- All other runs: successful repair. No ordinary agent failure occurred.

## Human reference comparison

Comparison was performed only after both members of every case pair were closed. The reference implementation was never copied into an agent workspace.

| Case | Reference files | Reference +/- lines | Medium source overlap | Max source overlap |
|---|---|---:|---|---|
| black-16 | black.py | +14/-1 | black.py | black.py |
| fastapi-3 | fastapi/routing.py | +25/-7 | fastapi/routing.py | fastapi/routing.py |
| scrapy-3 | scrapy/downloadermiddlewares/redirect.py | +5/-2 | scrapy/downloadermiddlewares/redirect.py | scrapy/downloadermiddlewares/redirect.py |
| tqdm-5 | tqdm/_tqdm.py | +7/-6 | tqdm/_tqdm.py | tqdm/_tqdm.py |
| tornado-13 | tornado/http1connection.py, tornado/test/runtests.py | +4/-1 | tornado/http1connection.py | tornado/http1connection.py |

Overlap here is a file-level comparison only; TASK_SUCCESS is based on behavior, not matching the human patch.

## E001 contrast

E001 scored 0/5 for both conditions, but it is invalid as a capability comparison: its noninteractive `accept-edits` configuration rejected required tool calls and yielded empty patches. E002 enabled dangerous/Bypass only inside the disposable isolated container, allowing autonomous exploration, editing, and verification.

## Infrastructure, protocol, and security

- Infrastructure incidents: none. All pre-run isolation/evaluator checks passed; all Devin sessions closed before evaluator execution; all containers were disposable and removed after each run.
- Protocol deviations: none. No retries, substantive interventions, prompt/model/order changes, or evaluator/reference leakage were recorded.
- No paid-charge prompt or charge was observed; provider cost/ACU fields were unavailable.
- No Devin/harness tool-call rejections were found in the ten session exports. A small number of ordinary in-container shell errors are preserved in raw output and did not stop evaluation.
- Security scan: no account credentials, auth tokens, cookies, authentication headers, private URLs, or environment secrets found in generated artifacts. The ignored raw workspace copies contain upstream test-fixture PEM material only, not account credentials; raw outputs and patches are preserved locally under `results/runs/experiment-002/`, while the committed report/summary contain metadata and metrics only.

## Artifacts

- Summary: `results/experiment-002-summary.json`
- Raw per-run artifacts: `results/runs/experiment-002/<run-id>/output/`
- Evaluator results are stored as `evaluation-result.json` in each run output directory.

E002 is complete. Experiment 003 was not started.
