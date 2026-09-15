# Experiment 002 Protocol

Status: infrastructure validated and frozen, benchmark not started.

## Purpose

Experiment 002 repeats the same five-case, two-condition BugsInPy capability
experiment after correcting the E001 execution-permission failure. It asks
whether Devin can diagnose and repair the same real bugs when required tools
are available autonomously inside a disposable isolated environment.

E001 remains immutable at commit `223928abc57ba9b1c9fe3e2a206bae8796c2df04`.
E001 is retained as provenance but is unsuitable as a capability comparison:
all ten E001 runs used `accept-edits` in noninteractive mode, encountered
required shell-tool rejection, and produced empty patches.

## Frozen invariants

E002 retains, byte-for-byte:

- the five cases: Black 16, FastAPI 3, Scrapy 3, tqdm 5, and Tornado 13;
- the E001 task prompts;
- the E001 held-out tests and regression suites;
- SWE-2 Medium (`swe-2-medium`) and SWE-2 Max (`swe-2-max`);
- the TASK_SUCCESS definition;
- Fusion exclusion;
- zero substantive human or Codex assistance;
- one fresh case environment per run;
- no retries for ordinary agent failures.

The only experimental infrastructure changes are the corrected autonomous
permission configuration and the disposable container boundary.

## Frozen execution environment

Each run uses a fresh `linux/arm64` Docker container built from
`isolation/experiment-002/Dockerfile` at Devin CLI version 3000.10.21.
The container runs the CLI with:

```text
--permission-mode dangerous
```

The effective Devin mode is Bypass. The container receives only:

1. the sanitized buggy workspace, read-write;
2. a fresh artifact directory, read-write; and
3. a read-only mount of the Devin `credentials.toml` file.

The container does not receive `/Volumes/Research`, the control repository,
the host home directory, SSH keys, GitHub credentials, Obsidian, Supabase
credentials, or the Docker socket. It is non-privileged, drops all Linux
capabilities, enables `no-new-privileges`, uses a read-only root filesystem,
and uses ephemeral tmpfs paths for CLI state and caches.

The agent network is an internal Docker network. An egress proxy permits only
`api.devin.ai`, `app.devin.ai`, and `server.codeium.com`. Case dependencies
are provisioned before the agent session; package installation is not part of
the agent network path.

## Frozen run order

The new balanced interleaved order is recorded in
`manifests/experiment-002-runs.json`, generated with seed `20260915`:

| # | Run | Condition | Model |
|---:|---|---|---|
| 1 | E002-C02-M | M | swe-2-medium |
| 2 | E002-C04-X | X | swe-2-max |
| 3 | E002-C01-M | M | swe-2-medium |
| 4 | E002-C05-X | X | swe-2-max |
| 5 | E002-C03-M | M | swe-2-medium |
| 6 | E002-C01-X | X | swe-2-max |
| 7 | E002-C04-M | M | swe-2-medium |
| 8 | E002-C02-X | X | swe-2-max |
| 9 | E002-C05-M | M | swe-2-medium |
| 10 | E002-C03-X | X | swe-2-max |

## Per-run procedure

1. Regenerate a fresh sanitized workspace from the frozen buggy source.
2. Provision only the case dependencies into the disposable environment.
3. Verify the leak audit, prompt hash, model, run ID, and evaluator readiness.
4. Start a new container with the frozen network and mount policy.
5. Invoke Devin noninteractively with the frozen prompt and `dangerous` mode.
6. Provide no substantive assistance and do not retry ordinary task failures.
7. Capture stdout, stderr, session export, wall time, and filesystem patch.
8. Destroy the container before evaluator-side access.
9. Run the existing held-out evaluator and regression suite outside the agent
   environment.
10. Record TASK_SUCCESS, evaluator status, regressions, patch metadata,
    termination reason, and available usage data.

Any authentication, service, billing, container, workspace, or evaluator
failure is an infrastructure stop condition. A dependency failure or bad fix
inside the supplied OSS repository is an agent result.

## Launch gate

The synthetic validation record in
`docs/experiment-002-synthetic-validation.md` demonstrates the container
boundary, allowlisted egress, autonomous tool use, public and held-out
success, non-empty patch, and clean reset. This clears the infrastructure gate
for a future separately approved E002 launch; no E002 case has been started by
this protocol commit.
