# Experiment 004 difficulty calibration

Status: frozen with private ground truth; no Devin or SWE-2 execution was
performed during design or validation.

## Calibration rule

E004 targets the observed structural and reasoning envelope of E002. The
calibration uses repository and task properties that are fixed before agent
execution: baseline file count, source-module count, manually identified
relevant modules, call/data-flow depth, behavioral-contract breadth, visible
versus held-out separation, source files in the minimal patch, and reference
patch line counts. It does not use agent time, agent steps, or agent success as
a tuning signal, and it does not use E003 as a target.

The historical E002 file counts below include the sanitized task workspace and
exclude generated virtual-environment/cache churn. E002 source patch sizes are
the human reference patches, not the larger generated-file diffs recorded in
some agent workspaces.

## E002 reference distribution

| E002 case | Baseline files | Relevant source files observed in reference | Reference patch | E002 observed wall / steps | Main reasoning shape |
|---|---:|---:|---:|---:|---|
| black-16 | 112 | 1 | +14/-1 | 366–400 s / 36–47 | repository discovery and path-boundary behavior; visible failure is close to discovery logic |
| fastapi-3 | 686 | 1 | +25/-7 | 299–1,138 s / 35–69 | nested response transformation, aliases, and exclude-unset behavior in a large framework |
| scrapy-3 | 473 | 1 | +5/-2 | 818–1,380 s / 62–91 | downstream URL/protocol symptom with broader request-method and scheme behavior |
| tqdm-5 | 39 | 1 | +7/-6 | 157–405 s / 22–42 | state initialization where public success can miss the sized-iterable contract |
| tornado-13 | 295 | 1 source target; reference also records a test file | +4/-1 | 176–326 s / 33–36 | HTTP state/lifecycle edge case with a narrow defensive repair |

E002 therefore spans very small to very large repositories, but the source
repair itself is usually narrow. The central E004 adjustment is to keep the
repair bounded while increasing the number of modules whose contracts must be
understood. This is the design response to E003's five near-local one-file
cases.

## Case-by-case comparison

| E004 case | Baseline files / source modules | Relevant modules / reference files | Reference patch | Data-flow and contract breadth | Closest E002 comparison | E002-like evidence |
|---|---:|---:|---:|---|---|---|
| E004-N01 buildgraph | 21 / 12 | 3 / 1 | +10/-3 | graph loader → dependency graph → cached planner; transitive and shared invalidation plus unrelated-cache preservation | FastAPI 3; Scrapy 3 | multi-stage derived behavior, downstream stale result, bounded source patch |
| E004-N02 taskqueue | 21 / 13 | 3 / 1 | +3/-0 | job runner → lease → pool return; healthy reuse, failed-resource replacement, capacity and idempotent release | Tornado 13; tqdm 5 | lifecycle/state boundary and public-versus-broader resource contract |
| E004-N03 preferences | 18 / 10 | 2 / 1 | +4/-3 | edit context → snapshot/replace boundary → nested mutable values; atomic rollback and ownership isolation | FastAPI 3; tqdm 5 | nested state semantics, small reference repair, held-out alias cases |
| E004-N04 signalhub | 17 / 10 | 3 / 2 | +4/-1 | event hub → subscription collection → callback; mutation during delivery, once semantics, and synchronous reentrancy | Tornado 13; Scrapy 3 | protocol-like lifecycle state, downstream callback effect, two-module reference repair |
| E004-N05 reportpipe | 19 / 11 | 3 / 1 | +0/-2 | input → assembler → batch → writer; full and partial batches, sequence preservation, and idempotent finalization | Scrapy 3; tqdm 5 | downstream symptom, visible/held-out contract split, minimal repair |

### Why each may be easier than its comparison

- N01 has far fewer total files than FastAPI or Scrapy and a shorter graph than
  a mature framework's nested response path.
- N02 has no network protocol, external service, or dependency setup, and the
  reference repair is smaller than the Tornado and tqdm references.
- N03 uses a small in-memory store and the ownership failure is a familiar
  shallow-copy pattern; it is materially smaller than FastAPI.
- N04 has no asynchronous scheduling or I/O, and a stable-snapshot repair is
  compact once the mutation semantics are understood.
- N05 has the smallest patch and no external serialization or transport layer;
  the visible symptom can lead directly to the writer boundary.

### Why each may be harder than its comparison

- N01 requires tracing invalidation beyond the changed node and preserving an
  unrelated cached target, rather than changing one local response or path
  condition.
- N02 requires following an exception across the runner, lease, and pool and
  distinguishing a released lease from a healthy reusable worker.
- N03 requires reasoning about nested aliases across both rollback and commit;
  a fix for only the visible exception path can leave caller-owned data shared.
- N04 requires a contract for the whole delivery cycle. A repair that handles
  self-removal can still incorrectly run newly added subscribers or disturb
  nested publish order.
- N05 requires understanding that the assembler's `complete` flag is metadata
  and not a permission to discard a non-empty final batch. A visible-only
  repair can still mishandle repeated finalization or sequence order.

## Set assessment

The set is intentionally below E002 in raw repository size, because the brief
forbids making difficulty depend on enormous repositories or dependency
installation. It is above E003 in relevant-module count: three of five cases
require reasoning across three modules, and two cases have minimal reference
patches in two source files or a public API boundary. All five separate a
legitimate visible symptom from a broader held-out contract, while the
reference patches remain in E002's compact range.

Qualitative assessment: approximately E002-equivalent as a set on software
reasoning, with N03 and N05 toward the easier side, N02 and N04 near the
middle, and N01 toward the harder end. This is a calibration judgment, not a
claim of numerical equivalence. The largest residual uncertainty is that
synthetic projects cannot reproduce the incidental discovery cost of mature
frameworks such as FastAPI, Scrapy, or Tornado; that limitation is recorded
explicitly rather than hidden by an invented precision score.
