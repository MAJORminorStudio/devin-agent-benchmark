# Experiment 006 Isolation and Security Preflight

The E006 launch contract inherits the validated E002 Docker topology and is
encoded in `manifests/experiment-006-config.json` and the dry-run planner.
Each future run must use a fresh workspace and fresh artifact directory. The
evaluator is outside the container and is not mounted until the agent session
has closed. The prelaunch dependency gate for the original image failed
because it exposed only Python 3.11.2, with no `python` command, pytest, or
historical project dependencies. This was repaired before execution by the
immutable derived image described in `docs/experiment-006-runtime.md`.

## Static contract

- image is pinned by digest and platform is Linux/arm64; the exact original
  Devin image remains the derived image's base;
- root filesystem is read-only, all capabilities are dropped, and
  `no-new-privileges` is enabled;
- limits are four CPUs, 4 GiB memory, and 512 PIDs;
- the only writable mounts are the single sanitized workspace and fresh
  artifacts directory; the credential file is read-only;
- there is no host home, control repository, Docker socket, paired case, fixed
  tree, held-out evaluator, or prior result mount;
- network is the internal `e002-internal` path through the restricted
  `egress-proxy:3128`, with no direct internet access;
- dependency installation is disabled during the agent session; all required
  runtimes and packages are already present in the immutable image;
- case selection is mechanical: the frozen runner supplies the case-specific
  virtualenv on `PATH` and its runtime library directory through
  `LD_LIBRARY_PATH`;
- Python 3.8.3, 3.8.1, 3.7.0, and 3.6.9 are pinned for the cases that require
  them, with legacy `libffi.so.6` included for standard-library completeness.

The private preflight inspected the selected image's digest and architecture,
validated the security/resource/mount command shape, checked the fresh
workspace rules, and confirmed that no agent executable was called. The
control-side runtime validator additionally ran every buggy/fixed public,
held-out, and regression check twice in fresh containers; it mounted private
evaluators only for that control-side check, never in an agent session. The
planner's default path emits a JSON command plan only.

## Operational gate

The bare image inspection is intentionally not treated as a task run. The
repaired image's preinstalled dependency layer and all case mappings were
confirmed by the runtime validator. If that dependency-layer confirmation is
ever unavailable for a future image, E006 must remain unlaunched even though
its static isolation checks are green.

The paid guard requires both `--execute` and `--confirm-paid`; neither flag
was passed during this freeze. Any unexpected credential, proxy, Docker, or
mount behavior is an infrastructure stop and requires a new review before
resuming.
