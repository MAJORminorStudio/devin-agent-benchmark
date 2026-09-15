# Experiment 005 Difficulty Calibration

E005 is calibrated manually against the known historical E002 baseline. No
Devin, SWE-2, or other autonomous coding agent was used to calibrate, inspect,
or pre-solve the cases. The comparison is structural and predictive; it is not
a claim about realized model success before execution.

## Baseline

E002's five repairs were real historical BugsInPy defects. The reference
repairs centered on one production source file in four cases, with Tornado
also carrying a test-side reference change. The observed source reference
patches were 2 to 32 changed lines. The E002 tasks were meaningful framework
defects, but the visible failure generally localized to a single implementation
area and did not require reconstructing a new multi-component contract.

The E002 longest observed run was 1,380.464 seconds; E005's frozen ceiling is
5,400 seconds. Runtime allowance is preparation, not a difficulty metric.

## Detailed structural calibration

Scores are manual ordinal estimates: 1 = low, 3 = E002-like, and 5 = clearly
beyond the E002 baseline. Counts are approximate relevant implementation files
or conceptual modules, not repository size. “Visible-test specificity” is
scored in the opposite direction: 5 means the public evidence is useful but
does not point to a single local patch.

| Dimension | E002 baseline | H01 | H02 | H03 | H04 | H05 |
|---|---:|---:|---:|---:|---:|---:|
| Relevant-file count | 1–2 | 4 | 4 | 3 | 6 | 4 |
| Interacting-module count | 1–2 | 4 | 4 | 4 | 5 | 4 |
| Symptom/root-cause distance | 2 | 5 | 4 | 5 | 5 | 4 |
| Data/control-flow depth | 2 | 4 | 4 | 5 | 5 | 4 |
| Plausible competing hypotheses | 2 | 4 | 4 | 5 | 4 | 4 |
| Reference patch breadth | 1–2 | 4 | 2 | 4 | 2 | 4 |
| Regression surface | 2 | 4 | 4 | 4 | 4 | 5 |
| Behavioral contract breadth | 2 | 5 | 4 | 5 | 5 | 5 |
| State required to understand | 2 | 5 | 5 | 5 | 5 | 5 |
| Subsystems involved | 1–2 | 4 | 4 | 4 | 5 | 4 |
| Visible-test specificity | 2 | 5 | 4 | 5 | 4 | 5 |
| Opportunity for incomplete local repair | 2 | 5 | 4 | 5 | 5 | 5 |

### Why each case is expected to exceed E002

| Case | Evidence beyond E002 | Why a local symptom patch is insufficient |
|---|---|---|
| H01 | Two independent memoization layers sit above a reusable transitive graph; the root can remain unchanged while a leaf revision changes. | Refreshing only the resolver or only the facade leaves the other cache stale; held-out shared consumers and rewiring expose that split. |
| H02 | Cancellation crosses a task boundary, an exception hierarchy boundary, a worker-slot release, and a registry state machine. | Assigning a cancelled state in the scheduler can make the public assertion pass while the executor path still leaves inconsistent terminal/error data; held-out successor and ordinary-failure checks cover this. |
| H03 | Fragment boundaries, malformed body consumption, session recovery, and command dispatch interact in one stream. | Preserving buffered bytes without resetting session recovery still rejects the next command; resetting the session without fixing decoder consumption still loses bytes. |
| H04 | A final outbox failure must unwind three earlier stateful subsystems in dependency order. | Releasing stock or voiding payment locally cannot restore the order lifecycle and subsequent capacity; the audit order and follow-up purchase distinguish incomplete compensation. |
| H05 | Projection ownership and event-bus dispatch semantics are separate lifecycle contracts, with callbacks mutating subscriptions during iteration. | A start guard prevents duplicate totals but does not stabilize the current dispatch; a tuple snapshot prevents skipped listeners but does not prevent duplicate ownership. |

## Pre-freeze challenge

The proposed set was challenged against the question: “Could a strong coding
agent read the failing assertion, jump to one function, and make a local patch
that solves most cases?” The answer is no for the set as frozen: H01, H03, H04,
and H05 each have a public-visible partial repair that is rejected by held-out
behavior, and H02 requires tracing scheduler, executor, and registry lifecycle
state even though its minimal patch is compact. Four cases require multiple
modules and three reference repairs span at least two source files.

H02 is the leanest case and its three-line reference repair is a deliberate
lower-bound async lifecycle stressor. It is the one case most likely to be
underestimated from patch size alone. Before execution, a review that finds
its public contract can be satisfied by a scheduler-only status assignment
would require redesign; the current held-out terminal error and successor
checks are the guard against that local workaround.

## Limits of the calibration

These estimates do not predict which effort will win, how long an agent will
reason, or whether the cases are absent from training data. They establish
that E005 is structurally more coupled and contract-broad than E002 without
manufacturing difficulty through repository size, dependencies, timing,
network access, obscure syntax, or adversarial wording.
