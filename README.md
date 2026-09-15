# Devin + SWE-2 Reasoning Effort Benchmark

An independent, reproducible evaluation of Cognition's Devin agent on five
real Python bugs from [BugsInPy](https://github.com/reproducing-research-projects/BugsInPy).
Experiment 002 compares SWE-2 Medium and SWE-2 Max with identical tasks,
fresh sanitized workspaces, hidden evaluator tests, and zero substantive
intervention.

## Key result

| Metric | SWE-2 Medium | SWE-2 Max |
|---|---:|---:|
| Behavioral success | **5/5** | **4/5** |
| Mean wall time | 363s | 730s |
| Observable steps | 199 | 274 |
| Prompt tokens | 4.12M | 11.74M |
| Completion tokens | 52.3K | 165.0K |

In this five-case paired pilot, Max consumed substantially more time and model
activity without improving aggregate repair accuracy. This is an exploratory
result at n=5, not a statistical superiority study or a general claim about
Devin, SWE-2, or reasoning effort.

![Paired wall-clock time](assets/charts/paired-wall-time.png)

## Paired results

| Case | Medium | Max | Medium wall | Max wall | Held-out disagreement |
|---|---:|---:|---:|---:|---|
| Black 16 | pass | pass | 366.3s | 399.8s | — |
| FastAPI 3 | pass | pass | 299.3s | 1,137.8s | — |
| Scrapy 3 | pass | pass | 817.9s | 1,380.5s | — |
| tqdm 5 | pass | **fail** | 157.3s | 405.3s | Max left the inferred total unset |
| Tornado 13 | pass | pass | 175.5s | 326.5s | — |

Four pairs succeeded under both conditions. One pair was Medium-only; no pair
was Max-only or failed under both conditions. See the
[standalone research report](reports/swe-2-medium-vs-max-research-report.md)
for the complete case analysis and charts.

## The disagreement: tqdm-5

Both agents passed the visible public test. The independent held-out test
checked the externally observable contract for a disabled progress wrapper
around a sized iterable. Medium inferred `len(iterable)` and passed; Max
initialized `total` but left it `None`, so it failed the held-out assertion.
The result illustrates why public-test success alone is not sufficient for
this benchmark.

![tqdm case study](assets/charts/tqdm-case-study.png)

## Why Experiment 001 matters

Experiment 001 used the same five cases and paired model conditions, but its
noninteractive `accept-edits` permission mode still required shell
confirmation. Confirmation was unavailable in unattended execution, so
required tool calls were rejected in all ten runs and every patch was empty.
E001 is therefore preserved as operational provenance, not as a capability
comparison. Experiment 002 corrected only this execution boundary by using
dangerous/effective Bypass inside a disposable isolated Docker environment;
no permission-related tool rejection occurred in E002.

![Task success](assets/charts/success-rate.png)

Permission policy is part of the effective autonomous-agent system. The full
forensic account is in the [E002 forensic analysis](reports/experiment-002-forensic-analysis.md).

## Methodology

- Five historical BugsInPy bugs with known buggy and fixed revisions.
- Identical frozen prompts within each Medium/Max pair.
- Fresh sanitized workspace for every run; the reference patch and held-out
  tests stayed evaluator-side.
- One interleaved frozen order, no retries, and no substantive assistance.
- Session closed before evaluation; TASK_SUCCESS required public tests,
  held-out target tests, and a clean regression suite.
- Experiment 002 used a disposable Linux/arm64 Docker container with a
  read-only root, dropped capabilities, no-new-privileges, no Docker socket,
  no control-repository mount, a single workspace, and restricted egress.

The harness is intentionally isolated from Major Minor research databases,
Obsidian vaults, Supabase projects, research pipelines, and production
repositories. BugsInPy is an external checkout and is not vendored here.

## Evidence and reproduction

Start with the [full research report](reports/swe-2-medium-vs-max-research-report.md),
then follow its evidence links to the [E002 results](reports/experiment-002-results.md),
[forensic analysis](reports/experiment-002-forensic-analysis.md),
[per-run public artifacts](artifacts/experiment-002/README.md), prompts,
sanitized timelines, patches, and evaluator results. E001 is available as
[invalid capability-comparison provenance](reports/experiment-001-results.md)
with its [public artifacts](artifacts/experiment-001/README.md).

Machine-readable publication data are in
[results/publication-summary.json](results/publication-summary.json) and
[results/publication-paired-results.csv](results/publication-paired-results.csv).
The committed source data are [the E002 summary](results/experiment-002-summary.json),
[the forensic JSON](results/experiment-002-forensics.json), and the frozen
[E002 configuration](manifests/experiment-002-config.json).

To rebuild the publication derivatives without invoking Devin:

```sh
python3 scripts/build_publication_assets.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

The chart builder requires Pillow. No command above runs a benchmark case or
contacts Devin. The public artifact policy and safe evidence boundary are
documented in the [research report](reports/swe-2-medium-vs-max-research-report.md)
and [methodology](docs/methodology.md).

## Limitations

This is a five-case historical Python pilot, one agent product/model family,
and one frozen task setup. Cost and ACU data were unavailable. Public
benchmark exposure or contamination cannot be ruled out absolutely. The
results are exploratory and do not establish that either condition is
generally superior, that more reasoning causes worse coding performance, or
that the observed resource differences will generalize.

## Repository map

| Path | Contents |
|---|---|
| `cases/` | Case-source conventions and workspace notes |
| `manifests/` | Frozen configurations and evaluator-side ground truth |
| `prompts/` | Frozen task prompts |
| `evaluation/` | Held-out tests and scoring metadata |
| `artifacts/` | Sanitized public per-run evidence |
| `results/` | Canonical summaries and publication data |
| `reports/` | Detailed experiment, forensic, and publication reports |
| `scripts/` | Preparation, export, evaluation, analysis, and chart tools |
| `docs/` | Methodology, isolation, and protocol documentation |
| `assets/charts/` | Publication figures derived from committed results |

## Status

Experiment 001 is retained as invalid capability-comparison provenance.
Experiment 002 is complete and publication-ready as an exploratory paired
pilot. Experiment 003 has not started. See [CITATION.cff](CITATION.cff) and
[third-party notices](THIRD_PARTY_NOTICES.md) for reuse boundaries.
