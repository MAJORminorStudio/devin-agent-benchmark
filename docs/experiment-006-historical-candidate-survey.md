# Experiment 006 Historical Candidate Survey

## Scope and method

The survey used the external BugsInPy checkout at dataset commit
`316b95e2353ecda832bad9b42f86fa7c2fcec8ac`, not a vendored copy. The checkout
contains 501 bug records across 17 projects. Every record was enumerated from
`projects/*/bugs/*/{bug.info,bug_patch.txt,run_test.sh,requirements.txt,setup.sh}`.
The first pass measured production-file footprint, total changed lines,
test availability, declared Python version, and setup requirements. A serious
candidate then needed a deterministic public oracle, at least two production
files or a credible cross-module path, a small enough checkout to avoid
repository bulk as the task, and no required native accelerator, live service,
or network dependency. Cases already used by E001-E005 were excluded from the
E006 selection even when they were structurally strong.

The all-record scan was followed by a manual comparison of 32 serious
candidates. The table is the audit trail for that comparison; `prod` excludes
tests, docs, examples, and fixtures from the patch's changed-file count. A
rejection is a design decision, not a claim that the upstream bug is
uninteresting.

| Candidate | prod / total files | + / - | Cross-boundary signal | Decision |
|---|---:|---:|---|---|
| scrapy-33 | 8 / 8 | 186 / 49 | engine, scraper, media pipeline, signals | reject: broad patch and high setup surface |
| pandas-44 | 5 / 5 | 71 / 15 | index family and dtype propagation | reject: pandas dependency/version risk |
| keras-20 | 5 / 5 | 48 / 19 | backend-specific convolution path | reject: compiled backend matrix |
| fastapi-1 | 4 / 4 | 207 / 16 | app, encoder, OpenAPI, routing | reject: already represented by E005 family; oversized patch |
| pandas-167 | 4 / 4 | 19 / 3 | index/date/indexing propagation | reject: pandas dependency/version risk |
| pandas-79 | 4 / 4 | 12 / 3 | groupby, datetime, multi-index, series | reject: pandas dependency/version risk |
| youtube-dl-42 | 4 / 4 | 11 / 10 | extractor and shared utility | reject: extractor fixtures/network assumptions |
| thefuck-16 | 4 / 4 | 11 / 7 | Bash, Fish, Zsh, correction context | reject: adjacent shell case to E005; repeat risk |
| pandas-80 | 3 / 7 | 332 / 856 | masked array, generic, indexing | reject: huge churn and pandas risk |
| pandas-92 | 3 / 5 | 47 / 15 | resampling and period index | reject: pandas dependency/version risk |
| keras-11 | 3 / 5 | 40 / 21 | generator, training, data utilities | reject: backend/runtime risk |
| black-6 | 3 / 4 | 109 / 17 | target dispatch, tokenizer, parser driver | select as K01: deterministic, dependency-light |
| keras-1 | 3 / 4 | 84 / 71 | initializer plus two backends | reject: backend matrix |
| matplotlib-1 | 3 / 3 | 31 / 18 | backend, figure, tight layout | reject: rendering/display environment |
| pandas-123 | 3 / 3 | 21 / 9 | base, numeric, range indexes | reject: pandas dependency/version risk |
| cookiecutter-4 | 3 / 3 | 20 / 6 | exceptions, generation, hooks | reject: filesystem/template fixture sensitivity |
| pandas-105 | 2 / 6 | 56 / 68 | frame and generic dispatch | reject: large test/setup surface |
| pandas-70 | 2 / 5 | 40 / 5 | groupby and operations | reject: pandas dependency/version risk |
| matplotlib-15 | 2 / 4 | 29 / 12 | color normalization and docs examples | reject: plotting environment and example churn |
| black-23 | 2 / 3 | 51 / 13 | legacy grammar and formatter | select as K03: deterministic, distinct contract |
| pandas-46 | 2 / 3 | 34 / 8 | multi-index and reshape | reject: pandas dependency/version risk |
| pandas-53 | 2 / 3 | 9 / 15 | base index and series | reject: pandas dependency/version risk |
| scrapy-30 | 2 / 3 | 8 / 7 | command line and test process | reject: subprocess/platform assumptions |
| PySnooper-1 | 2 / 3 | 8 / 4 | compatibility helper and tracer source path | select as K02: deterministic after public adapter |
| pandas-125 | 2 / 2 | 69 / 0 | categorical and internal blocks | reject: pandas dependency/version risk |
| pandas-90 | 2 / 2 | 67 / 27 | testing and pickle I/O | reject: serialization/version risk |
| keras-42 | 2 / 2 | 61 / 26 | training and model wrappers | reject: backend/runtime risk |
| keras-37 | 2 / 2 | 60 / 8 | recurrent and wrapper layers | reject: backend/runtime risk |
| keras-19 | 2 / 2 | 53 / 19 | recurrent layer and backend | reject: backend/runtime risk |
| pandas-47 | 2 / 2 | 41 / 0 | frame and indexing | reject: pandas dependency/version risk |
| luigi-9 | 2 / 2 | 34 / 9 | execution summary and return codes | reject: scheduler/dependency setup risk |
| tornado-6 | 2 / 2 | 16 / 2 | asyncio loop and platform adapter | reject: represented by E005 family |
| tqdm-2 | 2 / 2 | 6 / 6 | meter and display utility | select as K05: deterministic and low setup |
| thefuck-17 | 2 / 2 | 6 / 10 | Bash process/environment handoff | select as K04: deterministic and distinct from K05 |

The final five are intentionally compact enough to run honestly while still
requiring cross-file reasoning. Their production footprint is 3/4 files for
K01, 2/3 for K02, 2/3 for K03, 2/2 for K04, and 2/2 for K05. No E001-E005
case ID is reused. K02 is the only adapted public oracle: the pinned
`tests/test_chinese.py` passed on the validation interpreter, so the
public-facing adapter adds one deterministic no-cookie source assertion while
retaining the upstream test and its provenance. The adapter is documented in
the public manifest and its bytes are hash-locked privately.

## Rejected alternatives and boundary rationale

The tempting high-footprint records (scrapy-33, pandas-44, keras-20, and
pandas-80) were rejected because their dependency or repository size would
make setup failure and environment breadth a material confound. The tempting
shell/parser repeats were split deliberately: black-6 and black-23 exercise
different parser contracts, while thefuck-17 is retained as a compact
environment-ownership case and thefuck-16 is excluded as too close to the
prior hard tier. No candidate was selected merely because its patch was large.
