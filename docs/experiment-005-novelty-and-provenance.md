# Experiment 005 Novelty, Provenance, and Embargo

The defensible novelty claim is limited to this: E005's five project
instances, buggy implementations, prompts, fixed trees, reference repairs,
and evaluator tests were newly constructed for this experiment and withheld
from Devin until after freeze. Absence from unknowable model training corpora
is not claimed.

E005-specific private staging records source and fixed-tree hashes, prompt and
test hashes, reference-patch hashes, timestamps, and the pre-execution
invocation count. The public freeze manifest records hashes and configuration
only, not source, fixed code, hidden tests, evaluator logic, or construction
notes.

Solution-bearing material stays under the ignored local E005 staging root until
all ten sessions close. It includes buggy and fixed trees, public tests,
held-out tests, regression tests, prompts, metadata, reference patches,
agent-workspace exports, and validation output. No E004 file or experimental
content is copied, changed, or reconciled by this experiment.

## Fail-closed leak audit

The private validator rebuilds each agent workspace from the buggy tree only,
adds its task prompt, excludes fixed/evaluation/metadata material, scans paths
and text for forbidden solution or benchmark markers, and fails rather than
continuing on any finding. The evaluator is never part of that workspace.
