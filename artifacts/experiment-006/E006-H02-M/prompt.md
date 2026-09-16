A retrying asynchronous job can lose ownership of its current worker handle.
When cancellation arrives during a later attempt, the job may continue or
its capacity may be accounted against the wrong attempt. Repair the lifecycle
so ownership, cancellation, retry state, and terminal records remain
consistent. Ordinary success, permanent failure, and queued work must
continue to behave normally.

Run the available test suite with:

    PYTHONPATH=src python -m unittest discover -s tests -v
