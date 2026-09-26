# Devin SWE-2 benchmark follow-up v5.0.0

This versioned follow-up adds the E007 effort-level experiment and E008 replication/stability analysis. It preserves V4 and the historical E007 evaluator results.

## Included

- E007's 90 agent sessions across 30 cases and three effort levels.
- Formal correction note documenting the stale `.pyc` evaluator-staging defect and the clean re-evaluation of preserved E007 workspaces.
- Both E007 result sets: historical 16/30, 18/30, 18/30; clean recheck 22/30, 24/30, 24/30.
- Original-to-clean-E007 case-level agreement: Medium 24/30 and Max 25/30.
- E008's 33 targeted repeat sessions across nine selected cases and 11 case/effort conditions.
- Five-observation sequences, sanitized machine-readable run tables, protocols, figures, and checksums.

## Principal findings

High and Max tie at 24/30 in the clean E007 evaluation; Medium is 22/30. Six of 11 selected conditions were unanimous over three new trials and five were mixed. The new targeted trials passed 19/33 times; the 11 five-observation sequences contain 30/55 passes. These selected repeats are not a new full-benchmark score and do not establish a general effort reliability gap.

The evidence cannot distinguish ordinary stochastic variation from temporal/backend change. One High E007 run lacks wrapper timing metadata. Actual monetary cost is unknown.

## Package

See `PUBLICATION.md`, `METHODOLOGY.md`, `LIMITATIONS.md`, `CORRECTION.md`, `docs/`, `data/`, and `figures/`. This local draft is intended to become the asset for a future GitHub release at tag `v5.0.0`; no tag or release has been created.
