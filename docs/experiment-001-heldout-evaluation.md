# Experiment 001 held-out evaluation

This document records the evaluator-side suite frozen for Experiment 001.
The files under `evaluation/experiment-001/` are never copied into a Devin
workspace. The checks were run against the existing Phase 1 verification trees
using fresh external Python environments; no Devin session was started.

## Readiness summary

| Case | Held-out tests | Buggy fails | Fixed passes | Regression command(s) | Environment | Ready |
|---|---:|:---:|:---:|---|---|:---:|
| E001-C01 Black 16 | 1 | yes | yes | `python -m unittest -q tests.test_black.BlackTestCase.test_broken_symlink`; `...test_include_exclude` | Python 3.8.20; Black runtime pins | yes |
| E001-C02 FastAPI 3 | 2 | yes | yes | `pytest -q tests/test_response_model_invalid.py` | Python 3.8.20; FastAPI 0.55.1 / Pydantic 1.5.1 | yes |
| E001-C03 Scrapy 3 | 1 | yes | yes | `pytest -q ...test_redirect_3xx_permanent`; `...test_latin1_location` | Python 3.8.20; Scrapy 2.1.0 | yes |
| E001-C04 tqdm 5 | 1 | yes | yes | `pytest -q tqdm/tests/tests_tqdm.py::test_disable`; `...::test_repr` | Python 3.8.20; pytest 5.4.3 / nose 1.3.7 | yes |
| E001-C05 Tornado 13 | 1 | yes | yes | `python -m unittest -q tornado.test.httputil_test` | Python 3.9.25; Tornado 6.0.4 | yes |

The exact command strings, environment pins, and per-command output are in
each case's evaluator-only `metadata.json` and `validation.json`.

## Case details

### E001-C01 — Black 16

The held-out test creates a real temporary workspace containing an in-root
Python file and a Python symlink to a file outside the root. Directory
discovery must return the in-root file, ignore the external target, and not
raise. The historical regression used mocks; this is an independent real
filesystem check. The buggy run fails with the intended `ValueError` from the
out-of-root path calculation. The fixed run passes. The neighboring broken-
symlink and include/exclude checks pass on both trees.

Limitation: symbolic links must be available on the evaluator host.

### E001-C02 — FastAPI 3

The held-out suite exposes two endpoints with new model names and new values:
one nested list and one mapping of lists. Both use an aliased required field,
an optional field, and `response_model_exclude_unset=True`. The expected JSON
must preserve aliases, omit unset fields, and retain explicitly set values.
This tests the external response contract and accepts any implementation that
produces the same JSON. Both buggy tests fail with response validation errors
for the missing aliased field; both fixed tests pass. The invalid-response
model tests pass on both trees and are used as the regression subset.

Limitation: the suite is intentionally pinned to the historical FastAPI /
Pydantic compatibility environment.

### E001-C03 — Scrapy 3

The held-out test sends a 302 response with a three-slash `Location` value to
the redirect middleware for an HTTPS GET request. The returned request must
use the original scheme, the redirect host, the normalized path, and the GET
method. It uses different scheme, hosts, method, and path from the historical
HEAD regression. The buggy URL retains the origin host and treats the value as
a path; the fixed URL is the protocol-relative target. The two neighboring
redirect checks pass on both trees.

Limitation: no network access is required or used; only middleware behavior is
tested.

### E001-C04 — tqdm 5

The held-out test constructs a disabled wrapper around a fresh three-element
list and checks its public `total` and `len()` values. The buggy tree raises
`AttributeError` because the inferred total is absent on the disabled early
return; the fixed tree reports three and passes. The disable and
representation regression checks pass on both trees; the regression subset
does not rely on an upstream test that is skipped by its own compatibility
guard in this environment.

Limitation: the historical test support layer requires old pytest/nose pins.

### E001-C05 — Tornado 13

The held-out test performs a local socket round trip and asks a client
`HTTP1Connection` to read a bodyless HTTP/1.0 204 response with no
`Content-Length`. It checks the received status and empty body. This uses a
different status and response shape from the historical test while exercising
the externally observable HTTP parsing path. The buggy tree raises the
intended `ResponseStartLine` missing-`method` `AttributeError`; the fixed tree
passes. The 30-test `httputil_test` module passes on both trees.

Limitation: the evaluator host must permit loopback socket creation.

## Scoring and evaluator errors

The evaluator now records `heldout_tests`, `regression_tests`, and
`evaluation_status`. `task_success` (and the legacy `pass` field) is true only
when the held-out suite, the required public tests, and the configured
regression suite all pass. A missing or invalid evaluator suite, a held-out
workspace/setup error, or a timed-out evaluator command is recorded as
`EVALUATION_ERROR` with a null success value; a missing held-out execution is
also never silently converted to an agent failure. An ordinary assertion/test
failure remains an ordinary failed task result.

## Leak audit and export validation

The exporter audit rejects held-out evaluator basenames in an agent export,
along with the existing fixed-commit, reference-patch, metadata, history, and
control-repository checks. The ten fresh exports were regenerated after this
change and all ten leak audits passed. The held-out files remain only in the
control repository's evaluator directory.
