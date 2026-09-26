> **Publication context:** This frozen pre-run document records the catalog-based expectation and budget controls as they were written before execution. They are planning assumptions only, not billed or actual cost. No account billing evidence was available; actual monetary cost is unknown.

# E007 Protocol

## Study framing

E007 is an independent replication of SWE-2 effort-level behavior in the frozen MAJOR//minor 30-case primary benchmark, with SWE-2 High added as a third condition. It is not a comparison of old Devin with SWE-2.

## Design

The experimental unit is one case-condition run. Each of the 30 canonical cases is run once with each condition: `swe-2-medium`, `swe-2-high`, and `swe-2-max` (90 total). The canonical case order and exact case data are in `E007-MANIFEST.json`. Moderate, hard, and very-hard each contain ten cases. The five-case E003 pilot is supplemental and excluded.

The current Devin CLI selects SWE-2 effort through explicit model variants (`--model swe-2-medium|swe-2-high|swe-2-max`), rather than a separate effort flag. All other model settings remain default and identical. Model availability and labels were inspected with Devin CLI 3000.10.21 on 2026-09-25; all three variants appeared under SWE-2 and were labeled Free.

## Outcomes

Primary outcome is the existing frozen binary `TASK_SUCCESS`: public checks, held-out behavioral checks, and regression checks all pass. Evaluator/infrastructure faults are separately classified; they are not counted as agent failures or successes. No scoring changes are permitted. Each run also records per-suite result, failure class, infrastructure state, timestamps, elapsed wall time, and available Devin session telemetry. Behavioral telemetry is secondary and cannot change the primary score.

## Controls

Use the identical frozen task prompt, source tree/base commit (or frozen source snapshot for locally constructed cases), held-out tests, regression suite, evaluator, permissions, environment, resource limits, and zero-substantive-intervention policy defined by each source experiment and referenced by the E007 manifest. Each run receives a fresh isolated workspace. Evaluators and reference fixes remain unavailable to Devin until the run is closed. Do not repair prompts or failed cases after observing outcomes. Do not repeat ordinary task failures. Infrastructure/authentication retries follow the parent protocol and must be explicitly recorded. No new tasks or stochastic repeats are added.

The E007 run order is frozen in the manifest: for each canonical case in preserved order, using a frozen three-order rotation (Medium/High/Max; High/Max/Medium; Max/Medium/High) to balance within-case condition position. This blocks by case while keeping the historical case order.

## Execution and billing

Use the existing local Docker Linux/arm64 isolated-run architecture and the immutable, case-appropriate runtime inherited from the source experiments. Capture the selected model in both invocation metadata and Devin session export. The inspected Devin model catalog showed each SWE-2 variant as Free; no direct model overage is expected from model use. Still record account-reported usage and cost when exposed. Stop before any unexpected direct overage; the direct overage ceiling is $100.

## Analysis

Compare Medium and Max case by case to the original binary outcomes, reporting aggregate and exact agreement separately. Analyze all three conditions as paired data: overall, by difficulty, and each pairwise effort contrast. Report Cochran's Q, exact two-sided McNemar tests, absolute rate differences, and small-sample confidence intervals; interpret small tier samples cautiously. Efficiency summaries include all attempted runs and successful runs only, with unavailable costs labeled unavailable rather than imputed. Failure explanations require trace evidence and distinguish observation, plausible interpretation, and unresolved cause.

## Deviations and exclusions

Any intervention-contaminated run is excluded from primary analysis and documented. Infrastructure errors remain visible in run records and are not silently replaced. The frozen case list and scoring are immutable. Report deviations before conclusions.
