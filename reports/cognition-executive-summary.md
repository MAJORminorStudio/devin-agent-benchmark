# Executive summary for Cognition

## Independent Devin + SWE-2 reasoning-effort benchmark

### Purpose

This completed benchmark examines how SWE-2 Medium and SWE-2 Max relate to autonomous software-repair success and observable resource use as task difficulty increases. It is an independent evaluation, not a Cognition-sponsored or Cognition-endorsed study.

### What was tested

The final primary benchmark contains 30 unique software defects and 60 valid runs. Every defect was run once with SWE-2 Medium and once with SWE-2 Max using the same paired prompt, fresh sanitized workspace, hidden evaluator tests, and no substantive intervention. The 30 cases are balanced into three ten-case tiers. Each tier contains five historical/public defects and five newly constructed/withheld defects.

The benchmark's success contract required public tests, evaluator-side held-out behavioral tests, and a clean regression suite. We recorded wall time, steps, tool calls, prompt/completion/cached tokens, source patch breadth, and workspace churn. These are observable activity measures; private reasoning was not measured.

### Main results

| Tier | Medium | Max | Paired composition |
|---|---:|---:|---|
| Moderate, E002 + E004 | 10/10 | 8/10 | 8 both-success, 2 Medium-only |
| Hard, E005 | 7/10 | 6/10 | 5 both-success, 2 Medium-only, 1 Max-only, 2 both-fail |
| Very-hard, E006 | 7/10 | 9/10 | 7 both-success, 0 Medium-only, 2 Max-only, 1 both-fail |
| **Primary total** | **24/30** | **23/30** | **20 both-success, 4 Medium-only, 3 Max-only, 3 both-fail** |

The aggregate result is nearly tied. The important result is the change in paired behavior across difficulty. Medium has the higher score in the moderate and hard tiers. At very-hard difficulty, Max has the higher score and produces two unique repairs that Medium does not, while Medium produces no unique repair.

### Resource use

Max performed more observable work in every tier. At E006, Max's mean versus Medium's mean was:

- 1.63× wall time: 719.0s versus 440.7s.
- 1.61× steps: 36.0 versus 22.3.
- 1.77× tool calls: 36.9 versus 20.8.
- 3.92× prompt tokens: 1.368M versus 349k.
- 5.07× completion tokens: 24.3k versus 4.8k.
- 4.27× cached tokens: 1.316M versus 308k.

Descriptively, the additional effort became more productive at the very-hard tier because it coincided with two Max-only repairs. This is not a cost-effectiveness estimate: price and ACU data were unavailable, and per-case means can be influenced by long runs.

### Held-out evaluation finding

Independent held-out behavioral checks were material. Across E002, E004, E005, and E006, ten primary runs passed public tests but failed held-out tests and were classified as held-out-only behavioral failures. There were also two regression failures, one visible/public failure, no timeouts, and no in-protocol evaluator incidents. A public-test-only benchmark would have counted those ten incomplete repairs as successes.

### Provenance finding

Historical/public cases may have been represented in public model-training corpora; newly constructed/withheld cases were withheld before execution. This is a provenance distinction, not a contamination diagnosis. In E006, both conditions solved all five historical/public cases. On the five withheld cases, Medium solved 2/5 and Max 4/5. The sample is too small to attribute this pattern to exposure.

### Interpretation and limits

The strongest supported conclusion is conditional: additional reasoning effort changed repair trajectories, but did not provide a uniform correctness benefit across tiers. In this benchmark, Max's unique-repair advantage appeared at the very-hard frontier. The data do not establish that Max is generally better on very-hard tasks, that Medium is generally better on moderate tasks, that there is a universal crossover point, that hidden reasoning caused the result, or that the pattern generalizes.

Each tier has only ten pairs and each condition ran once per case. The benchmark covers one agent product, one model family, one protocol, and primarily Python repair tasks. The exact two-sided paired p-values were 0.50 (moderate), 1.00 (hard), 0.50 (very-hard), and 1.00 (cumulative); the study is exploratory and underpowered for confirmatory claims.

### Follow-up questions

1. Does the tier-dependent paired pattern replicate with a larger, preregistered case set and repeated stochastic runs per case?
2. Does the relationship persist across languages, repositories, and another coding-agent/model family?
3. Which observable trajectory features distinguish productive Max effort from extra effort that does not improve correctness?
4. How do cost- or ACU-normalized outcomes change the practical trade-off between conditions?
5. Would a supported High-effort condition, or a separately designed multi-agent/Fusion study, reveal a different frontier pattern?

### Evidence and reproducibility

- [Final V4 report](devin-swe2-reasoning-effort-v4-final.md)
- [Machine-readable summary](../results/publication-v4-summary.json)
- [Paired results](../results/publication-v4-paired-results.csv)
- [All primary runs](../results/publication-v4-runs.csv)
- [Tier summary](../results/publication-v4-tier-summary.csv)
- [Chart manifest and hashes](../artifacts/publication-v4/MANIFEST.json)
- [Rebuild script](../scripts/build_publication_v4.py)

The planned experimental phase is complete. This publication does not create E007 or modify E001–E006 canonical evidence.
