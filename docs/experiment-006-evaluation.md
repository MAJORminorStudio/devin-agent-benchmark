# Experiment 006 Evaluation Contract

The evaluator is private and remains outside the public repository. It accepts
any source change satisfying behavior, rather than comparing a candidate patch
with the reference diff.

## Three-group score

Every closed run is evaluated independently in three groups:

1. `PUBLIC`: the pinned upstream regression test for K cases or the visible
   unittest suite supplied with an H workspace;
2. `HELD_OUT`: evaluator-only behavioral scenarios that extend beyond the
   visible assertion;
3. `REGRESSION`: neighboring behavior that must remain intact.

`TASK_SUCCESS` is the conjunction of these three groups. A setup, evaluator,
or infrastructure fault is never silently scored as a repair failure.

## Historical behavioral contracts

| Case | Visible oracle | Held-out behavior | Regression |
|---|---|---|---|
| K01 black-6 | target-version parser test | accept `async` as a legacy identifier under Py3.6 and reject it as a Py3.7 keyword | ordinary formatting remains stable |
| K02 PySnooper-1 | source-inspection compatibility adapter | preserve UTF-8 source without a cookie and honor declared Latin-1 | ordinary source tracing remains usable |
| K03 black-23 | Python-2 formatter test | preserve compact `print >>stream` grammar and Python-2/3 parser behavior | modern formatting remains stable |
| K04 thefuck-17 | Bash alias test | discover current aliases and pass them to correction context | ordinary command conversion remains unchanged |
| K05 tqdm-2 | meter-format test | trim ANSI text without duplicating an existing reset | plain display trimming remains unchanged |

The K evaluator runs the same behavior and regression files against each
buggy/fixed tree. The expected ground-truth invariant is buggy failure/fixed
pass for public and held-out behavior, with regression passing on both. The
private ledger records exact statuses and stderr, not just a boolean.

## Novel behavioral contracts

| Case | Held-out behavior | Regression |
|---|---|---|
| H01 feature-store | shared and nested plans refresh after a transitive leaf update; rewiring invalidates the old root; rollback preserves valid cache | unrelated definitions, cycles, and unknown definitions |
| H02 work-queue | cancellation during a later retry owns the current task, is terminal, preserves capacity, and permits queued work | success, permanent failure, and queued-job records |
| H03 wire-relay | malformed and oversized frames recover across fragmentation while preserving order and flow credit | unknown commands and close behavior |
| H04 account-ledger | reentrant listeners observe committed state; current-dispatch membership is stable; once listeners fire once | ordinary balance updates and listener lifecycle |
| H05 profile-runtime | mode and source revision are part of artifact identity; nested serialization does not mutate source | unknown modes and unrelated profiles |

## Ground-truth, repeat, and workspace rules

Before any launch, the private validator must run public, held-out, and
regression groups on every buggy and fixed tree, then repeat the same matrix
from fresh processes. The repeat must match the first result exactly. It also
creates two sanitized agent-workspace templates per case, audits them for
fixed trees, held-out tests, solution patches, private evaluator paths,
benchmark/model names, credentials, control-repository paths, and prior
results, and checks the two prompt bytes per case are identical.

The validated matrix had one known baseline-only exception: H01's buggy
regression tree reports a recursion error for a cycle where the fixed tree
reports the required `ValueError`; this is part of the defect surface, while
the fixed regression suite is green. All other buggy regression groups and all
fixed groups passed. E006 is frozen with zero agent and SWE-2 invocations
before this validation. The validator must fail if an agent executable, model
invocation, paid execution flag, or evaluator overlay is observed.
