# Limitations

- **Fixed task set:** E007 has 30 benchmark cases, 10 in each of three difficulty tiers. The cases are not a random sample of all software-repair tasks.
- **One E007 execution per cell:** E007 has one run per case/effort condition. It cannot estimate within-condition run variance on its own.
- **Targeted sample:** E008 repeats only 11 case/effort cells selected because earlier outcomes disagreed. The 33 new runs and 55 five-observation outcomes are not independent new benchmark tasks and do not estimate full-benchmark accuracy.
- **Three repeats per selected cell:** unanimous or mixed results over three repeats are a small descriptive check, not a precise reliability estimate.
- **Evaluator correction scope:** the cache defect affected some staged very-hard evaluator runs. The clean recheck used preserved workspaces and frozen tests. It corrected evaluation outcomes without new agent execution, but it does not identify why original and later agent outcomes differed on the remaining discordant cases.
- **Temporal/backend confounding:** E007 and E008 were executed on different dates. Provider deployment revision and per-session backend identity were unavailable. The observed variation cannot be separated into stochastic run variation versus temporal/backend change.
- **Effort comparison:** Medium, High, and Max have clean totals 22/30, 24/30, and 24/30, but this study does not establish an optimal effort setting or a general effort-related reliability difference. High was not included in E008 repeats.
- **Telemetry:** one High E007 run has no wrapper timing metadata. High timing n=29; Medium and Max n=30. Missing time is not imputed. Trace-derived behavior labels are heuristic.
- **Cost:** actual monetary cost is unknown. Catalog labels and token counts are not billing evidence.
- **Outcome scope:** a pass means the frozen task's evaluator contract passed. It is not a measure of general coding ability, product quality, or user satisfaction.
- **Publication inference:** no causal claim is made about cognition, provider changes, or the cause of residual run-to-run differences. No new post-hoc significance testing was performed.
