# Results

Canonical committed summaries and public publication derivatives live here.
Raw Devin artifacts, patches, and usage metadata remain separate from
ground-truth manifests and fixed verification trees; runtime output is ignored
by default.

- [V3 primary summary](publication-v3-summary.json) — E002 + E004 moderate and
  E005 hard benchmark
- [V3 run-level CSV](publication-v3-runs.csv) — all 40 primary runs
- [V3 paired CSV](publication-v3-paired-results.csv) — all 20 primary pairs

- [Experiment 002 summary](experiment-002-summary.json) — canonical 5×2
  result ledger
- [Experiment 002 forensic JSON](experiment-002-forensics.json) — observable
  tool behavior and source-only metrics
- [Publication summary](publication-summary.json) — machine-readable public
  overview across E001 and E002
- [Paired publication CSV](publication-paired-results.csv) — case-level
  Medium/Max comparison
- [V2 publication summary](publication-summary-v2.json) — ten-case historical
  plus novel machine-readable result ledger
- [V2 paired CSV](publication-paired-results-v2.csv) — all twenty valid runs,
  with historical/novel provenance

Rebuild the publication derivatives with
`python3 scripts/build_publication_assets.py`. It reads only committed summary
and forensic data, does not invoke Devin, and makes no statistical-significance
claims. The v2 bundle is rebuilt with `python3 scripts/build_v2_publication.py`
from the closed E003 staging area and committed E002/E003 summaries.
