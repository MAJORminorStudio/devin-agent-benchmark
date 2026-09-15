# Experiment 005 Evaluation Plan

## Frozen scoring

Each closed run is evaluated in three independent groups:

- public: the visible test supplied in the sanitized workspace;
- held-out: evaluator-only behavioral tests, accessed only after session close;
- regression: evaluator-only neighboring behavior checks.

`TASK_SUCCESS = 1` exactly when public, held-out, and regression all pass. An
evaluator setup or execution failure is `EVALUATION_ERROR`, not an agent
failure and not a silent fail.

## Held-out coverage

The held-out suites are behavior-oriented and distinguish a visible-symptom
patch from a complete repair:

- H01 exercises shared roots, indirect leaf changes, and dependency rewiring.
- H02 exercises active cancellation, the next queued job, repeated queued
  cancellation, and terminal error state preservation.
- H03 exercises fragmented malformed input, recovery followed by multiple
  frames, ordering, and oversized-frame recovery.
- H04 exercises capacity restoration, compensation order, and payment decline
  without an order record.
- H05 exercises callback-driven subscription changes, late subscribers,
  once-only delivery, and projection stop/restart behavior.

Regression suites cover unchanged behavior such as unrelated cache updates,
ordinary success/failure, unknown commands, non-target topics, and normal
successful transactions. They do not inspect implementation identity.

## Validation boundary

For each case the private validator runs public, held-out, and regression tests
against both the buggy and fixed trees. The expected matrix is buggy failure on
the target contract and fixed success on all three groups. One H03 regression
also fails on the buggy tree because malformed-frame recovery leaves the
session in the wrong state; this is intentional and deterministic.

The fixed-side reference tree establishes solvability. Reference patches are
minimal technically correct repairs and are retained only in private staging.
