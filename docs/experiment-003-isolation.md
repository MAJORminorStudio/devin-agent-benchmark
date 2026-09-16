# Experiment 003 Isolation

E003 uses the corrected E002 execution boundary without changing the agent
conditions. Each run uses a fresh disposable Linux/arm64 Docker container,
read-only root filesystem, all Linux capabilities dropped,
`no-new-privileges`, no Docker socket, no host home or control-repository
mount, one sanitized buggy workspace, and a fresh artifact directory. Only
the minimum Devin credential file is mounted read-only.

The agent uses dangerous permission mode, whose effective mode is Bypass, only
inside the disposable container. This is required because E001's
noninteractive permission gating rejected required tool calls. The container
has no evaluator files, reference material, prior-run artifacts, or control
repository history.

The agent network is the E002 internal network with the deny-by-default proxy
allowlist for Devin service endpoints. Dependencies for these compact cases
are standard-library-only and are prepared before a session; the agent does
not need package installation or general internet access.

Before each future run the harness must verify the fresh workspace, passing
leak audit, prompt hash, model assignment, container settings, and evaluator
readiness. After Devin exits, the session is closed, artifacts are captured,
the disposable environment is destroyed, and only then are evaluator tests
run. Any authentication, service, container, workspace, or evaluator
infrastructure failure stops the experiment under the existing policy.
