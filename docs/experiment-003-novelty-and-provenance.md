# Experiment 003 Novelty and Provenance

## Claim boundary

E003 does not claim that its cases could not have appeared in training data.
The supported claim is:

> The E003 benchmark instances, defect implementations, prompts, reference fixes, and held-out behavioral evaluations were newly constructed for this experiment and withheld from Devin until the experimental protocol was frozen and execution began.

## Provenance record

The private staging area records creation and freeze timestamps, deterministic
hashes for every buggy and fixed case tree, every reference patch, each visible
and evaluator-side test, every task prompt, the run order, model assignments,
evaluator version, and isolation configuration version. The public freeze
manifest contains hashes only; it does not contain source or evaluator files.

The private staging area is outside the control repository. The control
repository contains no E003 source, fixed implementation, reference patch,
held-out test, task prompt, or solution metadata.

## Embargo rule

Until all ten E003 runs are closed, do not publish the private case trees,
fixed trees, reference patches, held-out tests, or solution-bearing metadata.
That embargo ended after the tenth run closed. Following a separate security
and leak review, the public package now includes the E003 case trees, visible
tests, held-out behavior tests, regression tests, reference patches, and safe
case manifests under `artifacts/experiment-003/cases/`. Raw session exports,
credentials, hidden reasoning, and private environment dumps remain excluded.

The v2 publication report combines E002 and E003 descriptively while keeping
their historical-versus-novel provenance separate. It makes no claim that the
novel cases were absent from training data.
