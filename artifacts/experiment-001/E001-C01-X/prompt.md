# Black 16

Black's directory processing behaves incorrectly when a directory contains a
symbolic link that resolves outside the directory being processed. Reproduce
the failure with the provided regression test, diagnose the cause, implement a
focused fix, and run the relevant tests. Keep the change limited to the bug
and avoid unrelated formatting or refactoring.
