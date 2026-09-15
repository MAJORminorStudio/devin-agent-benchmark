# Experiment 002 Isolation Design

## Docker versus VM

The installed host CLI is a macOS arm64 Mach-O binary and cannot run inside a
Linux container. Docker Desktop is installed and its LinuxKit VM runs arm64
Linux containers successfully. The official pinned Devin installer exposes an
`aarch64-unknown-linux` target, so a Linux CLI can be installed in the image.
The E002 image and proxy are referenced by the locally built immutable image
digests recorded in `manifests/experiment-002-config.json`.
No separate lightweight Linux VM tool is installed or required: Docker
Desktop already supplies the required Linux VM boundary.

The native CLI's own macOS `--sandbox` mode was not selected for E002 because
it selects Autonomous mode, where direct `edit`/`write` calls still prompt.
E002 requires `dangerous`/Bypass to eliminate the E001 failure, so it runs the
Linux CLI inside the Docker boundary instead.

## Authentication

`devin auth status` and the installed CLI documentation identify the Devin
credential store as:

```text
~/.local/share/devin/credentials.toml
```

The host credential file is mounted read-only at the same path inside the
container. No credential values are copied into the repository, image,
prompt, logs, or command line. No GitHub authentication is required for a
local workspace session with no remote operations. The runner does not mount
SSH configuration, GitHub configuration, cloud credentials, or the host home
directory.

## Filesystem boundary

The agent sees a container filesystem containing the CLI and runtime plus one
sanitized workspace. It receives no mount under `/Volumes/Research`. Output
artifacts are mounted separately and are not available as prior-run state.
The root filesystem, CLI state, and caches are ephemeral; each run uses
`--rm` and fresh tmpfs mounts. The Docker socket is not mounted, and the
container is not privileged.

## Network boundary

The agent is placed on an internal Docker network with no direct external
route. A separate proxy container has one internal interface and one external
Docker interface. It accepts CONNECT only for:

- `server.codeium.com`
- `api.devin.ai`
- `app.devin.ai`

The agent receives only `HTTP_PROXY`/`HTTPS_PROXY` pointing to that proxy.
Dependency installation occurs during environment preparation rather than in
the agent session, so PyPI and GitHub are not in the runtime allowlist.

The proxy is intentionally small and deny-by-default. Its allowlist should be
updated only from observed Devin service requirements and then re-frozen before
E002.

## Remaining security assumption

Docker Desktop is a meaningful boundary from the Mac host, but `dangerous`
remains unrestricted inside the container. A Docker Desktop or kernel escape
would be an infrastructure security failure, not an agent result. The
container must therefore remain disposable, unprivileged, unmounted from the
control repository, and free of unrelated credentials.

## Validation status

The disposable synthetic validation completed before any E002 case was run.
It used the pinned Linux image, the internal agent network, and the
allowlisted proxy. See `docs/experiment-002-synthetic-validation.md` for the
recorded evidence and the one pre-session Docker mount syntax correction.
