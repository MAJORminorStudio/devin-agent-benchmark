# Experiment 001 results summary

Exploratory paired evaluation; n=5. This report makes no statistical-significance claims.

Completed runs: 10/10
Total wall time: 299.547 seconds
Raw per-run artifacts are preserved under `results/runs/experiment-001/`.

## Condition summary

| Condition | Solved | Total | Mean wall (s) | Median wall (s) | Mean steps | Total completion tokens |
|---|---:|---:|---:|---:|---:|---:|
| Medium | 0 | 5 | 22.720 | 20.993 | 11.0 | 2210 |
| Max | 0 | 5 | 37.190 | 36.935 | 12.0 | 9932 |

Provider-reported cost was unavailable for every run. Token counts above come from the preserved Devin session exports.
Observed Medium tokens: 257602 prompt, 2210 completion, 227234 cached.
Observed Max tokens: 368380 prompt, 9932 completion, 322535 cached.

## Complete run table

| Run | Case | Model | Result | Public | Held-out | Regression | Wall (s) | Steps | Patch lines | Failure classification |
|---|---|---|---|---|---|---|---:|---:|---:|---|
| E001-C03-M | scrapy-3 | swe-2-medium | fail | fail | fail | pass | 27.138 | 10 | 0 | no patch / premature completion |
| E001-C01-X | black-16 | swe-2-max | fail | fail | fail | pass | 50.860 | 13 | 0 | no patch / premature completion |
| E001-C05-M | tornado-13 | swe-2-medium | fail | fail | fail | pass | 13.878 | 11 | 0 | no patch / premature completion |
| E001-C02-X | fastapi-3 | swe-2-max | fail | fail | fail | pass | 17.656 | 10 | 0 | no patch / premature completion |
| E001-C04-M | tqdm-5 | swe-2-medium | fail | fail | fail | pass | 13.561 | 12 | 0 | no patch / premature completion |
| E001-C03-X | scrapy-3 | swe-2-max | fail | fail | fail | pass | 43.699 | 11 | 0 | no patch / premature completion |
| E001-C01-M | black-16 | swe-2-medium | fail | fail | fail | pass | 38.028 | 12 | 0 | no patch / premature completion |
| E001-C05-X | tornado-13 | swe-2-max | fail | fail | fail | pass | 36.799 | 13 | 0 | no patch / premature completion |
| E001-C02-M | fastapi-3 | swe-2-medium | fail | fail | fail | pass | 20.993 | 10 | 0 | no patch / premature completion |
| E001-C04-X | tqdm-5 | swe-2-max | fail | fail | fail | pass | 36.935 | 13 | 0 | no patch / premature completion |

## Paired outcomes

| Case | Outcome |
|---|---|
| black-16 | both failed |
| fastapi-3 | both failed |
| scrapy-3 | both failed |
| tornado-13 | both failed |
| tqdm-5 | both failed |

## Medium versus Max observations

### black-16

- Exploration: Max recorded one more session step and 12.832 additional seconds.
- Diagnosis: Both captured outputs inspected the external-symlink failure; neither completed a repair.
- Patch strategy: Neither condition produced a patch.
- Verification behavior: Neither reached a passing public or held-out evaluation; both regression subsets passed.
- Final outcome: Both failed. Max did not improve the final outcome.
### fastapi-3

- Exploration: Both recorded 10 session steps; Max completed 3.337 seconds sooner and emitted more completion tokens.
- Diagnosis: Neither captured output demonstrated a completed diagnosis or implementation.
- Patch strategy: Neither condition produced a patch.
- Verification behavior: Neither reached a passing public or held-out evaluation; both regression subsets passed.
- Final outcome: Both failed. Increased effort did not change the outcome.
### scrapy-3

- Exploration: Max recorded one more session step and 16.561 additional seconds.
- Diagnosis: Both inspected the redirect test and middleware; neither completed a repair.
- Patch strategy: Neither condition produced a patch.
- Verification behavior: Neither reached a passing public or held-out evaluation; both regression subsets passed.
- Final outcome: Both failed. Max did not improve the final outcome.
### tornado-13

- Exploration: Max recorded two more session steps and 22.921 additional seconds.
- Diagnosis: Max articulated the response/request start-line mismatch; Medium left no comparable diagnostic statement in captured output.
- Patch strategy: Neither condition produced a patch.
- Verification behavior: Neither reached a passing public or held-out evaluation; both regression subsets passed.
- Final outcome: Both failed. The extra effort did not produce an implementation.
### tqdm-5

- Exploration: Max recorded one more session step and 23.374 additional seconds.
- Diagnosis: Max articulated the likely disabled-state initialization issue; Medium left no comparable diagnostic statement in captured output.
- Patch strategy: Neither condition produced a patch.
- Verification behavior: Neither reached a passing public or held-out evaluation; both regression subsets passed.
- Final outcome: Both failed. The extra effort did not produce an implementation.

## Evaluator-side comparison with human reference patches

Reference comparison was performed only after both conditions for each case were closed. Reference implementations were not copied into agent workspaces.

| Case | Reference files | Reference lines | Agent patch files | Comparison |
|---|---|---:|---|---|
| black-16 | black.py | 15 | none | no matching agent patch |
| fastapi-3 | fastapi/routing.py | 32 | none | no matching agent patch |
| scrapy-3 | scrapy/downloadermiddlewares/redirect.py | 7 | none | no matching agent patch |
| tornado-13 | tornado/http1connection.py, tornado/test/runtests.py | 5 | none | no matching agent patch |
| tqdm-5 | tqdm/_tqdm.py | 13 | none | no matching agent patch |

## Infrastructure and protocol notes

During the resumed ten-run execution, no authentication failure, Cognition service outage, unexpected paid charge, frozen-model availability issue, workspace preparation failure, or evaluator infrastructure error was recorded.
A pre-resume evaluator-environment error for E001-C03-M is preserved as provenance; it was corrected before the resumed sequence, and the Devin session was not rerun.
Protocol deviations recorded: none.
The CLI permission warning appeared in 10/10 runner captures. It is preserved as an execution observation and should be considered when interpreting the uniformly empty patches.

E001-C03-M was not rerun. Its frozen result remains 27.138 seconds, empty patch, public fail, held-out fail, regression pass, TASK_SUCCESS=false.
