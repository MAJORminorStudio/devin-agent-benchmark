PySnooper's source inspection must preserve non-ASCII Python source when a
file has no coding cookie, while still honoring an explicitly declared
encoding. Reproduce the failing source-inspection test, diagnose the decoding
path, implement a focused repair, and run the relevant tests. Preserve
ordinary tracing behavior.
