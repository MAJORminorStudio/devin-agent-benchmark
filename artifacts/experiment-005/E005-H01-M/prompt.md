The plan builder can return stale content after a definition used indirectly by
a published plan changes. A direct consumer may appear correct while a deeper
consumer continues to publish the old result. Make the implementation preserve
the existing reuse behavior while ensuring published plans always reflect the
current definitions in their dependency chain.

Run the available test suite with:

    PYTHONPATH=src python -m unittest discover -s tests -v

Keep the public API and the existing behavior for unrelated definitions,
invalid definitions, and dependency errors intact.
