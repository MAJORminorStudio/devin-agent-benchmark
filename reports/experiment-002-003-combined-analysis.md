# Combined E002 + E003 Analysis

This descriptive combined analysis keeps the two experiments distinct: E002 used five historical BugsInPy repairs; E003 used five newly constructed cases withheld from Devin before execution. E001 is excluded from the capability denominator because permission gating invalidated it as a capability comparison.

## Results

| Set | Medium | Max | Both success | Medium-only | Max-only | Both fail |
|---|---:|---:|---:|---:|---:|---:|
| E002 historical | 5/5 | 4/5 | 4 | 1 | 0 | 0 |
| E003 novel | 5/5 | 5/5 | 5 | 0 | 0 | 0 |
| Combined 10 cases | 10/10 | 9/10 | 9 | 1 | 0 | 0 |

## Comparable aggregate observables

| Set / condition | Total wall s | Steps | Tool calls | Prompt tokens | Completion tokens |
|---|---:|---:|---:|---:|---:|
| E002 Medium | 1816.309 | 199 | 169 | 4120476 | 52313 |
| E002 Max | 3649.780 | 274 | 322 | 11740951 | 164983 |
| E003 Medium | 498.911 | 77 | 47 | 560746 | 5287 |
| E003 Max | 684.480 | 78 | 60 | 625125 | 15035 |
| Combined Medium | 2315.220 | 276 | 216 | 4681222 | 57600 |
| Combined Max | 4334.260 | 352 | 382 | 12366076 | 180018 |

## Interpretation

E002 showed one Medium-only outcome. E003 showed five both-success outcomes, so the E002 outcome pattern did not reproduce on the novel set. Across both experiments, Medium solved 10/10 cases and Max solved 9/10. This is descriptive evidence only: the samples are small, the case sets differ, and no causal or statistical-significance claim is made.

E003's five novel cases were newly constructed and withheld before execution; no claim is made that they were absent from training data. E003 costs/ACUs were unavailable, and only observable activity was measured.
