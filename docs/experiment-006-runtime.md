# Experiment 006 Repaired Runtime

The original frozen image failed the dependency gate before execution: it
provided only Python 3.11.2 and lacked the historical interpreters, `python`
command, pytest, and project dependencies required by E006. The repaired
runtime is an immutable derived image; the original image is not modified.

Image identity:

- base: `devin-e002:3000.10.21@sha256:bb045374bc655c185cced99a6cb769a6695c88527fb432456eb8e0d6dd0e4bb6`;
- derived: `devin-e006:3000.10.21-r7@sha256:7557a0bc640492d8f77f271ebafc6402733fa0ba843c344f74ab613b94416699`;
- platform: Linux/arm64;
- Devin CLI: `3000.10.21 (611c1cba)`;
- build definition: `isolation/experiment-006/Dockerfile`;
- dependency lock: `isolation/experiment-006/runtime-lock.json`;
- build timestamp: `2026-09-16T14:45:19Z`.

## Case mapping

| Cases | Python | Virtualenv | Main dependencies |
|---|---:|---|---|
| H01-H05 | 3.8.3 | `py383-h` | pytest 3.10.1 and control-side test support |
| K01 black-6 | 3.8.3 | `py383-k01` | appdirs 1.4.3, attrs 19.3.0, click 7.0, toml 0.10.0, typed-ast 1.4.0, pytest 3.10.1 |
| K02 PySnooper-1 | 3.8.1 | `py381-k02` | python-toolbox 1.3.2, pytest 3.10.1, attrs 25.3.0 |
| K03 black-23 | 3.8.3 | `py383-k03` | attrs 17.4.0, click 6.7, pytest 3.10.1 |
| K04 thefuck-17 | 3.7.0 | `py370-k04` | pytest 3.10.1 plus the pinned shell/project dependencies |
| K05 tqdm-2 | 3.6.9 | `py369-k05` | pytest 5.4.3 plus the pinned tqdm dependencies |

H01-H05 use the standard library for project code. The environment also
contains the control-side pytest layer so the same evaluator runner can be
used for every case. The runner supplies each case environment's virtualenv
bin directory on `PATH` and the corresponding runtime library directory through
`LD_LIBRARY_PATH`; no prompt or task command was changed. The old
`libffi.so.6` ABI is included for completeness of the copied legacy Python
standard libraries.

## Validation

`scripts/validate_experiment_006_runtime.py` ran each buggy and fixed tree in
a fresh read-only-root Linux/arm64 container, with a fresh workspace and
fresh evaluator copy, twice. All fixed public/held-out/regression groups
passed. All buggy public and held-out groups failed as expected; regression
matched the prior ground truth, including the known H01 buggy regression
exception. The 40-container signatures matched the pre-freeze ground truth.
The evaluator was control-side only and was never mounted in an agent
session. Runtime dependencies are preinstalled; the experimental run path
does not need package downloads.
