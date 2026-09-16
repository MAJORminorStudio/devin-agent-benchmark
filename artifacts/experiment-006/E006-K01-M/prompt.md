Black's parser must respect the selected Python target when `async` and
`await` are identifiers in legacy code. Reproduce the failing parser test,
trace the target-version handling, implement a focused repair, and run the
relevant tests. Preserve ordinary formatting behavior and keep the change
limited to this compatibility issue.
