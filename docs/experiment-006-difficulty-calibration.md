# Experiment 006 Difficulty Calibration

E006 is calibrated against the observed E005 hard tier and the E002 historical
moderate tier. This is a structural forecast made without Devin, SWE-2, or
any autonomous coding agent; it is not a prediction of success or wall time.

## Evidence from E005

The E005 ledger recorded 10 unique cases and 20 planned runs. Its paired
outcomes were five both-success, two Medium-only, one Max-only, and two
both-fail pairs; Medium completed 7/10 and Max 6/10. The E005 actual Max wall
times averaged about 438 seconds, with a 5,400-second ceiling. That result is
calibration evidence only: the ceiling is an execution allowance, not a
difficulty score. E005's hard cases commonly crossed two to four relevant
modules, whereas the E002 historical controls were mostly one-production-file
repairs.

The full E005 workload evidence was also considered. Medium averaged 186.052
wall seconds, 28.0 steps, 29.3 tool calls, 319,031 prompt tokens, 2,871
completion tokens, and 310,943 cached tokens; Max averaged 438.385 seconds,
38.1 steps, 39.8 tool calls, 498,938 prompt tokens, 5,348 completion tokens,
and 481,869 cached tokens. Max took longer in all ten pairs, used more steps
in nine, more tool calls in nine, and more prompt and completion tokens in all
ten. Source patches averaged +18.3/-3.5 lines over 1.9 files for Medium and
+22.1/-4.2 over 2.0 files for Max. These paired resource deltas are why E006
keeps the same two-model comparison and removes step/token caps; they are not
treated as a proxy for intrinsic reasoning or as a target to reproduce.

## Case-level structural matrix

Scores are ordinal review notes: 1 = E002-like, 3 = E005-like, and 5 = a
clear capability-frontier stressor. “Distance” measures the number of
semantic handoffs from visible symptom to the mutated state, not repository
size. “Shortcut risk” measures how likely a plausible local fix is to pass the
visible test while violating the broader contract.

| Case | Relevant modules | State / flow depth | Competing hypotheses | Ref breadth | Contract scenarios | Shortcut risk | Band |
|---|---:|---:|---:|---:|---:|---:|---|
| K01 black-6 | 3 production / parser stack | 5 / 5 | 4 | 3 files, +109/-17 | 3 behavior + regression | 5 | upper-very-hard |
| K02 PySnooper-1 | 3 conceptual / 2 production | 4 / 4 | 4 | 2 files, +8/-4 | 3 behavior + regression | 4 | middle-very-hard |
| K03 black-23 | 3 conceptual / 2 production | 5 / 5 | 5 | 2 files, +51/-13 | 3 behavior + regression | 5 | upper-very-hard |
| K04 thefuck-17 | 3 conceptual / 2 production | 4 / 4 | 4 | 2 files, +6/-10 | 2 behavior + regression | 4 | middle-very-hard |
| K05 tqdm-2 | 3 conceptual / 2 production | 3 / 3 | 3 | 2 files, +6/-6 | 2 behavior + regression | 3 | lower-very-hard |
| H01 feature-store | 5 | 4 / 5 | 4 | 2 source files | 4 behavior + regression | 5 | upper-very-hard |
| H02 work-queue | 4 | 4 / 5 | 4 | 1 source file | 4 behavior + regression | 5 | middle-very-hard |
| H03 wire-relay | 4 | 5 / 5 | 5 | 2 source files | 4 behavior + regression | 5 | upper-very-hard |
| H04 account-ledger | 4 | 5 / 4 | 4 | 2 source files | 4 behavior + regression | 5 | middle-very-hard |
| H05 profile-runtime | 5 | 4 / 4 | 4 | 1 source file | 4 behavior + regression | 4 | middle-very-hard |

## Why this exceeds E005

The historical half is not a second copy of the E005 symptom set. K01 and K03
require grammar/token/parser-state tracing; K02 requires byte decoding and
loader fallback reasoning; K04 requires shell-process/environment ownership;
and K05 requires display-width state preservation. Each visible test gives a
reproducible failure, but the held-out checks exercise an adjacent contract.
The novel half combines transaction boundaries, transitive lineage, retry
attempt ownership, malformed-stream recovery, reentrant event dispatch, and
cache identity. These are small synthetic repositories, so difficulty comes
from state and contract breadth rather than setup pain.

The selection deliberately mixes upper, middle, and lower anchors. K05 may be
too easy for a strong agent; it remains as a compact lower anchor so the tier
does not confuse repository size with capability. H02 and H05 are similarly
compact but have high incomplete-repair risk. No timing threshold, native
dependency, network call, or generated artifact is used to manufacture
difficulty.

The final very-hard decision is therefore evidence-backed but not overclaimed:
it predicts more coupled investigation and broader behavioral validation than
E005, while leaving realized model outcomes entirely to a future authorized
run.
