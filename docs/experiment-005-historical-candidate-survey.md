# Experiment 005 Historical Candidate Survey

## Survey scope and method

The survey inspected all 501 records across the 17 projects in the pinned
[BugsInPy corpus](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac)
at commit `316b95e2353ecda832bad9b42f86fa7c2fcec8ac`. Twenty candidates were
then retained for serious comparison. For each, the survey read the immutable
bug metadata, upstream regression-test command, buggy/fixed revisions, and
unified patch. Production-file counts exclude tests and documentation.

The acceptance screen was software-reasoning difficulty, not setup pain:
multi-module interaction, a symptom/root-cause gap, a meaningful behavioral
contract, a plausible incomplete repair, deterministic local testing, and no
required network, native stack, enormous suite, or obsolete-runtime workaround.
The five accepted cases are deliberately public/known. BugsInPy is a
provenance source, not a novelty source.

## Serious-candidate matrix

The `harder than E002` and `easier/risk` columns record the reason on both
sides of the decision. This avoids treating a large patch or a mature project
as automatic evidence of reasoning difficulty.

| Candidate and immutable record | Revisions | Production footprint / interacting subsystem | Symptom → root cause; visible test; held-out potential | Environment / regression | Harder than E002 because | Easier or risky because | Decision |
|---|---|---|---|---|---|---|---|
| [fastapi-1](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/fastapi/bugs/1) | `766157b…` → `3397d4d…` | 4 production files, 5 total, +207/-16; application decorators, router/APIRoute, response serializer, encoder, OpenAPI | response options rejected in an encoder test; root is option propagation across API and serialization boundaries (distance 3); visible `test_jsonable_encoder.py`; held-out direct, nested, and router response contracts are deterministic | Python 3.8-era FastAPI/Pydantic/Starlette; no network; ordinary encoding regression is local | Four production modules and multiple public entry points versus E002 FastAPI-3’s one-file +25/-7 repair | The requested feature is visible in a test name and the patch is broad but repetitive | **Accept K01** |
| [luigi-23](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/luigi/bugs/23) | `c707253…` → `dc41727…` | 2 production files, +7/-2; interface factory, scheduler configuration, worker/task pruning | external dependency retry stalls in worker test; root is the default factory/config path rather than the worker assertion (distance 3); visible `test_external_dependency_completes_later`; held-out factory, explicit config, and normal dependency scheduling | Python 3.8, local scheduler, no network; deterministic worker test | State/config propagation across factory, scheduler, and external-task lifecycle versus E002’s mostly local repairs | The reference patch is compact and the configuration flag is discoverable after tracing | **Accept K02** |
| [tornado-6](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/tornado/bugs/6) | `fb74e48…` → `2905ee4…` | 2 production files, +16/-2; IOLoop adapter map and asyncio adapter lifecycle | loop leak count grows after close; root is ownership/cleanup coordination between Tornado and asyncio maps (distance 3); visible two `LeakTest` methods; held-out repeated close, externally closed loop, and new registration | Python 3.8-compatible Tornado source; standard library only; deterministic memory-map assertions | Lifecycle state crosses two adapters and two close paths, unlike E002 Tornado-13’s narrow HTTP state edge | The focused tests are small and the source files are adjacent | **Accept K03** |
| [ansible-13](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/ansible/bugs/13) | `41472ee…` → `694ef56…` | 2 production files, +15/-3; Galaxy CLI argument classification and collection artifact resolver | URL is split into namespace and requirement; root is the CLI/downstream input contract (distance 2); visible `test_collection_install_with_url`; held-out local path, mixed-case scheme, and ordinary namespace parsing | Python 3.8 with local mocks; no download; regression is one ordinary requirement tuple | Two-layer input classification and alternate artifact paths versus E002 Scrapy-3’s one production file +5/-2 | The sanitized checkout is 17,954 files, so repository bulk and dependency surface would dominate the reasoning signal | Reject |
| [thefuck-16](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/thefuck/bugs/16) | `d92765d…` → `bb5f6bb…` | 4 production files, +11/-7; Bash/Zsh/Fish generators and command-type environment logging | aliases set correction context before command substitution; root is shell evaluation scope across implementations (distance 2); visible Bash/Zsh alias tests; held-out both aliases, Fish, and ordinary parser behavior | Python 3.8, shell-string tests only; no external command or network; deterministic | Three shell implementations plus environment-sensitive command construction versus E002’s one-file Black-16 and tqdm-5 cases | Alias output is textual and a strong agent may identify the ordering quickly; this is intentionally the lower-hard member | **Accept K05** |
| [scrapy-33](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/scrapy/bugs/33) | `2d21677…` → `6dccb3a…` | 8 production files, +186/-49; engine, scraper, robot middleware, feed exporter, logging, pipelines, signals | media pipeline/logging failure crosses many components; visible two upstream tests; strong held-out and regression surface | Python 3.8 plus Twisted, media, and logging stack; broad setup and possible incidental failures | Broadest cross-component graph in the survey | 430-line patch and dependency breadth make evaluator failures hard to attribute; difficulty would be infrastructure-heavy | Reject |
| [keras-20](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/keras/bugs/20) | `76da5f0…` → `6dd087a…` | 5 production files, 236 changed lines; backend adapters, convolution utilities, convolutional layers | convolution behavior differs by backend; visible layer test; held-out backend/shape contract is possible | TensorFlow/CNTK/Theano and native numerical dependencies | Multiple backend branches and broad patch | Native stack and obsolete Keras dependencies violate the reproducibility screen | Reject |
| [pandas-44](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/pandas/bugs/44) | `96d22d4…` → `5081748…` | 5 production files, 221 changed lines; base, datetime, period, timedelta, numeric indexes | index operation fails across dtype families; visible base/indexing tests; broad dtype held-out possible | NumPy/Cython/pandas build and old Python 3.8 pins | Multi-family dispatch and high patch breadth | Compiled dependency setup and version archaeology dominate | Reject |
| [youtube-dl-42](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/youtube-dl/bugs/42) | `b853d2e…` → `5aafe89…` | 4 production files, 89 changed lines; XML utility and three extractors | malformed ampersands break utility/extractor behavior; visible utility test; held-out XML variants possible | Network-facing extractor project even though the selected unit test is local | Utility-to-consumer propagation across several extractors | Root is a straightforward utility rename and the surrounding extractor surface invites network leakage | Reject |
| [pandas-167](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/pandas/bugs/167) | `6af6d51` → `2263982…` | 4 production files, 87 changed lines; base/indexing plus datetime/period indexes | partial string slice is classified incorrectly; visible datetime slicing test; held-out Series/DataFrame variants possible | Old pandas numerical build | Non-local indexing protocol and several index classes | Build/version risk and a large unrelated regression surface | Reject |
| [pandas-79](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/pandas/bugs/79) | `38ea154` → `0b0cd08…` | 4 production files, 80 changed lines; Series, MultiIndex, DatetimeIndex, grouper | invalid key handling is normalized at several index layers; visible datetime indexing test; held-out scalar/list key cases possible | Old pandas numerical build | Four-module exception/data-flow path | Compiled dependency and Python-version risk exceed software reasoning signal | Reject |
| [pandas-123](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/pandas/bugs/123) | `b6d64d2` → `17fe9a4…` | 3 production files, 91 changed lines; base, numeric, and range indexes | dtype validation accepts an invalid combination; visible numeric/range index tests; held-out constructor matrix possible | Old pandas numerical build | Cross-class validation contract and multiple constructors | Environment setup is the dominant uncertainty | Reject |
| [black-6](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/black/bugs/6) | `8c8aded…` → `f8617f9…` | 3 production files, 273 changed lines; formatter, grammar driver, tokenizer | async syntax is parsed under the wrong target version; visible formatter tests; held-out target-version matrix possible | Python 3.8 parser and Black dependencies | Parser/tokenizer interaction and broad patch | Same upstream project as E002 Black-16 and Python grammar-version sensitivity | Reject |
| [matplotlib-1](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/matplotlib/bugs/1) | `c404d1f…` → `5324ada…` | 3 production files, 114 changed lines; backend renderer, figure, tight layout | tight bounding-box rendering fails; visible bbox test; held-out renderer lifecycle possible | Matplotlib backend/native/display stack | Renderer ownership crosses three modules | Native/display behavior and backend nondeterminism are disqualifying risks | Reject |
| [cookiecutter-4](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/cookiecutter/bugs/4) | `9568ab6…` → `457a1a4…` | 3 production files, 85 changed lines; hook runner, generator, exceptions | failing hook is not surfaced with the intended exception; visible hook test; held-out hook success/failure possible | Filesystem and subprocess behavior under old tox/Python 3.5 | Error propagation crosses generator and hook layers | Process/filesystem setup and obsolete Python constraint overshadow reasoning | Reject |
| [scrapy-30](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/scrapy/bugs/30) | `4d41cc0…` → `3e6d6c4…` | 1 production file plus test helpers; command discovery and subprocess test utility | Python 2/3 mapping API breaks command version output; visible version test; held-out discovery ordering possible | Python 3.8 and Twisted-adjacent project | Compatibility boundary is real but narrow | One local mapping call, same project as E002 Scrapy-3, and little behavioral breadth | Reject |
| [scrapy-23](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/scrapy/bugs/23) | `c9e046d…` → `f042ad0…` | 1 production file plus a neighboring test; proxy middleware bytes | proxy authorization is built with text instead of bytes; visible proxy-auth tests; held-out empty-password/header contract | Python 3.8, local request objects | Boundary conversion is a legitimate protocol issue | Single-file local type conversion and same-project duplication make it below hard-tier target | Reject |
| [luigi-9](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/luigi/bugs/9) | `f7e0b77…` → `b711597…` | 1 production file, 86 changed lines; execution summary status sets | retry history is reported as current failure; visible summary test; held-out retry/status matrix possible | Python 3.8 local scheduler data | Historical state interpretation can fool a visible assertion | Root and symptom are in one module and the project already appears as K02 | Reject |
| [tornado-10](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/tornado/bugs/10) | `ecd8968…` → `5931d91…` | 2 production files, 25 changed lines; RequestHandler/WebSocket close lifecycle | WebSocket close timing leaves a reference cycle; visible render-message test; held-out ordinary handler versus 101 WebSocket lifecycle | Python 3.8, local Tornado tests; deterministic and network-free | Two lifecycle owners and a status-code branch, with a downstream visible symptom | It duplicates K03’s project and lifecycle family, but is materially smaller and cleaner than Ansible’s repository-heavy alternative | **Accept K04** |
| [thefuck-17](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/thefuck/bugs/17) | `f7f0660…` → `7ce4307…` | 2 production files, 52 changed lines; Bash/Zsh alias and alias-cache parsing | aliases do not expose existing aliases during correction; visible Bash tests; held-out alias parsing possible | Python 3.8, shell strings | Cross-shell environment/cache boundary | Narrower than K05 and same project; K05 covers three shell implementations | Reject |

## Selected-case records

### E005-K01 — FastAPI bug 1

Provenance is the BugsInPy record and the upstream FastAPI revisions shown in
the provenance table. The historical patch changes
`fastapi/applications.py`, `fastapi/encoders.py`, `fastapi/openapi/utils.py`,
and `fastapi/routing.py` (+207/-16 in production, plus one upstream test
file). The visible failure is an encoder test, but the root cause is distributed
through decorator defaults, APIRoute state, response serialization, and direct
encoding. That symptom/root-cause distance and four-file propagation are the
main reason it is harder than E002 FastAPI-3, whose reference repair centers on
one routing file (+25/-7). The private held-out contract tests direct model
encoding, container composition supported by the historical implementation,
and router-backed responses; it asserts values, not patch shape.

### E005-K02 — Luigi bug 23

The patch changes `luigi/interface.py` and `luigi/scheduler.py` (+7/-2). The
visible worker test exercises an external dependency that becomes complete
later, while the defect is in the factory/configuration path that determines
whether pruning runs before work selection. This is a three-step factory →
scheduler config → worker lifecycle path, materially wider than the local
Tornado-13 and tqdm-5 E002 repairs. Held-out tests check both factory-created
and explicitly configured schedulers and retain ordinary dependency ordering.
The evaluator uses a local scheduler and no network.

### E005-K03 — Tornado bug 6

The patch changes `tornado/ioloop.py` and `tornado/platform/asyncio.py`
(+16/-2). The visible leak count is a downstream symptom; the cause is stale
ownership between Tornado’s wrapper map and two different loop-closing paths.
The held-out tests cover immediate cleanup for Tornado-owned closes, deferred
cleanup for asyncio-owned closes, repeated creation, and valid open-loop
registration. Compared with E002 Tornado-13’s narrow HTTP lifecycle repair,
K03 requires tracing two adapters and a persistent mapping while remaining
standard-library deterministic.

### E005-K04 — Tornado bug 10

The patch changes `tornado/web.py` and `tornado/websocket.py` (+13/0). The
visible render-message test fails because the generic request-handler finish
path breaks template-related cycles before an established WebSocket has
actually closed. Held-out tests distinguish ordinary/failed-handshake cleanup
from the status-101 established-connection path. It is a middle-hard case:
the repair crosses two lifecycle owners and a status-code branch, while
remaining compact, deterministic, and local.

### E005-K05 — thefuck bug 16

The patch changes `thefuck/shells/bash.py`, `fish.py`, `zsh.py`, and
`types.py` (+11/-7). The visible Bash/Zsh tests assert the generated alias
shape, while the reasoning issue is command-substitution environment scope
across three shell generators. Held-out tests require both Bash and Zsh to
scope context inside the alias and verify the Fish generator’s parallel
contract; regression tests retain alias parsing and shell conversion. This is
the lower-hard case: it is broader than E002’s one-file shell-adjacent
comparators but a strong agent may recognize the textual ordering quickly. It
remains in the set because it is deterministic, public, multi-implementation,
and supplies useful lower-hard variation without setup-derived difficulty.

## Acceptance summary

All five accepted cases have multiple relevant production modules. K01-K03
have a symptom/root-cause distance of three; K04-K05 have distance two. All
five have a plausible local repair that can satisfy a narrow visible check but
fail the broader held-out contract: encoder-only or route-only propagation,
config-only scheduler changes, one-sided loop cleanup, immediate WebSocket
cycle breaking, or Bash-only alias correction. Four cases are middle/upper
hard; K05 is lower-hard by design. The private repeat validator reproduced the
buggy target failure and fixed pass for public, held-out, and regression groups
under deterministic local execution.
