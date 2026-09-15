# Experiment 003 Case Design

Five independent, compact Python projects were constructed in private
staging. They use ordinary package and test layouts, no external services, no
network access, and no benchmark-specific language in agent-visible files.

| Case | Target class | Manual calibration |
|---|---|---|
| E003-N01 | Filesystem/path semantics | One implementation module and one visible test; requires reasoning about resolved paths, directory boundaries, and links. |
| E003-N02 | Stateful/cache invalidation | One implementation module and one visible test; requires tracing a warmed derived view across mutation. |
| E003-N03 | Nested data transformation | One implementation module and one visible test; requires preserving container shape while recursively converting values. |
| E003-N04 | Async/concurrency/lifecycle | One implementation module and one visible test; requires understanding awaited worker cleanup and idempotent close behavior. |
| E003-N05 | Protocol/parser/state machine | One implementation module and one visible test; requires following incremental parser state and recovery from an incomplete record. |

Each case has a normal README, a minimal package declaration, a visible test,
one evaluator-only behavioral test, and one evaluator-only regression test.
The visible test exposes a legitimate user-facing symptom without specifying
the entire behavioral contract. The evaluator tests accept behavioral
equivalence rather than a particular patch shape.

Difficulty was calibrated manually, without Devin, SWE-2, or another coding
agent. The projects are intentionally bounded and deterministic; they are not
syntax puzzles, external-service tasks, or copies of the historical BugsInPy
cases.
