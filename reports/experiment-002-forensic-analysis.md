# Experiment 002 forensic analysis

Observable-behavior analysis of the completed paired Devin evaluation. No Devin session was invoked or rerun for this analysis. Hidden reasoning content was not analyzed.

## Executive finding

Medium solved 5/5 cases; Max solved 4/5. Max took more wall time in all five pairs and recorded more steps in four. The sole failure was Max on tqdm-5: the public and regression checks passed, but the evaluator-only sized-iterable test failed because `total` remained `None`.

E002 is an autonomous-capability result under the frozen isolated Docker configuration. It is not a causal or statistically significant comparison: there are five paired cases, the cases were not randomly sampled for this analysis, and E001 is not a valid capability baseline because its noninteractive permission gate rejected required tools.

## Evidence and scope

The analyzer reconciles all ten public sanitized session exports, the corresponding raw session-export/stdout/stderr inventories, runner metadata, evaluator results, workspace-change summaries, and final patches. It counts only observable tool calls, commands, observations, edits, and user-visible agent messages; it never reads or emits Devin `reasoning_content`.

All ten E002 runs recorded zero structured rejected tool calls, no permission warning, empty Devin stderr, return code 0, completed termination, and evaluator status `OK`. Ordinary shell/test failures inside a session are retained as agent/environment observations, not reclassified as infrastructure failures.

## Run-level tool behavior

Source-edit counts distinguish direct source edits and observable shell mutations from generated/cache files. `post-edit calls` is a descriptive proxy for activity after the first observable source mutation, not a diagnosis of internal reasoning.

| Run | Condition | Success | Wall s | Steps | Tools | exec/read/search/web/edit-write | Tests (pass/fail) | First source step | First test step | Source edits | Post-edit calls |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| E002-C02-M | M | 1 | 299.332 | 35 | 30 | 19/3/1/6/1 | 1/1 | 24 | 11 | 1 | 2 |
| E002-C04-X | X | 0 | 405.290 | 42 | 44 | 21/11/6/0/6 | 3/3 | 10 | 14 | 1 | 13 |
| E002-C01-M | M | 1 | 366.269 | 47 | 41 | 34/6/0/0/1 | 9/5 | 9 | 13 | 4 | 19 |
| E002-C05-X | X | 1 | 326.457 | 36 | 30 | 20/6/1/0/3 | 4/5 | 11 | 15 | 3 | 10 |
| E002-C03-M | M | 1 | 817.861 | 62 | 59 | 48/4/0/5/2 | 4/3 | 22 | 10 | 2 | 17 |
| E002-C01-X | X | 1 | 399.819 | 36 | 42 | 27/9/0/0/6 | 1/2 | 10 | 31 | 1 | 3 |
| E002-C04-M | M | 1 | 157.312 | 22 | 14 | 12/1/0/0/1 | 2/1 | 10 | 11 | 1 | 4 |
| E002-C02-X | X | 1 | 1137.750 | 69 | 71 | 38/11/2/11/7 | 2/3 | 32 | 55 | 1 | 16 |
| E002-C05-M | M | 1 | 175.535 | 33 | 25 | 23/1/0/0/1 | 3/4 | 19 | 11 | 3 | 8 |
| E002-C03-X | X | 1 | 1380.464 | 91 | 135 | 64/18/1/0/49 | 2/4 | 10 | 11 | 2 | 10 |

The complete command-level inventory is in `results/experiment-002-tool-metrics.csv` and the structured JSON. Repeated commands, test status, ordinary nonzero shell exits, inspected target paths, and final observable messages are preserved there.

## Condition aggregates

| Condition | Solved | Wall total / mean / median s | Steps total / mean | Tool calls | Prompt / completion / cached tokens | Source + / - | All changed files | Generated/environment files |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| M | 5/5 | 1816.309 / 363.262 / 299.332 | 199 / 39.800 | 169 | 4120476 / 52313 / 3968909 | +48 / -11 | 85 | 80 |
| X | 4/5 | 3649.780 / 729.956 / 405.290 | 274 / 54.800 | 322 | 11740951 / 164983 / 11408875 | +42 / -10 | 3223 | 3218 |

Max/Medium ratios from these aggregate totals are in the JSON: total wall 2.009×, mean wall 2.009×, median wall 1.354×, total steps 1.377×, total tool calls 1.905×, prompt tokens 2.849×, completion tokens 3.154×, and all changed files 37.918×. The last ratio is dominated by generated virtualenv/cache files and is not a source-complexity ratio.

## Evaluator outcome ledger

| Run | Public | Held-out | Regression | TASK_SUCCESS | Interventions | Termination |
|---|---|---|---|---:|---:|---|
| E002-C02-M | pass | pass | pass | 1 | 0 | completed |
| E002-C04-X | pass | fail | pass | 0 | 0 | completed |
| E002-C01-M | pass | pass | pass | 1 | 0 | completed |
| E002-C05-X | pass | pass | pass | 1 | 0 | completed |
| E002-C03-M | pass | pass | pass | 1 | 0 | completed |
| E002-C01-X | pass | pass | pass | 1 | 0 | completed |
| E002-C04-M | pass | pass | pass | 1 | 0 | completed |
| E002-C02-X | pass | pass | pass | 1 | 0 | completed |
| E002-C05-M | pass | pass | pass | 1 | 0 | completed |
| E002-C03-X | pass | pass | pass | 1 | 0 | completed |

The held-out evaluator was external to the agent workspace and was run only after the session closed. The `OK` statuses here mean evaluation infrastructure completed; the tqdm-Max held-out assertion itself failed and therefore TASK_SUCCESS was 0.

## Source-only patch metrics

| Run | Source file | Source + | Source - | All changed files | Generated/environment files | Recorded all-file + / - |
|---|---|---:|---:|---:|---:|---:|
| E002-C02-M | fastapi/routing.py | 25 | 7 | 2 | 1 | 26 / 7 |
| E002-C04-X | tqdm/_tqdm.py | 2 | 0 | 11 | 10 | 12 / 0 |
| E002-C01-M | black.py | 10 | 1 | 13 | 12 | 22 / 1 |
| E002-C05-X | tornado/http1connection.py | 1 | 1 | 36 | 35 | 36 / 1 |
| E002-C03-M | scrapy/downloadermiddlewares/redirect.py | 6 | 2 | 29 | 28 | 34 / 2 |
| E002-C01-X | black.py | 10 | 1 | 1512 | 1511 | 1517 / 1 |
| E002-C04-M | tqdm/_tqdm.py | 6 | 0 | 10 | 9 | 15 / 0 |
| E002-C02-X | fastapi/routing.py | 25 | 7 | 1 | 0 | 25 / 7 |
| E002-C05-M | tornado/http1connection.py | 1 | 1 | 31 | 30 | 31 / 1 |
| E002-C03-X | scrapy/downloadermiddlewares/redirect.py | 4 | 1 | 1663 | 1662 | 1662 / 1 |

The all-file records overstate code churn for Black-X and Scrapy-X because their preserved final filesystem records include virtualenv and bytecode/cache files. The source-only diffs are +10/-1 for both Black runs, +4 to +6/-1 to -2 for Scrapy, +25/-7 for FastAPI, +6/-0 or +2/-0 for tqdm, and +1/-1 for Tornado.

## Case deep dives

### black-16

Ignore a Python symlink resolving outside the discovery root while continuing to discover in-root files.

Both conditions inspected the symlink regression and the `gen_python_files_in_dir` implementation, reproduced the outside-root `ValueError`, and applied the same observable try/except-and-skip behavior. Their source diffs are identical at the recorded patch level (+10/-1), both passed the public, held-out, and regression evaluators. Max’s +1,512 changed-file record is almost entirely `.venv`/cache churn; Medium’s 13 files are mostly bytecode/cache plus one source file.

### fastapi-3

Recursively serialize nested response models with aliases and exclude unset fields.

Medium and Max both explored `fastapi/routing.py` and implemented recursive response-content preparation. Both passed all eight public checks, the independent nested-list/nested-map held-out checks, and the regression check. Max used 69 steps, 71 tool calls, six web-search calls, and 1,137.750 seconds versus Medium’s 35 steps, 30 tool calls, and 299.332 seconds. The source diff shape was +25/-7 for both; the recorded source text differs in formatting and parameter handling details, so behavioral success—not patch identity—is the relevant result.

### scrapy-3

Normalize an extra-slash protocol-relative Location using the request scheme and redirect host.

Both found the redirect middleware path and addressed the extra-slash protocol-relative Location behavior. Medium’s source diff was +6/-2 and Max’s +4/-1; both passed the public redirect test, independent HTTPS/GET held-out test, and regression subset. Max spent 1,380.464 seconds and recorded 135 tool calls, while Medium spent 817.861 seconds and recorded 59. Max’s 1,663 changed files were dominated by a generated `.venv` and bytecode/cache entries. The observable final messages explicitly describe the URL normalization; no hidden reasoning is used here.

### tqdm-5

A disabled progress wrapper retains an inferred total for a sized iterable and reports its length consistently.

This is the only pair that separated on correctness. Medium computed an inferred total for a sized iterable inside the disabled path and passed the held-out assertion. Max initialized `self.total` and `self.leave` but did not infer `len(iterable)` before returning; the held-out test therefore observed `progress.total is None` while public `test_bool` and the two regression checks passed. Max used 42 tools/21 shell commands and 405.290 seconds versus Medium’s 14 tools/12 shell commands and 157.312 seconds. More exploration reached the right state-initialization area but did not produce a complete behavioral fix.

### tornado-13

Read a bodyless HTTP/1.0 response without Content-Length when the response start line has no method field.

Both identified the unsafe `start_line.method` access for response start lines and made the same one-line defensive change (+1/-1). Both passed the public HTTP/1.0 test, the independent bodyless-204 held-out socket test, and the regression subset. Max used 36 steps and 326.457 seconds versus Medium’s 33 steps and 175.535 seconds; the final outcome was unchanged.

## Paired Medium-versus-Max summary

| Case | Outcome | Max − Medium wall s | Max − Medium steps | Max − Medium tool calls | Source patch identical | Interpretation |
|---|---|---:|---:|---:|---|---|
| black-16 | both succeeded | 33.550 | -11 | 1 | yes | Both reached the same compact source behavior and passed; Max incurred a large virtualenv-only churn record. |
| fastapi-3 | both succeeded | 838.418 | 34 | 41 | no | Both implemented the recursive response normalization behavior; Max used substantially more exploration, web lookup, and time. |
| scrapy-3 | both succeeded | 562.602 | 29 | 76 | no | Both found the redirect path and passed; Max spent substantially more time and created a large virtualenv/cache record. |
| tqdm-5 | Medium only | 247.978 | 20 | 30 | no | Max explored more and edited the same target, but its two-line initialization missed inferred totals for sized iterables; Medium passed the held-out contract. |
| tornado-13 | both succeeded | 150.922 | 3 | 5 | yes | Both reached the same one-line defensive source fix and passed; Max spent more wall time with only a small increase in steps. |

Observed: Max used more wall time in every pair; it used more steps in four pairs and more tool calls in every pair. The paired result was both-successful for Black, FastAPI, Scrapy, and Tornado, and Medium-only for tqdm.

Suggestive: on these cases, higher effort coincided with more exploration and environment/dependency work, especially FastAPI-X and Scrapy-X, without improving the aggregate score. This is descriptive association only.

Not supported: a causal claim that Max is slower or less capable in general; statistical significance; reconstruction of hidden model reasoning; or treating virtualenv/cache churn as implementation complexity.

## Human reference comparison

Reference patches were read evaluator-side only after both paired sessions were closed. All ten agent patches touched the reference target source file, but no agent patch is required to match the human implementation. Reference and agent source-only metrics are in `results/experiment-002-source-patch-metrics.csv` and the JSON.

| Case | Human reference | Medium source diff | Max source diff | Behavioral outcome |
|---|---|---:|---:|---|
| black-16 | +14/-1 in black.py | +10/-1 | +10/-1 | both pass |
| fastapi-3 | +25/-7 in fastapi/routing.py | +25/-7 | +25/-7 | both pass |
| scrapy-3 | +5/-2 in scrapy/downloadermiddlewares/redirect.py | +6/-2 | +4/-1 | both pass |
| tqdm-5 | +7/-6 in tqdm/_tqdm.py | +6/-0 | +2/-0 | Medium only |
| tornado-13 | +4/-1 in tornado/http1connection.py, tornado/test/runtests.py | +1/-1 | +1/-1 | both pass |

Black’s agents used a shorter equivalent source change than the reference. FastAPI’s agents matched the reference line counts but are not text-identical evidence of copying. Scrapy, tqdm, and Tornado used alternative source diffs; tqdm-Max’s alternative was behaviorally incomplete. These comparisons are descriptive and evaluator-side only.

## E001 to E002 contrast

E001 recorded 0/5 for both conditions, but its noninteractive `accept-edits` mode rejected required tools and produced empty patches; it is invalid as a capability comparison. E002 changed only the execution permission boundary while preserving the cases, prompts, models, order, scoring, and intervention policy, and ran inside the isolated disposable container. E002 therefore demonstrates the effect of making autonomous tool use operational in this harness, not a clean model-only comparison with E001.

## Reproducibility and security notes

The raw E002 result directories remain locally ignored and preserve the original exports, stdout/stderr, patches, evaluator output, and container metadata. Committed public artifacts are sanitized derivatives. No Devin or benchmark case was run during this analysis, no result/evaluator outcome was changed, and no Experiment 003 was started.

Generated outputs:

- `results/experiment-002-forensics.json`
- `results/experiment-002-tool-metrics.csv`
- `results/experiment-002-source-patch-metrics.csv`
- `reports/experiment-002-forensic-analysis.md`

The pre-commit scan of these generated artifacts found no credentials, tokens, cookies, authorization headers, private URLs, host paths, or environment secrets. Raw local artifacts are not included in this public report.
