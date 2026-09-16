# Experiment 005 Evaluation

## Frozen scoring

Each of the twenty closed runs is evaluated in three independent groups:

1. `PUBLIC`: the upstream visible test selected for a K case or the visible
   test supplied with an H workspace;
2. `HELD-OUT`: evaluator-only behavioral tests that exercise the broader
   contract without requiring a particular patch;
3. `REGRESSION`: evaluator-only neighboring behavior that must remain intact.

`TASK_SUCCESS = 1` if and only if all three groups pass. A setup, evaluator,
or infrastructure fault is `EVALUATION_ERROR`, not a task failure. The
evaluator opens only after the disposable agent session closes.

## Historical cases

The public group uses the pinned BugsInPy regression test, with no fixed tree or
solution metadata overlaid. The private held-out suites deliberately cover
behavior beyond the visible assertion:

| Case | Public symptom | Held-out behavioral contract | Regression contract |
|---|---|---|---|
| E005-K01 FastAPI-1 | response-model exclusion options are rejected or do not reach serialization | default, unset, and None filters compose for direct encoding and router-backed response models | ordinary encoding and exclude-unset behavior remain unchanged |
| E005-K02 Luigi-23 | external dependency retry cannot use the required local scheduler pruning path | factory and explicit scheduler configuration both enable pruning before work selection | ordinary dependency ordering remains available |
| E005-K03 Tornado-6 | closed asyncio-backed wrappers remain in the adapter map | Tornado-owned close removes its wrapper; asyncio-owned close is cleaned on the next adapter creation; open registration remains valid | new loops can still be created and registered |
| E005-K04 Tornado-10 | an established WebSocket loses template state before close | established WebSockets defer cycle cleanup until close, while failed handshakes still clean up | WebSocket remains a RequestHandler and ordinary status behavior remains available |
| E005-K05 thefuck-16 | Bash and Zsh aliases export correction context too early | Bash, Zsh, and Fish scope correction context at command execution | alias parsing and simple shell conversion remain unchanged |

The K held-out tests accept any implementation satisfying these observable
contracts. They do not compare a candidate patch with the upstream patch.
They use local mocks or standard-library behavior; no network, giant suite,
timing threshold, or external service is required.

## Novel cases

H01-H05 retain their original private evaluator and expected matrix:

| Case | Held-out behavior | Regression behavior |
|---|---|---|
| E005-H01 | shared roots, indirect leaf changes, and dependency rewiring refresh all consumers | unrelated updates preserve valid cache entries; cycles and unknown definitions remain rejected |
| E005-H02 | active cancellation is terminal, preserves cancellation provenance, releases the slot, and allows the next queued job; queued cancellation is idempotent | success and failure records remain terminal and balanced |
| E005-H03 | fragmented malformed input recovers, preserves frame order, and processes multiple subsequent frames | unknown commands and oversized-frame recovery remain supported |
| E005-H04 | rollback restores capacity and unwinds child resources before parent resources | payment decline creates no order or stock hold; ordinary success stage order is unchanged |
| E005-H05 | callback-driven subscription changes take effect after the current dispatch and once listeners fire once | projection stop/restart and topic filtering remain correct |

The H cases remain newly constructed/withheld and their source, tests, and
construction notes are not reproduced here.

## Ground-truth matrix and repeat rule

The private validator exercises every public, held-out, and regression group on
both the buggy and fixed tree, twice per tree. The frozen expected matrix is:

| Tree | Public | Held-out | Regression |
|---|---|---|---|
| every K buggy tree | fail | fail | pass |
| every K fixed tree | pass | pass | pass |
| H01, H02, H04, H05 buggy trees | fail | fail | pass |
| H03 buggy tree | fail | fail | fail |
| every H fixed tree | pass | pass | pass |

The H03 regression failure is intentional: its malformed-frame state is part
of the defect's deterministic failure surface. The repeat validator recorded
the same status on both repetitions for all ten cases. It also rebuilt and
audited two sanitized workspace templates per case, one for each planned
condition, yielding twenty passing leak-audit records.

## H02 review

The non-agent review tested the apparent shortcut directly in a disposable
copy: after awaiting cancellation, the scheduler only recorded
`CANCELLED`. That shortcut passed the public test and regression suite but
failed the held-out requirement that the terminal record preserve an
`asyncio.CancelledError` instance. The canonical H02 scheduler files are
identical between buggy and fixed trees; H02 remains unchanged and its
executor-side cancellation handling is the validated repair.
