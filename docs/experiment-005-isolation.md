# Experiment 005 Isolation

E005 reuses the already frozen E002/E003 isolated execution architecture by
reference only; it does not modify, start, stop, or reconfigure shared Docker
infrastructure, proxy settings, credentials, or network state.

Each future run must use one fresh `linux/arm64` disposable container with the
same effective Bypass permission mode, read-only root filesystem, all Linux
capabilities dropped, `no-new-privileges`, no Docker socket, no host or control
repository mounts, and one read-write sanitized buggy workspace. Only the
minimum Devin credential file may be mounted read-only. Dependency setup occurs
before the agent session; the agent has no package-installation path.

The agent network remains the existing restricted Devin-service proxy path. No
case evaluator, fixed source, reference patch, prior-run artifact, control
repository information, or E004 material may be mounted. The evaluator runs
outside the container only after the session and container are closed.

Any host mount, credential exposure, proxy change, evaluator visibility, or
fresh-workspace violation is an infrastructure stop condition, not an agent
result.
