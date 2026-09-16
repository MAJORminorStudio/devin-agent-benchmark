The runtime can return the artifact for one profile mode when the same profile
is loaded in another mode. Profile updates can also leave an old artifact in
use. Preserve deterministic serialization and normalization while ensuring
mode-specific artifacts and source revisions do not cross-contaminate.

Run the available test suite with:

    PYTHONPATH=src python -m unittest discover -s tests -v
