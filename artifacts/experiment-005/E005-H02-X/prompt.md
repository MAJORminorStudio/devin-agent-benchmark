Cancelling a running job releases its worker slot, but the job record can remain
in a non-terminal state. This makes cancellation indistinguishable from a job
that is still running and makes later scheduling behavior difficult to reason
about. Repair the lifecycle handling so cancellation is recorded consistently,
queued work still behaves normally, and ordinary success and failure semantics
remain unchanged.

Run the available test suite with:

    PYTHONPATH=src python -m unittest discover -s tests -v
