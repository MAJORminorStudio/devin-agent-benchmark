An account change publishes an event while its transaction is being applied.
Listeners can initiate related changes, close themselves, or register a
replacement. Repair the update and dispatch lifecycle so reentrant operations
observe committed state, the current dispatch has stable membership, and
once-only listeners remain once-only. Preserve ordinary balance behavior.

Run the available test suite with:

    PYTHONPATH=src python -m unittest discover -s tests -v
