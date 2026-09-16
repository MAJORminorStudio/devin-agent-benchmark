# Outreach draft to Cognition

Subject: Independent Devin + SWE-2 reasoning-effort benchmark: final 30-case result

Hi Cognition team,

We have completed an independent paired benchmark of Devin with SWE-2 Medium and SWE-2 Max. The final primary set contains 30 software defects and 60 valid runs across moderate, hard, and very-hard tiers, with five historical/public and five newly constructed/withheld cases in each tier.

The aggregate result is nearly tied: Medium repaired 24/30 and Max 23/30. The more interesting pattern is tier-dependent. Medium led 10/10 to 8/10 on moderate cases and 7/10 to 6/10 on hard cases. At very-hard difficulty, Max led 9/10 to 7/10, with two Max-only repairs and no Medium-only repairs. Max also used substantially more observable time, tools, steps, and tokens, especially at the frontier.

The full report, data, and reproducibility materials are available in the [benchmark repository](https://github.com/MAJORminorStudio/devin-agent-benchmark) and the [v4.0.0 release](https://github.com/MAJORminorStudio/devin-agent-benchmark/releases/tag/v4.0.0). We would welcome technical feedback on the protocol, evaluator design, provenance split, and the hypotheses this result suggests. This is independent work and does not imply Cognition endorsement.

Best,

MAJOR//minor Studio
