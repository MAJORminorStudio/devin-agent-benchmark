# E008 Re-evaluation of Existing E007 Very-Hard Workspaces

E007’s saved E006 evaluator outputs for some Medium/High/Max workspaces report pytest collection errors: `import file mismatch` because pre-existing `.pyc` files embed the original host evaluator path while the frozen suite is mounted at `/control/evaluation`. This is an evaluator staging/cache error, not a task failure. We made a clean temporary copy of each frozen E006 evaluator directory, removed only generated `__pycache__`, `.pyc`, and pytest cache entries from that copy, and re-ran the frozen public, held-out, and regression commands against the preserved E007 workspaces using the same pinned E006 runtime. No Devin session was launched and E007’s original records were not modified.

| E007 effort | Rechecked very-hard cases | Valid evaluator runs | Very-hard pass | Very-hard fail | Recorded E007 total | Clean-recheck E007 total |
| --- | --- | --- | --- | --- | --- | --- |
| Medium | 10 | 10 | 8 | 2 | 16/30 | 22/30 |
| High | 10 | 10 | 8 | 2 | 18/30 | 24/30 |
| Max | 10 | 10 | 8 | 2 | 18/30 | 24/30 |

The 30 clean adjudications are preserved in `E008-E007-EVALUATOR-RECHECK.jsonl`. The historical E007 totals (16/30, 18/30, 18/30) remain its recorded scores. Clean-recheck totals (22/30, 24/30, 24/30) are an E008 sensitivity analysis, not a rewrite of E007. Six failed-to-pass E007 E006 cells changed for each effort; other outcomes were unchanged.
