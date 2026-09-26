# Devin SWE-2 benchmark follow-up — public release draft v5.0.0

This directory is a locally prepared publication package for E007 and E008. It is a draft for review; it has not been pushed, tagged, released, or deployed. E007 and E008 source evidence remains preserved in `artifacts/experiment-007/` and `artifacts/experiment-008/`.

The study began as a comparison of SWE-2 Medium, High, and Max effort. E008 then exposed an evaluator-staging defect in the historical E007 results, and targeted repeats showed mixed outcomes in some previously discordant case/effort conditions. The public account preserves the order of discovery and both E007 score sets.

## Release contents

- `PUBLICATION.md` — technical synthesis and results.
- `METHODOLOGY.md`, `LIMITATIONS.md`, `CORRECTION.md`, and `CHANGELOG.md`.
- `docs/` — preregistration, protocols, audit, evaluator correction, and experiment reports.
- `data/` — sanitized, machine-readable run and case tables generated from source records.
- `figures/` — publication figures; every plotted denominator is identified in its subtitle or labels.
- `checksums/SHA256SUMS.txt` — hashes for all package files except the checksum file itself.

## Headline data

- E007: 90 new Devin sessions, one per case and effort cell; historical evaluator totals were Medium 16/30, High 18/30, Max 18/30.
- E008 clean recheck of preserved E007 very-hard workspaces: corrected totals were Medium 22/30, High 24/30, Max 24/30. These are re-evaluations, not new agent sessions, and do not replace the historical E007 record.
- E008 targeted repeats: 33/33 planned sessions completed with valid final evaluations; 19/33 passes over 11 selected conditions.
- Selected five-observation sequences: 30/55 passes across original, E007 clean recheck, and three E008 repeats. This is not a benchmark-wide score.
- Actual monetary cost: unknown.

## Rebuild and verify

These commands are maintainer-side release tools. They build from the original E007 and E008 source ledgers, which are intentionally not included in the public repository or release package because they contain private run evidence. They cannot regenerate this release from a public clone; the sanitized outputs and checksums are included here for verification. In the maintainer checkout, use the bundled publication Python environment or install `requirements-publication.txt`, then run:

```sh
python3 scripts/build_publication_v5.py
python3 scripts/render_publication_v5_figures.py
python3 scripts/validate_publication_v5.py
```

No Devin sessions are launched by these scripts. Public CSVs exclude session IDs, host paths, raw commands, exports, and private traces. See `LIMITATIONS.md` for interpretation boundaries.
