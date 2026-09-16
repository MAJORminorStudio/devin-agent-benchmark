A WebSocket close path retains a request-handler cycle after the connection is
finished. Restore close lifecycle cleanup without changing ordinary request
handling.

Run the relevant tests, make the smallest complete source change, and leave the
working tree with the fix applied.
