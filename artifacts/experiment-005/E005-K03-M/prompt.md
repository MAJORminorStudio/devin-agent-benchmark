Repeated creation and closure of asyncio-backed event loops leaves stale
Tornado loop wrappers reachable. Restore correct wrapper lifecycle cleanup
while preserving normal IOLoop operation.

Run the relevant tests, make the smallest complete source change, and leave the
working tree with the fix applied.
