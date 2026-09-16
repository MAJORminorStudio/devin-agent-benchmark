# Prompts

The standardized task prompt is stored with each evaluator case in `manifests/experiment-001.json` for Phase 1. Before a Devin run, export only the selected case's `task_prompt` and the contents of its `agent-workspace/`.

Do not provide the evaluator manifest, fixed checkout, BugsInPy `bug.info`, `bug_patch.txt`, `bug_fixed.txt`, or reproduction logs from the fixed side.

Experiment 006 prompts are under `prompts/experiment-006/`. They are frozen
public task inputs; private E006 evaluators, fixed trees, and reference patches
remain outside the repository.
