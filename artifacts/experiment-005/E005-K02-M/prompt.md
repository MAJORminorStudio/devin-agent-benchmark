The local scheduler does not consistently enable the lifecycle cleanup needed
when external dependencies are retried. Restore the scheduler behavior so
external work can be reconsidered as it progresses, without breaking ordinary
dependency scheduling.

Run the relevant tests, make the smallest complete source change, and leave the
working tree with the fix applied.
