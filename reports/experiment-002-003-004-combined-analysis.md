# Combined E002, E003, and E004 Analysis

This is a new descriptive cross-experiment derivative; the existing E002/E003 evidence remains unchanged.

| Experiment | Case set | Medium | Max | Paired pattern |
|---|---|---:|---:|---|
| E002 | historical BugsInPy | 5/5 | 4/5 | 1 Medium-only, 4 both-success |
| E003 | novel/easier | 5/5 | 5/5 | 5 both-success |
| E004 | novel/E002-calibrated | 5/5 | 4/5 | 1 Medium-only, 4 both-success |

Across the 15 paired cases, Medium solved 15/15 and Max solved 13/15. There were 13 both-success pairs, 2 Medium-only pairs, and no Max-only or both-fail pairs.

Outcome-wise, E004 resembled E002 more than E003: it reproduced a single Medium-only pair rather than an all-success tie. E004 was nevertheless much lighter in raw wall time and workspace burden than E002, so this is not evidence of full difficulty equivalence. These are small descriptive samples and do not support causal or statistically significant claims about reasoning effort.

See the [E004 report](experiment-004-results.md), [E004 summary](../results/experiment-004-summary.json), [E002 summary](../results/experiment-002-summary.json), and [E003 summary](../results/experiment-003-summary.json).
