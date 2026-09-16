# Experiment 005 Protocol

Status: authoritative hard-tier freeze, validated and ready for a separately
authorized launch. No Devin or SWE-2 execution has occurred.

## Primary question

> Within the HARD tier, how do `swe-2-medium` and `swe-2-max` compare on
> complete behavioral repair across five known historical BugsInPy defects and
> five newly constructed withheld defects?

E005 is the balanced hard tier: five public/known historical cases (`K01`-
`K05`) plus five newly constructed/withheld cases (`H01`-`H05`), for ten unique
bugs and twenty runs. Every case appears exactly once at each reasoning level.
E002 historical plus E004 novel is the primary moderate comparator; E003 is
supplemental evidence and is not part of that balanced denominator.

The original E005 freeze contained only the five novel H cases. It was never
executed. This expanded K+H freeze supersedes its ten-run order before any
E005 execution and is the sole authoritative launch specification.

## Cases and intervention policy

`manifests/experiment-005-config.json` is the case and infrastructure source
of truth. `K01`-
`K05` are intentionally known historical BugsInPy defects; `H01`-
`H05` remain the original newly constructed/withheld cases. Historical source
revisions and upstream tests are public provenance, while fixed trees,
solution-bearing patches, and E005 evaluator material remain private.

The two conditions are `M = swe-2-medium` and `X = swe-2-max`. Fusion is
excluded. Prompts are byte-identical within each case pair. There is no
substantive human or Codex assistance and no retry for an ordinary task
failure. The agent session closes before evaluator access.

`TASK_SUCCESS = 1` exactly when public, held-out behavioral, and regression
suites all pass. Evaluator setup or execution faults are recorded separately as
`EVALUATION_ERROR`.

## Frozen run order

The original H-only order is superseded. The expanded order uses
`Python random.Random(20260918).shuffle` over all twenty case-condition pairs.
It has ten M and ten X runs, interleaves conditions and provenance, and does not
run either condition as a block.

| # | Run | Provenance | Condition | Model |
|---:|---|---|:---:|---|
| 1 | E005-K04-X | historical | X | swe-2-max |
| 2 | E005-K05-M | historical | M | swe-2-medium |
| 3 | E005-K02-X | historical | X | swe-2-max |
| 4 | E005-K01-M | historical | M | swe-2-medium |
| 5 | E005-H05-X | novel | X | swe-2-max |
| 6 | E005-K04-M | historical | M | swe-2-medium |
| 7 | E005-H05-M | novel | M | swe-2-medium |
| 8 | E005-H04-X | novel | X | swe-2-max |
| 9 | E005-H03-X | novel | X | swe-2-max |
| 10 | E005-K02-M | historical | M | swe-2-medium |
| 11 | E005-H03-M | novel | M | swe-2-medium |
| 12 | E005-K03-X | historical | X | swe-2-max |
| 13 | E005-H01-M | novel | M | swe-2-medium |
| 14 | E005-H02-M | novel | M | swe-2-medium |
| 15 | E005-H04-M | novel | M | swe-2-medium |
| 16 | E005-H01-X | novel | X | swe-2-max |
| 17 | E005-H02-X | novel | X | swe-2-max |
| 18 | E005-K01-X | historical | X | swe-2-max |
| 19 | E005-K03-M | historical | M | swe-2-medium |
| 20 | E005-K05-X | historical | X | swe-2-max |

## Resources and isolation

Each run retains the proposed 5,400-second maximum. Runs are sequential
(`parallel_runs = 1`), with zero ordinary retries and no agent step or token
cap. A process exit ends the run; a watchdog or service timeout is an
infrastructure result only when the harness or service is at fault.

The frozen container contract is the proven E004 Docker architecture:

- frozen image `devin-e002:3000.10.21@sha256:bb045374bc655c185cced99a6cb769a6695c88527fb432456eb8e0d6dd0e4bb6`;
- Linux/arm64, dangerous permission mode with effective Bypass;
- read-only root, all capabilities dropped, `no-new-privileges`, four CPUs,
  4 GiB memory, and 512 PID limit;
- internal `e002-internal` network through `http://egress-proxy:3128`, with no
  direct internet access;
- no Docker socket, host/control-repository mount, paired workspace, or prior
  result exposure;
- one fresh sanitized buggy workspace per run, read-write, plus only the
  minimum read-only Devin credential file;
- case dependencies are preinstalled in the execution image; the agent may
  not install dependencies;
- evaluator and fixed/reference material are outside the container and become
  reachable only after the agent session closes.

The dry-run planner in `scripts/experiment_005_container.py` must validate the
selected image, network, resource limits, model, and run ID before any future
launch. This task did not pass its execution flag.

## Pre-launch gates and stop condition

Before launch, rerun the private validator and require all ten buggy/fixed
ground-truth matrices, deterministic repeats, twenty leak audits, prompt-pair
identity checks, evaluator smoke tests, static checks, and Markdown/security
checks to remain green. Any change to a case, prompt, evaluator, configuration,
isolation value, or run order creates a new freeze record.

After this freeze, stop. Launching any of the twenty runs requires separate
authorization.
