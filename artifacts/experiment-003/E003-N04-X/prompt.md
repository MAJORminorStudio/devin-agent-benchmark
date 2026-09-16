You are working in this repository.

A user reports that closing a running session can return before the background worker has completed its cleanup. Callers need close to be awaitable, safe to call more than once, and complete only after the worker is no longer active. Reproduce the issue with the existing test suite, investigate the implementation, and make the smallest maintainable fix. Run the relevant public test before and after your change.

Do not change the public API or add dependencies.
