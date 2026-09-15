---
title: Same Five Bugs, Twice the Work
dek: >-
  A paired Devin experiment on five real Python bugs found SWE-2 Max using
  more time, tools, and tokens than Medium, and finishing with one fewer
  complete repair.
slug: same-five-bugs-twice-the-work
meta_description: >-
  Paired Devin pilot on five real Python bugs. SWE-2 Medium went 5/5, Max 4/5,
  while Max used substantially more time and tokens.
---

# Same Five Bugs, Twice the Work

We gave Cognition's Devin the same five real software bugs twice: once with SWE-2 Medium, once with SWE-2 Max. Each pair used the same frozen prompt, a fresh workspace, no retries, and no human pointing at the right file.

The intuitive expectation is that greater reasoning effort should at least preserve correctness, even if it costs more time and tokens. In this five-case paired pilot, Medium completed 5/5 repairs. Max completed 4/5. Max took more wall time in every pair, issued more observable tool calls in every pair, and consumed 2.85× the prompt tokens and 3.15× the completion tokens. The extra activity did not raise the aggregate score.

This is n=5, too small to rank Devin conditions. What the files show is narrower: when one autonomous coding agent was asked to spend substantially more effort on five historical Python bugs, that effort did not convert into more complete repairs.

## What we tested

The agent was Cognition Devin, run through the local CLI, on two frozen SWE-2 effort conditions: Medium and Max. Fusion was excluded. The capability comparison, Experiment 002, ran unattended inside disposable isolated Docker containers. The tasks were five real bugs from BugsInPy. Each case has a known buggy revision and a known fixed revision; project tests come with the dataset metadata:

- **Black 16.** Skip a Python symlink that resolves outside the discovery root, without abandoning in-root files.
- **FastAPI 3.** Recursively serialize nested response models when aliases and unset fields are involved.
- **Scrapy 3.** Normalize an extra-slash protocol-relative `Location` while keeping the request scheme and redirect host.
- **tqdm 5.** When display is disabled, still infer the length of a sized iterable and keep that total consistent.
- **Tornado 13.** Make a keep-alive decision for a bodyless HTTP/1.0 response whose start line has no method field.

The design was paired. Within each pair the task was identical. Each run started from a fresh sanitized workspace built from the buggy archive, not a git clone, so later commits and the historical patch were not sitting in `.git`. The agent saw the frozen prompt and the tests that belong in that workspace. The reference patch, the held-out tests, and the evaluator metadata stayed outside the agent workspace.

There were no retries and no substantive intervention. After each Devin session closed, a held-out evaluator ran the public project test, an independent behavioral test the agent never saw, and a practical regression subset. The evaluator tests were outside the agent workspace, unavailable to Devin during execution, and run only after the session closed. They were subsequently published with the research evidence. `TASK_SUCCESS` required all three. A patch that made the visible test green and missed the held-out contract did not count.

The frozen protocol is in the [v1.0.0 research report](https://github.com/MAJORminorStudio/devin-agent-benchmark/blob/v1.0.0/reports/swe-2-medium-vs-max-research-report.md).

## Results

| Metric | Medium | Max |
|---|---:|---:|
| Successful repairs | 5/5 | 4/5 |
| Mean wall time | 363s | 730s |
| Observable steps | 199 | 274 |
| Observable tool calls | 169 | 322 |
| Prompt tokens | 4.12M | 11.74M |
| Completion tokens | 52.3K | 165.0K |
| Source-only diff | +48 / -11 | +42 / -10 |

Four pairs succeeded under both conditions: Black, FastAPI, Scrapy, Tornado. tqdm succeeded only under Medium. No pair succeeded only under Max.

Wall time was higher for Max in all five pairs. Mean wall was 363 seconds for Medium and 730 for Max, about 2.01×. Median wall moved less (299s versus 405s) because two Max runs, FastAPI and Scrapy, ran much longer than their Medium twins. Max also issued more observable tool calls in every pair and more steps in four of five.

Those ratios describe this sample. They are not a significance test. n=5 stays attached to every comparison below: substantially greater agent activity did not produce greater aggregate repair accuracy.

## The tqdm repair that passed the public test

tqdm is the only pair that split on correctness, and it is the reason a visible-test-only score would have been wrong.

The public test, `test_bool`, originally failed because a disabled tqdm object had no `total` attribute. Both conditions found that path, produced a patch, made `test_bool` pass, and kept the regression subset clean.

The held-out test never went to the agent. After the session closed, the evaluator constructed a disabled progress wrapper around a sized iterable and did not pass `total`:

```python
progress = tqdm(["a", "b", "c"], disable=True, file=StringIO())
assert progress.total == 3
```

The expected behavior is an inferred total of 3. Medium passed. Max failed with `assert None == 3`.

The patches explain the split without any need to guess at hidden reasoning. Medium inferred length before storing the total:

```python
if total is None and iterable is not None:
    try:
        total = len(iterable)
    except (TypeError, AttributeError):
        total = None
self.total = total
```

Max stored the explicit `total` argument directly and returned:

```python
self.total = total
self.leave = leave
```

When no explicit total was supplied, `total` stayed `None`. The public test did not fully distinguish an explicit total from an inferable one. The held-out test did. Max spent 405.290 seconds, 42 steps, and 44 tool calls on this case, against Medium's 157.312 seconds, 22 steps, and 14 tool calls. More exploration reached the right initialization site and still left the sized-iterable behavior unset.

The files do not show why the agent stopped there, and they do not show that Max knowingly overfit the visible test. The precise statement is narrower: the Max repair satisfied the visible failure and did not fully capture the behavioral contract the held-out evaluator exercised.

For autonomous coding agents, that distinction is the point of holding tests out. A production caller still needs `tqdm(["a", "b", "c"], disable=True)` to report length 3. If the benchmark only scores the test the agent can see, an incomplete repair looks like a win.

## What did the extra activity buy?

The [forensic analysis](https://github.com/MAJORminorStudio/devin-agent-benchmark/blob/v1.0.0/reports/experiment-002-forensic-analysis.md) stays on observables: wall time, tool calls, commands, edits, user-visible messages. Hidden reasoning was not read and is not reconstructed here.

Max had higher wall time in 5/5 pairs, more observable tool calls in 5/5 pairs, and more steps in 4/5 pairs. Aggregate prompt and completion token use was substantially higher for Max. The largest time gaps were FastAPI and Scrapy, both successes, not the tqdm miss.

On FastAPI, both conditions implemented recursive response-content preparation in `fastapi/routing.py` and passed all three evaluator checks. Medium finished in 299.332 seconds with 35 steps and 30 tool calls. Max finished in 1,137.750 seconds with 69 steps and 71 tool calls. The source-diff shape was +25/-7 in both cases. The recorded source text was not identical. The score uses behavior; the two patches did not have to match.

On Scrapy, both found the redirect middleware and passed. Medium took 817.861 seconds, 62 steps, and 59 tool calls. Max took 1,380.464 seconds, 91 steps, and 135 tool calls. Source-only changes were small in both conditions (+6/-2 versus +4/-1).

Black and Tornado were more compact still. Both Black runs produced the same recorded source behavior, +10/-1 in `black.py`. Both Tornado runs made the same one-line defensive change, +1/-1 in `tornado/http1connection.py`. Max still spent more wall time on both.

The workspace-change totals look, at first glance, like Max rewrote the repositories. Medium's preserved all-file record covers 85 files. Max's covers 3,223, about 38×. Almost none of that is source. Medium changed 5 source files and 80 generated or environment files. Max changed 5 source files and 3,218 generated or environment files. Black-Max and Scrapy-Max dominate the gap: 1,511 and 1,662 generated files, mostly virtualenv trees and bytecode cache. Actual source edits across the five Max runs were +42/-10, against Medium's +48/-11.

Agent activity and useful source modification are different measurements. A run can spend 1,380 seconds, issue 135 tool calls, and leave a +4/-1 source patch. A run can also look like thousands of changed files when the filesystem record is a virtualenv. Counting either number as how much the agent rewrote the project misreads the trace.

## The experiment that failed first

Before any of those repairs existed, we ran the same five cases, same pair structure, same frozen prompts, and same model conditions, and scored 0/5 for Medium and 0/5 for Max.

That was not evidence that SWE-2 could not solve the bugs. Experiment 001 used the unattended CLI with `accept-edits`. File edits were acceptable. Shell commands still required confirmation. A noninteractive process cannot supply that confirmation. Required tool calls were rejected in all ten runs. Every patch was empty.

We kept the runs. Empty patches, rejected tool records, permission warnings, and evaluator output are in the [public E001 artifacts](https://github.com/MAJORminorStudio/devin-agent-benchmark/tree/v1.0.0/artifacts/experiment-001). Discarding them would have made the later 9/10 look cleaner than the work actually was.

Experiment 002 changed one operational fact: the agent received effective Bypass so it could inspect files, execute shell commands, edit source, and execute tests without waiting for a human. Because that setting permits unrestricted actions, the runs went inside disposable isolated Docker containers with a read-only root filesystem, all Linux capabilities dropped, no-new-privileges, no Docker socket, no host repository mount, one sanitized workspace, and allowlisted egress. Cases, prompts, model IDs, run order, scoring, and the no-intervention rule did not change. Under that configuration, nine of the ten repairs succeeded. Zero structured tool rejections occurred.

Permission policy is part of the effective agent system. A benchmark that cannot let the agent run `pytest` is measuring the harness. E001 failed that check. Publishing it is how we keep E002 honest.

## What this does and does not say

Observed, in these five pairs:

- Medium solved 5/5.
- Max solved 4/5.
- Max took longer in every pair.
- Max used more tool calls in every pair.
- Max used substantially more tokens.
- Additional activity did not improve aggregate correctness.

Suggestive, and only that: greater reasoning effort may have diminishing returns on some bounded software-repair tasks. Four of these bugs were already inside Medium's reach. On those four, Max still spent more time. On tqdm, more exploration did not complete the contract the held-out test checks. Treat that as a hypothesis for a larger evaluation, not a law of SWE-2.

Not established:

- Medium is generally superior to Max.
- Max is generally inefficient.
- More reasoning makes coding agents worse.
- These ratios generalize past these five historical Python bugs.
- Statistical superiority of either condition.

The evaluation covers one agent product and one frozen task setup. That bound travels with the result.

This is a five-case pilot. The sample is small, and that limit is real. The cases were selected for reproducibility and task suitability, not sampled at random from all software. Monetary cost and ACU data were unavailable, so the extra work is reported in seconds, steps, tool calls, and tokens, not dollars. Hidden reasoning was not analyzed. Public benchmark exposure cannot be ruled out. Those limits belong next to the result. A paired pilot is not a product ranking.

## Why the files are public

The [v1.0.0 release](https://github.com/MAJORminorStudio/devin-agent-benchmark/releases/tag/v1.0.0) includes the frozen protocol, the prompts, the run order, the patches, the evaluator outputs, sanitized tool timelines, session summaries, the forensic analysis, the held-out tests, and machine-readable results. The [research report](https://github.com/MAJORminorStudio/devin-agent-benchmark/blob/v1.0.0/reports/swe-2-medium-vs-max-research-report.md) and [forensic analysis](https://github.com/MAJORminorStudio/devin-agent-benchmark/blob/v1.0.0/reports/experiment-002-forensic-analysis.md) provide the narrative and observable-metrics records. The [E001 artifacts](https://github.com/MAJORminorStudio/devin-agent-benchmark/tree/v1.0.0/artifacts/experiment-001) and [E002 artifacts](https://github.com/MAJORminorStudio/devin-agent-benchmark/tree/v1.0.0/artifacts/experiment-002) preserve the per-run evidence. Held-out tests were hidden during execution and published afterward with the research evidence.

MAJOR//minor's research identity depends on that inspectability. A result like this one should be readable from the traces, including the failure we had to correct. The tqdm split can be checked against the held-out test and both patches in the public artifacts. The 38× file-change ratio can be checked against the source-only diffs. The jump from 0/5 to 9/10 can be checked against the rejected tool calls from E001.

Readers should be able to challenge the interpretation without taking our word for the traces.

## The question a 5-to-4 split does not settle

Five cases cannot rank Medium against Max. They can identify a pattern worth testing at a larger scale: in this pilot, Max did more observable work across the paired tasks, consumed substantially more model activity, and did not increase the aggregate repair count.

The next measurement is whether that pattern survives a much larger experiment. Does increasing reasoning effort reliably improve autonomous software repair, or is there a task-complexity point where additional exploration is mostly additional cost?

That is what a larger study should test.
