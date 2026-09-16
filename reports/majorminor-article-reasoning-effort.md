# We Ran Devin 60 Times. The Value of More Reasoning Changed With Difficulty.

*Across 30 paired software repairs, SWE-2 Max spent more observable effort. It only pulled ahead when the bugs reached the very-hard frontier.*

When we started this series, we expected a straightforward comparison. Give Devin the same bug, run it once with SWE-2 Medium and once with SWE-2 Max, and see whether the condition with more reasoning effort repairs more software.

The first honest answer was uncomfortable. On five historical bugs, Medium completed all five and Max completed four. That result was interesting, but it was also too small to carry much interpretation. Perhaps the cases were too easy. Perhaps public benchmark exposure mattered. Perhaps one disagreement dominated the result. Perhaps the execution environment had shaped the outcome.

So we expanded the study systematically. The final primary benchmark now contains 30 unique bugs and 60 valid runs. Every bug was run once under Medium and once under Max. The cases are split into three balanced difficulty tiers, and every tier contains five historical/public defects plus five newly constructed/withheld defects. The prompts were paired and frozen. Each run started in a fresh sanitized workspace. The success decision came from public tests, independent held-out tests, and a clean regression suite.

The final totals are almost tied: Medium repaired 24 of 30 cases, while Max repaired 23. That is not the end of the story. It is the reason to look at the pairs and the tiers.

![Success by difficulty tier](/research/v4-success-by-difficulty-tier.png)

## The question got bigger than “which model wins?”

The completed study asks:

> How does SWE-2 reasoning effort relate to autonomous software-repair success and resource use as task difficulty increases?

That question has several parts. Does additional effort change the agent's path through a repair? Does it cost more wall time, tools, steps, or tokens? Does it help consistently, or only for certain task demands? Do historical/public cases behave differently from newly constructed/withheld cases? And do visible tests tell the whole truth?

The benchmark cannot observe private chain-of-thought, so “more reasoning” means the Max condition and the activity recorded around it. We measured wall time, steps, tool calls, prompt tokens, completion tokens, cached tokens, source files changed, and workspace churn. These are useful operational signals, not a window into hidden thought.

There is also an important unit-of-analysis choice. A run is not an independent draw from a generic task distribution; it is one side of a deliberate pair. The same bug, prompt, and starting state give us a controlled comparison, while the paired outcome tells us whether a result was shared or unique. That is why four Medium-only repairs and three Max-only repairs matter more than a simple tally of 24 and 23. They reveal where the two trajectories diverged, and they keep easy both-success cases from overwhelming the cases that actually separate the conditions.

## A protocol failure became part of the research history

The series began with E001, which attempted to run the paired comparison in an unattended environment. The permission mode still required shell confirmation, so required calls were rejected and the resulting patches were empty. E001 did not test repair capability. It showed that permission policy is part of the effective autonomous-agent system.

E002 corrected that execution boundary and re-ran five historical/public BugsInPy cases in an isolated disposable environment. E003 added five easier newly constructed/withheld cases. E004 added five more withheld moderate cases. E005 added ten hard cases. E006 added ten very-hard cases under a frozen protocol and fixed order.

E001 remains methodological provenance. E003 remains supplemental evidence, where both conditions scored 5/5. Neither is included in the final 30-case primary denominator.

## The final design: three tiers, two provenances, one pair per bug

The primary benchmark is balanced by construction:

| Tier | Experiments | Cases | Medium | Max | Historical/public | Withheld |
|---|---|---:|---:|---:|---:|---:|
| Moderate | E002 + E004 | 10 | 10/10 | 8/10 | 5 | 5 |
| Hard | E005 | 10 | 7/10 | 6/10 | 5 | 5 |
| Very-hard | E006 | 10 | 7/10 | 9/10 | 5 | 5 |
| **Primary** | **E002/E004/E005/E006** | **30** | **24/30** | **23/30** | **15** | **15** |

“Historical/public” means the underlying defect came from a public source or benchmark lineage. “Newly constructed/withheld” means the benchmark instance was constructed for this study and withheld before execution. The latter is not proof that an instance was absent from all training data. It is a provenance boundary that reduces obvious public-case exposure.

## Moderate: more activity, no Max-only repair

On the ten moderate cases, Medium completed every repair. Max completed eight. Eight pairs succeeded under both conditions, and two were Medium-only. There were no Max-only repairs and no pairs in which both conditions failed.

Medium's mean wall time was 223 seconds. Max's was 429 seconds. Max also used more mean steps, 36.2 versus 28.0, and more tool calls, 43.7 versus 23.0. Its mean prompt-token count was 1.26 million compared with Medium's 477,335, and its mean completion count was 18,564 compared with 5,820.

The moderate result is not “less reasoning is better.” It is narrower: in these ten paired cases, the additional observable activity did not produce a unique Max success. Both conditions were already strong on this tier, which leaves little room for a higher score to show up.

## Hard: the first expansion did not overturn the result

The hard tier made the task distribution more demanding. Medium completed seven cases and Max completed six. The pairs contained five both-success outcomes, two Medium-only outcomes, one Max-only outcome, and two both-fail outcomes.

Max again did more observable work. Its mean wall time was 438 seconds versus 186 seconds for Medium. It averaged 38.1 steps and 39.8 tool calls, compared with 28.0 and 29.3. Mean prompt tokens were 49,894 for Max and 31,903 for Medium. Mean completion tokens were 535 and 287.

At this point in the series, Max was using more of the measured resources without an aggregate success advantage. If we had stopped at the hard tier, the cautious summary would have been that more effort changed trajectories but did not improve repair accuracy in this sample.

## Very-hard: the paired relationship changed

E006 is where the pattern becomes more interesting. Medium completed seven of ten very-hard cases. Max completed nine. Seven pairs succeeded under both conditions. Two were Max-only. There were zero Medium-only repairs and one pair where both conditions failed.

The historical/public cases in E006 were `black-23`, `tqdm-2`, `thefuck-17`, `PySnooper-1`, and `black-6`. Both conditions solved all five. The newly constructed/withheld cases were `work-queue`, `wire-relay`, `feature-store`, `profile-runtime`, and `account-ledger`. Medium solved two of those five; Max solved four.

The important observation is not simply that Max scored 9/10. It is the composition of the pairs. The earlier tiers included Medium-only repairs. At the very-hard tier, Max found two repairs that Medium did not, and Medium found none that Max did not.

![Paired outcome composition](/research/v4-paired-outcome-composition.png)

This does not prove that Max is generally better at very-hard software repair. Ten cases are not enough for that claim, and the tiers are not a universal difficulty scale. It does show that the unique-win pattern changed when the task demands reached this study's frontier.

## The aggregate total hides the interesting result

Across the full primary set, there were 20 pairs where both conditions succeeded, four Medium-only pairs, three Max-only pairs, and three both-fail pairs. Medium's 24/30 therefore edges Max's 23/30 by one run.

That total is a useful overall description, but it averages over a changing relationship. Moderate favored Medium 10/10 to 8/10. Hard favored Medium 7/10 to 6/10. Very-hard favored Max 9/10 to 7/10. An aggregate leaderboard would turn that into one narrow Medium lead and hide the case-level shift.

![Unique repairs by tier](/research/v4-unique-repairs-by-tier.png)

The strongest supported interpretation is conditional. More reasoning effort changed repair trajectories. Additional effort did not provide a uniform correctness benefit. Within this benchmark, Max's unique repair advantage appeared at the very-hard tier, while earlier tiers included Medium-only outcomes.

## What did the extra effort cost?

Max used more observable resources in every primary tier. The size of the difference grew most visibly in the very-hard tier.

| Tier | Condition | Mean wall | Mean steps | Mean tools | Prompt tokens | Completion tokens |
|---|---|---:|---:|---:|---:|---:|
| Moderate | Medium | 223s | 28.0 | 23.0 | 477k | 5.8k |
| Moderate | Max | 429s | 36.2 | 43.7 | 1,260k | 18.6k |
| Hard | Medium | 186s | 28.0 | 29.3 | 31.9k | 0.3k |
| Hard | Max | 438s | 38.1 | 39.8 | 49.9k | 0.5k |
| Very-hard | Medium | 441s | 22.3 | 20.8 | 349k | 4.8k |
| Very-hard | Max | 719s | 36.0 | 36.9 | 1,368k | 24.3k |

In E006, Max's mean wall time was 1.63 times Medium's. Mean steps were 1.61 times higher, tool calls 1.77 times higher, prompt tokens 3.92 times higher, completion tokens 5.07 times higher, and cached tokens 4.27 times higher. On the same tier where the unique Max repairs appeared, Max also spent substantially more observable effort.

![Observable token use](/research/v4-token-use-by-tier.png)

Does that mean the extra effort was cost-effective? We cannot answer that fully. Pricing and ACU data were not available, and the sample is too small for a stable cost-normalized estimate. Descriptively, though, the extra effort became more productive in the very-hard tier: it coincided with two Max-only repairs, compared with zero Max-only moderate repairs and one Max-only hard repair.

## Why hidden tests changed the interpretation

The evaluator required public tests, independent held-out target tests, and a clean regression suite. This distinction mattered repeatedly.

Across E002, E004, E005, and E006, ten primary runs passed public tests but failed held-out tests. Those are classified as held-out-only behavioral failures. There were also two regression failures and one visible/public failure. No primary run timed out, and no in-protocol evaluator incident occurred.

Held-out-only failures appeared once in E002, once in E004, five times in E005, and three times in E006. In other words, the harder part of the benchmark was not only finding a patch that satisfied the visible test. It was preserving the broader behavioral contract.

![Failure-mode composition](/research/v4-failure-mode-composition.png)

A public-test-only benchmark would have called those ten runs successes. That would have inflated every reported score and erased a meaningful failure mode. The result is a methodological finding that travels beyond this particular comparison: an autonomous repair benchmark needs evaluator-side behavioral checks that the agent cannot see.

## Provenance added a second axis of uncertainty

The provenance split was designed to make a simple exposure concern visible, not to prove contamination. Moderate cases were 5/5 historical/public and 5/5 withheld for Medium; Max was 4/5 in each subgroup. Hard cases were 4/5 historical/public and 3/5 withheld for Medium, and 4/5 and 2/5 for Max. Very-hard cases were 5/5 historical/public for both conditions; on withheld cases, Medium scored 2/5 and Max scored 4/5.

The very-hard withheld result is directionally consistent with the frontier story, but it is also only five cases per condition. The right conclusion is that provenance corresponded descriptively with different outcomes in this sample and that future evaluations should report it. The wrong conclusion would be that public cases were memorized or that withheld cases prove the opposite.

![Historical versus withheld success](/research/v4-historical-vs-withheld-success.png)

## Did the tiers work?

The tiers worked as a study design because they elicited different paired patterns and different amounts of activity. They should not be treated as a universal scale.

The moderate tier had no both-fail pair and a perfect Medium score. The hard tier had the lowest aggregate success and the richest mixture of Medium-only, Max-only, and both-fail outcomes. The very-hard tier elicited the largest Max prompt and completion means and the largest effort ratio, plus a different unique-win pattern.

It would be a mistake to say that very-hard was simply easier because Max scored 9/10. A condition can solve more cases while doing deeper work, encountering a different mix of obstacles, or entering a different capability regime. The final data argue for multidimensional difficulty calibration using success, paired failures, session duration, activity, and behavioral-failure complexity together.

![Paired wall time across primary cases](/research/v4-paired-wall-time-all-cases.png)

## What the statistics can and cannot say

We used an exact two-sided conditional McNemar/binomial test on discordant pairs, plus 95% Wilson intervals for the two success proportions in each set. The p-values were 0.50 for moderate, 1.00 for hard, 0.50 for very-hard, and 1.00 for the cumulative primary set. The cumulative intervals were 0.627–0.905 for Medium and 0.591–0.882 for Max.

These statistics do not identify a winner. Each tier has ten pairs, and the study was not powered as a confirmatory superiority test. The intervals overlap, and the exact paired tests are non-significant. The role of the analysis is to preserve uncertainty while showing that the very-hard pair composition is not the same as the moderate pair composition.

## What we think this suggests

The result suggests that the value of reasoning effort is conditional on the shape of the task. On cases where both conditions were already strong, additional activity often increased time and tokens without creating a unique success. On the very-hard cases, additional activity coincided with two repairs that Medium missed.

That is a research hypothesis, not a product verdict. We do not know whether the frontier pattern would survive a larger case set, repeated stochastic runs, another language, another agent, another SWE-2 version, or a cost-normalized comparison. We do not know whether a different difficulty calibration would move the apparent transition. We do know that one aggregate score is too blunt to answer the question.

## The experiment is complete; the questions continue

The planned experimental phase is complete with E006. We are not starting E007 as part of this publication.

The next useful studies are independent replications: another coding agent or model family, more languages, larger samples, repeated runs per case, and explicit cost or ACU normalization. A supported High-effort condition could test whether the observed relationship is specific to these two conditions. Fusion would be a separate system-level study, not a continuation of this denominator. Newer SWE-2 versions and models would also need their own frozen protocol.

The final answer from 30 bugs is not “Medium beats Max,” and it is not “Max wins when things get hard.” It is more precise: Medium and Max were nearly tied overall, the paired relationship changed across the designed difficulty tiers, and Max's additional observable effort produced its clearest unique-repair value at the very-hard frontier in this sample.

The complete report, machine-readable data, chart manifest, and reproducibility script are published with the benchmark release. The evidence is there for others to inspect, challenge, and extend.

Read the [V4 research report](https://github.com/MAJORminorStudio/devin-agent-benchmark/blob/v4.0.0/reports/devin-swe2-reasoning-effort-v4-final.md), browse the [publication data](https://github.com/MAJORminorStudio/devin-agent-benchmark/tree/v4.0.0/results), inspect the [sanitized evidence](https://github.com/MAJORminorStudio/devin-agent-benchmark/tree/v4.0.0/artifacts), or rebuild the derivatives with the [publication script](https://github.com/MAJORminorStudio/devin-agent-benchmark/blob/v4.0.0/scripts/build_publication_v4.py). The [v4.0.0 release](https://github.com/MAJORminorStudio/devin-agent-benchmark/releases/tag/v4.0.0) collects the final primary package.
