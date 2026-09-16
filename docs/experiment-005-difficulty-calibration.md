# Experiment 005 Difficulty Calibration

E005 is calibrated manually against the historical E002 and novel E004
moderate baselines. No Devin, SWE-2, or other autonomous coding agent was used
to calibrate, inspect, or pre-solve any case. The assessment is structural and
predictive; it is not a claim about realized model success.

## Baselines

E002’s five historical repairs mostly centered on one production file and
small local behavior changes. Its selected records were black-16 (112
checkout files, 1 relevant production file, +14/-1), fastapi-3 (686, 1,
+25/-7), scrapy-3 (473, 1, +5/-2), tqdm-5 (39, 1, +7/-6), and tornado-13
(295, 1 source file plus a test-side oracle change, +4/-1).

E004’s five novel repairs used 17–21-file workspaces, 2–3 relevant modules,
and +3/-0 to +10/-3 reference changes. They were useful moderate controls, but
their contracts and state paths were intentionally narrower than the E005
selection.

The E002 longest observed run was 1,380.464 seconds; E005’s 5,400-second
ceiling is an execution allowance, not a difficulty score.

## Case-level structural calibration

Scores are manual ordinal estimates: 1 = low, 3 = E002-like, and 5 = clearly
beyond the E002 baseline. Counts refer to relevant implementation files or
conceptual modules, not repository size. “Visible-test specificity” is scored
in the opposite direction: 5 means the public evidence is useful but does not
point to one obvious local patch.

| Case | Provenance | Relevant files / modules | Symptom → root distance | Depth | Competing hypotheses | Patch breadth | Contract / regression | Incomplete-repair opportunity | Band |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| K01 FastAPI-1 | historical | 4 / 4 | 5 | 4 | 4 | 4 | 5 / 4 | 5 | upper-hard |
| K02 Luigi-23 | historical | 2 / 3 | 5 | 4 | 4 | 2 | 4 / 4 | 4 | middle-hard |
| K03 Tornado-6 | historical | 2 / 4 | 5 | 5 | 5 | 4 | 5 / 4 | 5 | upper-hard |
| K04 Tornado-10 | historical | 2 / 2 | 4 | 4 | 4 | 3 | 4 / 4 | 4 | middle-hard |
| K05 thefuck-16 | historical | 4 / 3 | 4 | 3 | 3 | 3 | 4 / 3 | 4 | lower-hard |
| H01 feature-plan | constructed | 4 / 4 | 5 | 4 | 4 | 4 | 5 / 4 | 5 | upper-hard |
| H02 work-queue | constructed | 4 / 4 | 4 | 4 | 4 | 2 | 4 / 4 | 4 | middle-hard |
| H03 wire-relay | constructed | 3 / 4 | 5 | 5 | 5 | 4 | 5 / 4 | 5 | upper-hard |
| H04 order-flow | constructed | 6 / 5 | 5 | 5 | 4 | 2 | 5 / 4 | 5 | middle-hard |
| H05 event-ledger | constructed | 4 / 4 | 4 | 4 | 4 | 4 | 5 / 5 | 5 | middle-hard |

Patch breadth is a signal, not the target: K02 and H02 are deliberately
compact lifecycle/configuration cases, while K01’s broad patch does not by
itself establish difficulty. The selection is balanced by mixing historical
and constructed provenance, lifecycle/state-machine and data-flow defects,
and compact versus broad repairs.

## Why the selected cases exceed E002

| Cases | Structural evidence | Why a local symptom patch is insufficient |
|---|---|---|
| K01 | Decorator defaults, route state, response serialization, and direct encoding form a four-file propagation path. | Fixing only the encoder or only the route leaves one caller contract stale; direct, nested, and router-backed held-out behavior separates those repairs. |
| K02 | Factory defaults, scheduler configuration, pruning, and external-task completion form a three-step control path. | Enabling a flag in one construction path leaves explicit configuration or ordinary dependency scheduling broken. |
| K03 | Tornado and asyncio own different close paths while sharing a persistent adapter map. | Cleaning only one owner’s close path leaves stale wrappers for the other path; repeated close and new registration expose the split. |
| K04 | Generic RequestHandler cleanup and WebSocket-specific status/close lifecycle must coordinate. | Breaking cycles immediately makes the visible render test fail; unconditional deferral leaks ordinary/failed-handshake handlers, so both paths are held out. |
| K05 | Bash, Zsh, and Fish generators express one correction-context contract through shell evaluation rules. | Reordering one alias or one shell does not repair the cross-shell environment contract, while parser/conversion regression tests reject collateral changes. |
| H01 | Two memoization layers sit above a reusable transitive dependency graph. | Refreshing only the resolver or only the facade leaves another consumer stale; shared roots and rewiring expose that split. |
| H02 | Cancellation crosses an async task boundary, exception provenance, worker-slot release, and registry state machine. | A scheduler-only terminal-state assignment can satisfy the visible state assertion while losing cancellation provenance; held-out successor and ordinary-failure checks cover it. |
| H03 | Fragment boundaries, malformed-body consumption, session recovery, and command dispatch interact in one stream. | Preserving buffered bytes without resetting recovery still rejects the next command; resetting recovery without fixing decoder consumption still loses bytes. |
| H04 | A final outbox failure must unwind three earlier stateful subsystems in dependency order. | Releasing stock or voiding payment locally cannot restore order lifecycle and subsequent capacity; compensation order and a follow-up purchase distinguish incomplete fixes. |
| H05 | Projection ownership and event-bus dispatch semantics are separate lifecycle contracts, with callbacks mutating subscriptions during iteration. | A start guard prevents duplicate totals but not dispatch mutation bugs; a snapshot prevents skipped listeners but not duplicate ownership. |

## Balance and residual risk

The historical and constructed halves occupy broadly comparable hard ranges:
K01/K03/H01/H03 are upper-hard, K02/K04/H02/H04/H05 are middle-hard, and K05
is lower-hard. This is not an assertion that all ten have equal difficulty.
The historical half is harder than E002 in aggregate because K01–K04 include
multi-module propagation or lifecycle ownership, and every K case has a
behavioral contract broader than its visible oracle. The constructed half
retains the original E005 stateful interactions and independent hidden
contracts.

K05 is the clearest “possibly too easy” case: a strong agent may recognize the
shell-evaluation ordering quickly. H04 is also compact, but its compensation
ordering and follow-up-capacity contract provide a distinct stateful check.
Those cases remain as lower/middle-hard anchors rather than being inflated by
large repositories, obsolete dependencies, timing thresholds, or network
requirements. The rejected Ansible-13 alternative was removed for exactly that
reason: its 17,954-file sanitized checkout made repository bulk a material
confound.

## H02 shortcut review

The apparent scheduler-only shortcut was tested in a disposable copy before
freeze. It passed the public test and regression suite, but failed the held-out
requirement that the terminal record preserve an `asyncio.CancelledError`
instance. The canonical H02 scheduler files are identical between buggy and
fixed trees; H02 remains unchanged and its executor-side cancellation handling
is the validated repair. The direct review is recorded privately in
`.benchmarks/experiment-005-private/h02-review.json`.

These estimates do not predict which effort will win, how long an agent will
reason, or whether a historical case appeared in training data. They establish
that E005 is structurally more coupled and contract-broad than E002 without
manufacturing difficulty through repository size or setup pain.
