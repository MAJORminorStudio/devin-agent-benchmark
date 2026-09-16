The stream session reports malformed input, but later valid commands can be
lost or blocked by backpressure. Restore reliable recovery for fragmented
and coalesced input while preserving frame order, flow-control accounting,
command behavior, and session close semantics.

Run the available test suite with:

    PYTHONPATH=src python -m unittest discover -s tests -v
