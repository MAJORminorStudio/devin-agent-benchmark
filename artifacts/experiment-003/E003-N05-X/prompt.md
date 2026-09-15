You are working in this repository.

A user reports that the line-oriented transaction parser can become incorrect when a new transaction begins before the previous one is complete. The parser should recover to the newest valid transaction, tolerate fragmented input, and preserve normal record emission. Reproduce the issue with the existing test suite, investigate the implementation, and make the smallest maintainable fix. Run the relevant public test before and after your change.

Do not change the public API or add dependencies.
