# BugsInPy candidate survey

Survey basis: BugsInPy dataset commit
`316b95e2353ecda832bad9b42f86fa7c2fcec8ac`, 17 projects and 501 numbered bug
records. The survey used project metadata, triggering test names, dependency
metadata, changed-file/patch size, and the source project's reproducibility
records. It did not copy any source project into this repository.

Difficulty is an initial evaluation estimate, not a claim about agent success.
"Good test" means a useful balance of locality, reliable oracle, realistic
debugging, and manageable environment setup.

| Candidate | Project / BugsInPy bug | Original repository | Affected functionality and bug shape | Difficulty | Environment concerns | Agent-test assessment |
|---|---|---|---|---|---|---|
| 1 | PySnooper 2 | [cool-RR/PySnooper](https://github.com/cool-RR/PySnooper) | Tracing custom value representations and related output behavior | medium-high | Python 3.8; pytest; tracing/introspection edge cases | Good debugging signal, but the historical change spans several tracing concerns, so scope should be checked carefully. |
| 2 | Black 1 | [psf/black](https://github.com/psf/black) | Formatting in a host where multiprocessing is unavailable | medium | Python 3.8; unittest; process behavior can vary by runner | Realistic and local, but platform-dependent. Keep as an alternate if the consumer runner supports the scenario. |
| 3 | Black 16 | [psf/black](https://github.com/psf/black) | Directory traversal when a symlink resolves outside the processing root | medium | Python 3.8; unittest; local filesystem symlink support | Strong: deterministic local reproduction, clear oracle, one production file, and a meaningful boundary-condition diagnosis. |
| 4 | Black 20 | [psf/black](https://github.com/psf/black) | Expression-diff labels for files whose path is not just a basename | low | Python 3.8; unittest | Reliable but likely too obvious for a primary case; useful as a calibration case only. |
| 5 | Cookiecutter 2 | [cookiecutter/cookiecutter](https://github.com/cookiecutter/cookiecutter) | Discovery and execution of multiple matching template hooks | medium | Python 3.6; tox and pinned packages; no external service | Strong: realistic filesystem/process behavior and a test that exercises a small but nontrivial control-flow contract. |
| 6 | FastAPI 3 | [tiangolo/fastapi](https://github.com/tiangolo/fastapi) | Nested response-model serialization with unset fields and aliases | medium-high | Python 3.8; pytest; old Pydantic/FastAPI dependency pins | Strong: recognizable framework behavior, multiple related tests, and a clear semantic oracle; dependency pinning must be containerized. |
| 7 | FastAPI 9 | [tiangolo/fastapi](https://github.com/tiangolo/fastapi) | OpenAPI/body-schema media type selection for body parameters | medium | Python 3.8; pytest; old Pydantic/FastAPI pins | Good alternate: focused framework logic and no paid service, though API-schema tests can be more exposed to dependency drift. |
| 8 | HTTPie 2 | [jakubroztocil/httpie](https://github.com/jakubroztocil/httpie) | Client-side maximum redirect handling | medium | Python 3.7; pytest; mocked HTTP behavior | Good local CLI/client case, but its historical fix is compact and may be easier than the target mix requires. |
| 9 | Sanic 3 | [huge-success/sanic](https://github.com/huge-success/sanic) | Host-aware URL generation for routes | medium-high | Python 3.8; async web framework/event loop dependencies | Interesting routing case with a clear test, but event-loop compatibility should be validated before selection. |
| 10 | Scrapy 3 | [scrapy/scrapy](https://github.com/scrapy/scrapy) | Redirect middleware handling of a relative redirect | medium | Python 3.8; Twisted and several optional packages in dataset setup | Strong if the pinned Twisted stack installs: realistic URL middleware, local unit test, no network service required. |
| 11 | spaCy 7 | [explosion/spaCy](https://github.com/explosion/spaCy) | Selection and ordering of overlapping document spans | medium-high | Python 3.7; compiled numerical/NLP dependencies | Good semantic debugging task, but heavier native dependencies and version risk make it a backup for Experiment 001. |
| 12 | Tornado 13 | [tornadoweb/tornado](https://github.com/tornadoweb/tornado) | HTTP/1.x connection persistence when a response lacks content length | medium-high | Python 3.7; unittest; protocol-state test is local | Strong: recognizable protocol behavior, deterministic local test, and a nontrivial state/role distinction. |
| 13 | tqdm 5 | [tqdm/tqdm](https://github.com/tqdm/tqdm) | Progress-bar state when display is disabled but an iterable has a length | medium | Python 3.6; pytest; small pinned dependency set | Strong alternate and likely easy to reproduce; useful for lowering the difficulty mix if a heavier case is blocked. |
| 14 | matplotlib 16 | [matplotlib/matplotlib](https://github.com/matplotlib/matplotlib) | Colorbar behavior in a focused axes test | medium-high | Python 3.7; compiled plotting stack; possible display/backend issues | Realistic but less attractive initially because native builds and rendering backends add noise. |

## Recommended five for Experiment 001

1. **Black 16** — stable, local symlink boundary case.
2. **FastAPI 3** — framework serialization semantics with several related tests.
3. **Scrapy 3** — middleware/URL behavior in a recognizable OSS project.
4. **Tornado 13** — protocol-state reasoning with a deterministic unit test.
5. **tqdm 5** — a smaller, pure-Python state-management case that lowers setup risk.

**Cookiecutter 2** remains a strong alternate, but its BugsInPy command invokes
the project's multi-version tox matrix and was not promoted until a Python 3.6
runner is available. Cases should remain in the recommended set only after both
buggy-fail and fixed-pass checks succeed in the same pinned runner.
