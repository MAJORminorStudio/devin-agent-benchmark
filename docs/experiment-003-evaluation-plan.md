# Experiment 003 Evaluation Plan

## Frozen scoring

For every closed run, the evaluator records three independent result groups:

- public: the visible test supplied in the sanitized workspace;
- held-out: the evaluator-only behavioral test, run only after session close;
- regression: the evaluator-only practical neighboring behavior check.

`TASK_SUCCESS` is `1` exactly when public, held-out, and regression are all
passing. Otherwise it is `0` for a valid evaluation. If evaluator setup or
execution is impossible because of evaluator infrastructure, the result is
`EVALUATION_ERROR` and is not silently converted to failure.

## Case-level test structure

Each of E003-N01 through E003-N05 has one evaluator-only primary behavioral
test and one evaluator-only adjacent regression test. Their filenames,
assertions, commands, and expected values are private until all ten runs are
closed. The tests are behavior-oriented and independent of the reference
patch. The reference implementation is used only to establish expected
fixed-side behavior and for post-closure comparison.

## Planned combined analysis

Report E003 first as five unique novel cases, then combine it descriptively
with E002's five historical cases. For each condition report E003 successes
out of 5 and combined successes out of 10. Report paired outcomes as both
success, Medium-only, Max-only, or both fail. Report total/mean/median wall
time, steps, tool calls, prompt tokens, completion tokens, source patch size,
and workspace/generated churn where observable. Compare historical and novel
subgroups descriptively without treating their difference as causal evidence.

These metrics and outcome categories are frozen before execution; later
results cannot change which measures are emphasized.
