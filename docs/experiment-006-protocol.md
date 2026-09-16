# Experiment 006 Protocol

Status: authoritative VERY-HARD capability-frontier infrastructure re-freeze.
The original freeze was never executed: its dependency gate failed before
Run 1, and no Devin or SWE-2 run has been made for E006. The benchmark cases,
prompts, evaluators, behavioral contract, order, assignments, and success rule
are unchanged and the repaired runtime is ready for a separately authorized
launch.

## Question and unit

E006 asks whether `swe-2-medium` and `swe-2-max` differ on complete behavioral
repair at a capability frontier where the visible symptom and the root cause
cross module, lifecycle, or state boundaries. The balanced tier contains ten
unique defects: five historical/public BugsInPy cases (`K01`-`K05`) and five
newly constructed/withheld cases (`H01`-`H05`). Each case is run exactly once
at each condition, for twenty independent runs total. The historical and
novel halves are analyzed separately and together; n=5 per paired comparison
is descriptive, not a basis for significance claims.

The experimental unit is one case/condition pair from a fresh sanitized buggy
workspace. A pair shares one byte-identical task prompt, but receives a new
workspace and fresh output directory. The agent may inspect and modify only
that workspace during the session. The evaluator opens only after the session
closes.

## Intervention, scoring, and capture

Conditions are `M = swe-2-medium` and `X = swe-2-max`; fusion is disabled. No
substantive human or Codex assistance is allowed, and ordinary task failures
are not retried. Authentication or infrastructure recovery is logged as an
infrastructure event and cannot change the task prompt or workspace.

`TASK_SUCCESS = 1` if and only if the public test, private held-out behavioral
tests, and private regression tests all pass. Evaluator setup or service faults
are recorded as `EVALUATION_ERROR`, not silently converted to task failure.

The run ledger captures the exact prompt hash, model/configuration, UTC start
and end, wall time, observable steps/tool calls/tokens/usage/cost/ACUs when
available, stdout/stderr/session export, termination reason, final source
patch, generated/environment churn, evaluator results, and interventions.

## Frozen order and resource contract

`manifests/experiment-006-runs.json` is authoritative. Its order is the
20-item output of `random.Random(20260926).shuffle` over all case-condition
pairs. It has ten M and ten X runs, interleaves provenance and conditions, and
does not run either condition as a block. Runs are sequential with zero
ordinary retries. The maximum wall time is 7,200 seconds; there is no agent
step or token cap.

The selected image is the immutable derived runtime
`devin-e006:3000.10.21-r7@sha256:7557a0bc640492d8f77f271ebafc6402733fa0ba843c344f74ab613b94416699`,
built from the exact original base
`devin-e002:3000.10.21@sha256:bb045374bc655c185cced99a6cb769a6695c88527fb432456eb8e0d6dd0e4bb6`
on Linux/arm64. It contains pinned case-specific historical Python
environments; mechanical `PATH`/`LD_LIBRARY_PATH` selection is recorded in
the configuration and does not change the task prompt. The container contract
remains read-only root, all capabilities dropped, `no-new-privileges`, four
CPUs, 4 GiB memory, 512 PIDs, no Docker socket, no host home or
control-repository mount, one fresh read-write buggy workspace, one fresh
artifact directory, and one minimum read-only Devin credential file. The
agent network remains `e002-internal` through `http://egress-proxy:3128`;
direct internet access and dependency installation during the agent session
are disallowed.

The dry-run planner in `scripts/experiment_006_container.py` validates image,
network, resources, model, run ID, mounts, and the paid-execution guard. This
freeze work invokes it only in dry-run mode. The control-side
`scripts/validate_experiment_006_runtime.py` exercised all ten buggy/fixed
trees and private evaluators in 40 fresh containers (two repetitions), with
signatures matching the pre-freeze ground truth. Any actual launch requires a
new explicit authorization.

## Stop condition

After commit and push, stop. Do not invoke Devin, SWE-2, the container
execution path, or any evaluator against an agent-produced patch in this
task. A later launch must rerun the private preflight and create a new ledger
only if a frozen input changed.
