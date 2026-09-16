# Project wrap-up: Devin + SWE-2 reasoning effort

## Status

The planned experimental phase is complete. E001 through E006 now form the finished benchmark lineage and final publication. No E007 is created by this wrap-up.

## What each experiment contributed

**E001: protocol boundary.** The initial unattended execution used a permission mode that still required shell confirmation. The ten intended runs received rejected tool calls and produced empty patches. E001 is preserved as methodological provenance, not capability evidence. It established that permission policy and interaction mode are part of the system being evaluated.

**E002: corrected moderate historical baseline.** After repairing the execution boundary inside a disposable isolated environment, E002 evaluated five historical/public BugsInPy defects. Medium completed 5/5 and Max 4/5. It provided the corrected historical baseline for the moderate tier.

**E003: supplemental withheld replication.** E003 added five easier newly constructed/withheld defects. Medium and Max both completed 5/5. It remains supplemental because its task difficulty and role differ from the final three-tier denominator.

**E004: moderate withheld expansion.** E004 added five newly constructed/withheld cases to balance the moderate tier. Combined with E002, the moderate tier contains ten cases, five per provenance, and scores Medium 10/10 versus Max 8/10.

**E005: hard tier.** E005 supplied ten hard cases, balanced across historical/public and withheld provenance. Medium completed 7/10 and Max 6/10. Its pairs included Medium-only, Max-only, both-success, and both-fail outcomes, making it the first tier with a richer disagreement structure.

**E006: very-hard frontier.** E006 supplied ten frozen very-hard cases in a fixed interleaved order. Medium completed 7/10 and Max 9/10. The seven both-success, two Max-only, zero Medium-only, and one both-fail outcomes changed the unique-repair pattern observed in earlier tiers.

## Final primary benchmark

The final denominator is 30 unique bugs and 60 valid paired runs: ten cases and twenty runs in each of three tiers. Every case appears once under Medium and once under Max. Each tier has five historical/public and five newly constructed/withheld defects.

| Tier | Medium | Max | Pair outcomes |
|---|---:|---:|---|
| Moderate | 10/10 | 8/10 | 8 both-success, 2 Medium-only |
| Hard | 7/10 | 6/10 | 5 both-success, 2 Medium-only, 1 Max-only, 2 both-fail |
| Very-hard | 7/10 | 9/10 | 7 both-success, 2 Max-only, 1 both-fail |
| **Total** | **24/30** | **23/30** | **20 both-success, 4 Medium-only, 3 Max-only, 3 both-fail** |

The aggregate totals are nearly tied. The paired relationship changes with difficulty: Medium-only repairs appear in moderate and hard tiers, while the very-hard tier contains two Max-only repairs and no Medium-only repairs.

## Strongest supported findings

1. Additional reasoning effort changed observable repair trajectories.
2. Max performed more observable work in every primary tier.
3. Additional effort did not provide a uniform correctness benefit across tiers.
4. Max's unique-repair advantage appeared at the very-hard frontier in this sample.
5. Held-out behavioral evaluation repeatedly found incomplete repairs that public tests alone would have accepted.
6. Provenance corresponded descriptively with different subgroup outcomes, especially on E006 withheld cases, but does not diagnose training exposure.

At very-hard difficulty, Max's mean resource use was 1.63× Medium's in wall time, 1.61× in steps, 1.77× in tool calls, 3.92× in prompt tokens, 5.07× in completion tokens, and 4.27× in cached tokens. The additional activity coincided with two Max-only repairs, but no cost-normalized conclusion is possible without price or ACU data.

## Claims not supported

The evidence does not establish that Max is generally better on very-hard tasks, that Medium is generally better on moderate tasks, that there is a universal crossover point, that hidden reasoning caused the outcome, that historical cases were memorized, or that withheld cases prove absence from training data. It does not generalize automatically to other agents, model families, languages, versions, or task distributions.

The exact paired p-values were non-significant in every primary set: 0.50 for moderate, 1.00 for hard, 0.50 for very-hard, and 1.00 cumulatively. With ten pairs per tier and one run per condition per case, this is exploratory evidence with wide uncertainty, not a confirmatory superiority study.

## Methodological lessons

The first lesson is to preserve paired case identity. The aggregate 24/30 versus 23/30 total hides the switch from Medium-only to Max-only outcomes. The second is to separate provenance from causal exposure claims. Public versus withheld is informative context, not a contamination detector. The third is to require evaluator-side behavioral checks. Ten public-pass/held-out-fail runs would have been misclassified by a visible-test-only benchmark.

The fourth lesson is that difficulty is multidimensional. E006 Max scored higher while using deeper observable activity. Solve rate alone cannot define a universal difficulty ladder; session behavior, pair composition, regressions, held-out failures, and resource use should be reported together.

## Infrastructure lessons

The execution environment must be treated as part of the protocol. E001's permission-gating failure made the first comparison invalid for capability inference. The corrected runs used fresh sanitized workspaces, evaluator-side references, and isolated execution boundaries. E006 was frozen and executed once in its prescribed order; a pre-invocation launcher-staging issue did not become a benchmark run because Devin never started.

The publication layer now derives its summary, CSVs, and charts from canonical machine-readable evidence. The generator asserts the primary counts, pair completeness, and tier set before writing outputs. It does not invoke Devin or SWE-2. Prior canonical evidence and release tags remain preserved.

## Future research opportunities

Future work may include replication with another coding agent or model family, more programming languages, larger samples, repeated stochastic runs per case, cost-normalized analysis, a supported High-effort condition, Fusion as a separate system-level study, and newer SWE-2 versions or models. These are future studies with their own frozen protocols. They are not extensions of this denominator.

## Close

The benchmark is complete as a six-experiment program. Its final result is not a universal winner claim. It is a near-tie in aggregate with a meaningful change in paired behavior at the very-hard frontier, alongside substantially different resource use and a demonstrated need for hidden behavioral evaluation.
