The derived counter can receive the same event more than once after its
consumer is started repeatedly. During dispatch, subscribers may also close
themselves or add a replacement, and the current event should still be
delivered according to the subscription lifecycle contract. Repair the
subscription and dispatch behavior while preserving once-only listeners,
stop/restart behavior, and unrelated topics.

Run the available test suite with:

    PYTHONPATH=src python -m unittest discover -s tests -v
