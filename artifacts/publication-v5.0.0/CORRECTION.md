# Correction note: E007 evaluator staging

E007 originally recorded 90 agent sessions with evaluator totals of Medium 16/30, High 18/30, and Max 18/30. During E008's comparison of original and E007 case outcomes, very-hard failures were inspected and pytest collection errors were traced to stale Python `.pyc` cache artifacts. The compiled cache data embedded a source evaluator host path that was invalid in the staged evaluator location. Those collection errors had initially been scored as task failures.

The team copied the frozen evaluator directories, removed generated cache files from the copies, and re-ran the evaluators against the preserved E007 very-hard workspaces. No agent was rerun, no workspace changes were made, and the frozen tests and scoring contract were retained. Clean re-evaluation of the preserved E007 workspaces corrected 18 of the 90 recorded outcomes, six at each effort level, without rerunning Devin. The clean recheck totals are Medium 22/30, High 24/30, and Max 24/30.

The original historical E007 ledger and its 16/30, 18/30, 18/30 totals remain available and unchanged. The 22/30, 24/30, 24/30 values are explicitly labeled as E008 clean rechecks of E007 workspaces; they are not new agent runs and do not overwrite the original record. E007's 90 sessions plus E008's 33 targeted sessions constitute 123 new agent sessions; clean rechecks are evaluations, not additional sessions.

The defect was discovered after E007, as part of E008. It is documented here as a correction to evaluator results, not as evidence that the underlying historical record never existed.
