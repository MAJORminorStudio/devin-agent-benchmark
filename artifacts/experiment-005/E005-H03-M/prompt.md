The stream handler reports a malformed frame, but a valid command arriving
after that frame can be lost or treated as unusable. The problem is visible
with both coalesced input and input split across reads. Restore reliable
protocol recovery without changing normal fragmented-frame handling, command
ordering, or the session close behavior.

Run the available test suite with:

    PYTHONPATH=src python -m unittest discover -s tests -v
