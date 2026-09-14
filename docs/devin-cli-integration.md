# Devin CLI integration findings

Inspection date: 2026-09-14. All commands below were read-only help, model
listing, authentication/status, or empty session-list checks. No Devin session
was started.

## Installed CLI

```text
devin 3000.10.21 (611c1cba)
```

The root help exposes these relevant options:

- `--model <MODEL>` — select a model or alias.
- `-p, --print [<PROMPT>]` — non-interactive mode that processes the prompt and exits.
- `--prompt-file <FILE>` — load the initial prompt from a file.
- `--export [<PATH>]` — export the conversation after each turn.
- `--permission-mode <PERMISSION_MODE>` — `auto`, `accept-edits`, `smart`, or `dangerous`.
- `--respect-workspace-trust <true|false>` — useful for non-interactive prepared workspaces.
- a positional `[PATH]...` — workspace path.

The installed account lists these exact SWE-2 model IDs:

```text
swe-2-high
swe-2-medium
swe-2-max
```

It also lists separate `fusion-*` model IDs, plus a `fusion` family. The frozen
Experiment 001 configuration selects `swe-2-medium` and rejects any model ID
beginning with `fusion-`. This is the only Fusion control exposed by the
installed CLI; there is no separate `--fusion off` option in help.

## Supported runner path

The supported non-interactive local invocation is equivalent to:

```sh
devin \
  --model swe-2-medium \
  --print \
  --prompt-file TASK.md \
  --export session-export.json \
  --permission-mode accept-edits \
  --respect-workspace-trust false \
  /path/to/sanitized/workspace
```

The Phase 2 runner constructs this with an argument array and never uses shell
evaluation. It defaults to a dry run and requires an explicit paid-invocation
confirmation before execution.

`devin list --format json` is supported and can be captured before and after an
invocation. `--export` captures the conversation. The CLI help does not promise
a stable session ID or URL on stdout, so the runner records raw command output,
the export file, and before/after JSON session inventories. A session ID/URL is
reported only when the installed CLI actually emits it or the JSON inventory
contains it; the runner does not invent one.

## Cloud and GitHub limits

`devin cloud` exposes only Declarative Repo Setup commands in this installation:
`sandbox-create`, `run`, blueprint management, and build operations. The DRS
sandbox command creates a cloud sandbox and was not called. No general cloud
agent-session create or handoff command was exposed by help, so Experiment 001
uses local mode with a deterministic sanitized checkout. The runner treats
cloud handoff as a human checkpoint rather than scripting undocumented commands.

The CLI has no documented GitHub repository/branch option. Deterministic source
selection is therefore performed before invocation: the exporter creates a
sanitized case checkout/branch, and the local path passed to Devin is that exact
checkout. GitHub PR creation is not exposed by the inspected CLI help; PR URL
capture remains optional and manual unless the session itself produces a URL.

## Usage and cost

The inspected CLI exposes no usage, cost, or ACU reporting flag. The runner
records elapsed wall-clock time and leaves usage/cost/ACU fields nullable. Any
account-side usage must be copied into the result after the session by an
operator without sending it back to Devin.

## Human checkpoints

The following remain explicit checkpoints:

1. Review the sanitized case audit.
2. Confirm the exact `swe-2-medium` invocation and the zero-intervention policy.
3. Approve any paid invocation; Phase 2 dry runs stop before this point.
4. If a cloud session or PR is desired, create/verify it through a documented
   product path and record the resulting ID/URL manually.
5. Do not send evaluator findings, hidden-test results, or reference comparisons
   back to Devin during Experiment 001.
