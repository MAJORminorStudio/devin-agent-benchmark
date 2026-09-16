# Tornado 13

Tornado's HTTP/1.x connection handling makes an incorrect keep-alive decision
for a response without an explicit content length. Reproduce the failure with
the provided HTTP connection test, diagnose the protocol-state handling,
implement a focused fix, and run the relevant tests.
