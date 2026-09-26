> **Publication context:** This frozen pre-run document records the catalog-based expectation and budget controls as they were written before execution. They are planning assumptions only, not billed or actual cost. No account billing evidence was available; actual monetary cost is unknown.

# E007 Preregistration

**Status:** Frozen before new benchmark execution. The initial registration timestamp and file checksums are recorded in `checksums/`.

## Questions and hypotheses

- **Q1:** Do SWE-2 Medium and Max reproduce the original case outcomes?
- **Q2:** How does SWE-2 High perform relative to Medium and Max?
- **Q3:** Does the effort effect differ across moderate, hard, and very-hard tasks?
- **Q4:** Does higher effort increase steps, runtime, tokens, or cost without improving success on easier tasks?
- **Q5:** On very-hard tasks, does higher effort improve success enough to justify additional resource use?

The prior observed tier pattern (Medium/Max: moderate 10/8, hard 7/6, very-hard 7/9) motivates a directional hypothesis that additional effort may be more useful at the very-hard tier and less useful on moderate tasks. This is a hypothesis only; analyses will report the outcomes as observed and will not force this pattern.

## Frozen variables

Primary independent variable: `reasoning_effort ∈ {medium, high, max}`, operationalized by explicit Devin model IDs `swe-2-medium`, `swe-2-high`, and `swe-2-max`.

Primary dependent variable: the existing frozen `TASK_SUCCESS` result.

The exact 30 cases, difficulty tiers, prompts, source commits/snapshots, held-out tests, regression tests, evaluator configuration, and original outcomes are in `E007-MANIFEST.json`. There are exactly 10 moderate, 10 hard, and 10 very-hard cases. No case selection depends on historical outcomes. Supplemental E003 cases are excluded.

All other variables are held fixed wherever technically possible: permissions, isolation policy, runtime, interventions, success definition, and evaluation. Each run is fresh and receives no substantive human assistance. No prompt repair, task modification, or ordinary-failure retry is allowed. Infrastructure retries must follow the parent protocol and be logged. One run per case-condition; no stochastic repeats.

## Planned analyses

1. **Replication:** Medium and Max original-vs-E007 scores; both solved, both failed, original-only, E007-only, exact case agreement, overall and per tier.
2. **Three-way outcomes:** overall and tier solve rates; pairwise both-solve / first-only / second-only / both-fail matrices; unique solves by effort; effort transitions.
3. **Paired statistics:** Cochran's Q across three conditions and exact two-sided pairwise McNemar tests; absolute solve-rate differences and confidence intervals suitable for small samples. Report overall n=30 and each tier n=10. Statistical significance will not be overstated.
4. **Efficiency:** mean/median runtime, steps, input/output/total tokens, direct cost when reported, cost per attempted/successful task when defined, and steps before first edit; all attempts and successful runs separately. High/Medium and Max/Medium ratios where denominators permit.
5. **Behavior:** trace-based inspection of cases whose success changes with effort. Code success labels before trace interpretation. Distinguish observed behavior, plausible interpretation, and unresolved cause.

No scoring revisions, post hoc exclusions, or new confirmatory endpoints are permitted. Infrastructure and intervention cases are reported separately under the frozen protocol.

## Cost rule

The current authenticated Devin model catalog displayed all three SWE-2 model variants as Free. Expected direct model overage is therefore $0 based on the inspected catalog; account-side usage may still be consumed. Stop before accepting any unexpected direct overage and do not exceed $100.
