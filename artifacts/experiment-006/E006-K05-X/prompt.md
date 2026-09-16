tqdm's display trimming must account for ANSI control sequences without
appending a duplicate reset when the existing reset remains in the result.
Reproduce the failing display test, diagnose the trimming state, implement a
focused repair, and run the relevant tests. Preserve ordinary plain-text
trimming.
