The plan publisher can return stale content after a definition used
indirectly by a published plan changes. A direct consumer may appear correct
while a deeper consumer continues to publish the old result. Preserve the
existing reuse behavior while ensuring published plans reflect current
definitions in their dependency chain.

Run the available test suite with:

    PYTHONPATH=src python -m unittest discover -s tests -v

Keep the public API and existing behavior for unrelated definitions, invalid
definitions, and dependency errors intact.
