# Results

Future agent-run records belong here. Keep raw Devin artifacts, patches, and
usage metadata separate from ground-truth manifests and fixed verification
trees. Runtime outputs are ignored by default. The runner captures raw
stdout/stderr and the CLI export; the evaluator writes a separate structured
result and never sends evaluator findings back to Devin. After both conditions
for a case are closed, run `scripts/analyze_results.py` to produce the paired
case table, Medium/Max solved counts, and efficiency summaries. It makes no
statistical-significance claims for n=5.
