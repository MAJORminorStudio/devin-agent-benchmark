# Experiment 001 readiness report

## Current decision

Phase 1 infrastructure is ready for a small, controlled reproduction pass. The
recommended case set is Black 16, FastAPI 3, Scrapy 3, Tornado 13, and tqdm 5.
Cookiecutter 2 is retained as the strongest alternate, pending a Python 3.6
runner for its multi-version tox command.

No Devin integration has been installed or configured, and no batch experiment
has been run.

## Reproduction record

The checked-in harness wrote one `reproducibility.json` per prepared case, with
the sanitized summary retained in [results/phase-1-reproducibility.json](../results/phase-1-reproducibility.json).
The
following small validation used disposable `uv` virtual environments on macOS;
no Devin or paid API was involved.

| Case | Runner and dependency setup | Buggy side | Fixed side | Result |
|---|---|---:|---:|---|
| Black 16 | Python 3.8.20; appdirs, attrs, click, toml | fail | pass | reproduced |
| FastAPI 3 | Python 3.8.20; pytest 5.4.3, Pydantic 1.5.1, Starlette 0.13.2, requests 2.23.0, six, typing_extensions | fail | pass | reproduced |
| Scrapy 3 | Python 3.8.20; Scrapy 2.1.0, pytest 5.4.2, plus six, testfixtures, PyDispatcher | fail | pass | reproduced |
| tqdm 5 | Python 3.8.20; pytest 5.4.3, nose 1.3.7, six, python-dateutil | fail | pass | reproduced |
| Tornado 13 | Python 3.9.25 compatibility runner; no third-party package | fail | pass | reproduced under 3.9; canonical 3.7 still pending |
| Cookiecutter 2 (alternate) | Python 3.8.20; direct pytest passed after adding MarkupSafe 1.1.1 and pytest-cov 2.9.0 | fail | pass | equivalent tests pass; original tox command not validated |

The harness's exact test-command verification passed for the five recommended
cases. Cookiecutter remains an alternate because its source `run_test.sh`
invokes a tox matrix and the available host tox did not accept the historical
positional invocation. The default host Python 3.11 was also unsuitable for
old stacks: Black lacked `appdirs`, and Tornado failed before the target test
because `collections.MutableMapping` is absent. The BugsInPy requirements files
also include UTF-16/CRLF files, obsolete pinned packages, and (in some cases)
platform-specific packages; the harness normalizes metadata but intentionally
does not install it implicitly. Docker was unavailable because its daemon was
not running, so these results are macOS virtual-environment checks rather than
container checks.

## Before subscribing to Devin

- Re-run Tornado under Python 3.7 and the full five cases in disposable,
  preferably Linux, Python 3.6/3.7/3.8 runners.
- Confirm every buggy workspace fails for the expected reason and every fixed
  workspace passes with no network or paid service.
- Add at least one held-out evaluator test per case, kept outside the agent
  workspace.
- Decide how Devin patches, intervention events, model/configuration, elapsed
  time, and usage/cost will be exported without exposing the reference patch.
- Perform a fresh agent-workspace audit before every future Devin run.
