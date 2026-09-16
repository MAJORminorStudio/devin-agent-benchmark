# Publication V4 artifacts

This directory contains derived publication assets for the final three-tier
Devin + SWE-2 Medium/Max benchmark. The assets are generated from the
canonical E002, E004, E005, and E006 machine-readable evidence by
[`scripts/build_publication_v4.py`](../../scripts/build_publication_v4.py).
Generation does not invoke Devin or SWE-2.

## Charts

| File | Description |
|---|---|
| `charts/success-by-difficulty-tier.png` | Medium and Max success by moderate, hard, and very-hard tier. |
| `charts/paired-outcome-composition.png` | Both-success, Medium-only, Max-only, and both-fail composition per tier. |
| `charts/historical-vs-withheld-success.png` | Success split by historical/public versus newly constructed/withheld provenance. |
| `charts/mean-wall-time-by-tier.png` | Mean wall time per run by tier and condition. |
| `charts/token-use-by-tier.png` | Mean prompt and completion tokens in separate panels. |
| `charts/unique-repairs-by-tier.png` | Medium-only versus Max-only paired repairs. |
| `charts/paired-wall-time-all-cases.png` | Per-case Medium/Max wall time across all 30 primary pairs on a log scale. |
| `charts/cumulative-primary-result.png` | Aggregate 24/30 versus 23/30 primary result. |
| `charts/failure-mode-composition.png` | Mutually exclusive run-level failure categories across the primary experiments. |

`MANIFEST.json` records the chart dimensions and SHA-256 hash for each PNG.
The chart source data and all reported aggregates are in the adjacent
`results/publication-v4-*.{json,csv}` files.
