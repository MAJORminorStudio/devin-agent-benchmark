# FastAPI 3

FastAPI response-model serialization mishandles nested response content when
unset fields and model aliases are involved. Reproduce the failing
serialization tests, trace the behavior through response validation/encoding,
implement a focused fix, and run the relevant tests without changing
unrelated API behavior.
