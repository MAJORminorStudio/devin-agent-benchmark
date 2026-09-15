# Experiment 005 Case Design

E005 is a deliberately harder stress set, not a cosmetic refresh of E003 or
E004. The five projects are small enough to inspect locally, but their visible
failures sit at the boundary between ordinary components. Four of five cases
require tracing at least three implementation modules; three reference repairs
touch two source files.

| Case | Failure class | Modules/subsystems | Visible symptom | Held-out behavioral contract | Reference breadth |
|---|---|---|---|---|---|
| E005-H01 | Dependency graph and transitive cache invalidation | graph, recursive resolver, plan cache, publication facade | A published plan stays on an old leaf value after an indirect dependency changes. | Shared and nested consumers refresh after leaf changes; dependency rewiring refreshes the old root; unrelated updates remain cache-safe. | 2 source files, +5/-8 (13 changed lines) |
| E005-H02 | Async cancellation and worker lifecycle consistency | job state machine, executor, active-slot accounting, pending queue | A cancelled running job releases capacity but remains recorded as running. | Cancellation is terminal, a queued successor runs, queued cancellation is idempotent, and success/failure records remain unchanged. | 1 source file, 3 added lines |
| E005-H03 | Incremental framed-protocol parsing and recovery state machine | fragmented decoder, malformed-input recovery, session lifecycle, command router | A valid command after a malformed frame is lost or reported as unusable. | Recovery works across read boundaries, preserves frame order, and handles multiple valid frames after malformed or oversized input. | 2 source files, 2 added/4 deleted lines |
| E005-H04 | Transactional multi-stage operation and compensation ordering | inventory, billing, order lifecycle, outbox, compensation log | A notification failure leaves stock, payment, and order state inconsistent. | Rollback restores capacity for a following purchase, unwinds in dependency order, and leaves payment-decline and success behavior intact. | 1 source file, 1 added/1 deleted line |
| E005-H05 | Event subscription lifecycle and reentrant dispatch | subscription registry, event bus, append-only store, derived projection | Starting a projection twice applies one event twice. | Lifecycle start/stop is idempotent, dispatch uses a stable current subscriber set, late subscriptions wait for the next event, and once listeners fire once. | 2 source files, 4 added/3 deleted lines |

## Expected investigation paths

These are evaluator-side construction notes and are not copied into an agent
workspace.

- H01: follow a publication request through the facade, resolver, cache entry,
  and dependency graph; compare the revisions used by each cache layer after a
  transitive update. A direct-only invalidation repair is intentionally not
  enough for the publication facade and shared consumers.
- H02: trace cancellation from the scheduler into the asyncio task, then into
  the executor's exception boundary and registry state transition. Verify that
  releasing a worker slot and recording a terminal lifecycle state are separate
  obligations; a scheduler-only status assignment can leave the worker path
  inconsistent.
- H03: model the decoder buffer at header, body, malformed-body, and recovery
  boundaries, then trace emitted events through the session state machine to
  the router. A parser-only repair can preserve bytes while the session still
  rejects the first valid message after recovery.
- H04: enumerate the forward stages and compensation actions, then inspect the
  ownership dependency between the order record and its reservation. The
  failure is only apparent after the outbox boundary; a local stock or payment
  workaround does not establish the required unwind order or preserve retry
  capacity.
- H05: trace projection lifecycle calls into the subscription book and follow
  a callback that changes subscriptions during dispatch. A start guard alone
  does not define the current-dispatch snapshot; a bus-only snapshot alone does
  not prevent duplicate projection ownership.

## Agent-facing evidence

Each task has one visible public test that demonstrates a real user-facing
failure and a short task prompt naming the behavior to restore. Public tests do
not contain evaluator scenarios, reference values for all branches, expected
patches, or construction notes. The evaluator has separate behavioral and
regression suites and accepts any implementation that satisfies those
observable contracts.

The projects contain no benchmark names, model names, intentional-bug comments,
solution breadcrumbs, external services, network requirements, large generated
files, timing assumptions, or computationally expensive operations.
