# Results

Canonical committed summaries and public publication derivatives live here.
Raw Devin artifacts, patches, and usage metadata remain separate from
ground-truth manifests and fixed verification trees; runtime output is ignored
by default.

- [Experiment 002 summary](experiment-002-summary.json) — canonical 5×2
  result ledger
- [Experiment 002 forensic JSON](experiment-002-forensics.json) — observable
  tool behavior and source-only metrics
- [Publication summary](publication-summary.json) — machine-readable public
  overview across E001 and E002
- [Paired publication CSV](publication-paired-results.csv) — case-level
  Medium/Max comparison

Rebuild the publication derivatives with
`python3 scripts/build_publication_assets.py`. It reads only committed summary
and forensic data, does not invoke Devin, and makes no statistical-significance
claims for n=5.
