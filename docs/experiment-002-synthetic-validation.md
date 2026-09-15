# Experiment 002 Synthetic Validation

Date: 2026-09-15

This validation is disposable infrastructure testing only. It is not an
E001 or E002 benchmark case, and no BugsInPy workspace, prompt, evaluator, or
result was used.

## Synthetic task

A fresh toy Git repository contained a deliberately broken `format_total`
function, one public test, and a task prompt requiring repository exploration,
multiple shell/test commands, a source edit, and a post-edit test run. The two
held-out assertions were kept in a separate evaluator directory and were not
mounted into the Devin container.

The baseline behaved as expected:

- public test: failed because thousands grouping was absent;
- held-out evaluator: one target assertion failed and the independent zero
  edge case passed.

## Successful isolated run

The run used:

- Linux/arm64 CLI image `devin-e002:3000.10.21` containing the pinned
  `3000.10.21` bundle;
- model: `swe-2-medium`;
- CLI permission mode: `dangerous` (effective mode: `Bypass`);
- internal agent network: `e002-internal-validation`;
- proxy: `http://egress-proxy:3128`;
- one read-write synthetic workspace, one fresh artifact directory, and one
  read-only Devin `credentials.toml` mount;
- read-only image, all capabilities dropped, `no-new-privileges`, no
  privileged mode, no Docker socket, and ephemeral `/run` and `/tmp`.

The Devin session completed with return code 0 in approximately 128.175
seconds. Its export recorded session ID `daffy-abrosaurus` and 14 total
steps. The export contained eight tool calls across six tool-call-bearing
steps: repository exploration, three reads, three shell/test command
invocations, and an edit. There were no rejected or canceled tool calls.

The resulting patch was non-empty and changed only the synthetic source
function. The public test passed after the edit, and the evaluator-side
held-out suite passed independently after the Devin container had closed.

After this successful session, the same image definition was rebuilt with
immutable arm64 base-image digests and the resulting Devin image digest was
recorded in `manifests/experiment-002-config.json`. No second synthetic Devin
session was run.

## Boundary evidence

Validation tooling, not Devin, checked the container boundary. It confirmed
that `/Volumes/Research`, `/Users/dippo`, host SSH/GitHub/cloud credential
locations, `/var/run/docker.sock`, and inherited credential environment
variables were absent. The intended credential mount existed only at the
container path required by the CLI.

The agent network has no direct external route. A direct request with proxy
variables cleared failed, and a request through the proxy to an unallowlisted
HTTPS host received the expected deny response. The successful Devin session
demonstrated that the allowlisted service path was sufficient for the CLI.

After the run, the `--rm` container was gone. A fresh container with no
workspace or credential mounts confirmed that synthetic files, CLI state,
credentials, and the Docker socket did not persist into the next container.

## Pre-session harness correction

The first synthetic invocation did not create a Devin session. Docker rejected
the harness command because read-write bind mounts were expressed with an
invalid `rw` field in `--mount`. The corrected runners omit that field (read-
write is the Docker default); the credential mount continues to be
read-only. This was caught before any Devin task began and is recorded as an
infrastructure compatibility correction, not an agent result or protocol
change.

## Gate outcome

The proposed isolated environment satisfies the Phase 2 synthetic gate. E002
remains unstarted and requires its separate human launch approval.
