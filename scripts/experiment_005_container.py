#!/usr/bin/env python3
"""Plan or execute one frozen Experiment 005 container run.

Execution is deliberately opt-in and requires both --execute and
--confirm-paid. The freeze work uses this module only for dry-run planning.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NoReturn


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "manifests" / "experiment-005-config.json"
RUNS_PATH = REPO_ROOT / "manifests" / "experiment-005-runs.json"


def die(message: str) -> NoReturn:
    raise SystemExit(f"error: {message}")


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        die(f"could not read {path}: {exc}")
    if not isinstance(value, dict):
        die(f"expected JSON object in {path}")
    return value


def load_run(run_id: str) -> dict[str, Any]:
    matches = [run for run in read_json(RUNS_PATH).get("runs", []) if run.get("run_id") == run_id]
    if len(matches) != 1:
        die(f"run ID is absent or duplicated: {run_id}")
    return matches[0]


def outside_control(candidate: Path) -> bool:
    try:
        candidate.relative_to(REPO_ROOT)
        return False
    except ValueError:
        return True


def validate_paths(workspace: Path, output: Path, credential: Path | None, executing: bool) -> None:
    if not workspace.is_dir() or not (workspace / "TASK.md").is_file():
        die("workspace must be a directory containing TASK.md")
    if not outside_control(workspace):
        die("workspace must be outside the control repository")
    if not outside_control(output):
        die("output must be outside the control repository")
    if output == workspace or workspace in output.parents:
        die("output must not be inside the workspace")
    if output.exists() and any(output.iterdir()):
        die("output directory must be fresh and empty")
    if executing:
        if credential is None or not credential.is_file() or credential.name != "credentials.toml":
            die("execution requires an existing credentials.toml file")
        if credential == workspace or workspace in credential.parents:
            die("credential must be outside the workspace")


def docker_command(
    config: dict[str, Any], run: dict[str, Any], workspace: Path, output: Path, credential: Path
) -> list[str]:
    return [
        "docker", "run", "--rm", "--init", "--platform", "linux/arm64", "--read-only",
        "--cap-drop", "ALL", "--security-opt", "no-new-privileges:true", "--pids-limit",
        str(config["limits"]["pids_limit"]), "--memory", config["limits"]["memory"], "--cpus",
        str(config["limits"]["cpus"]), "--workdir", "/workspace", "--network", config["agent_network"],
        "--mount", f"type=bind,src={workspace},dst=/workspace", "--mount",
        f"type=bind,src={output},dst=/artifacts", "--mount",
        f"type=bind,src={credential},dst=/run/devin-data/devin/credentials.toml,ro",
        "--tmpfs", "/run:rw,noexec,nosuid,size=512m", "--tmpfs", "/tmp:rw,noexec,nosuid,size=1g",
        "--env", "HOME=/root", "--env", "XDG_CONFIG_HOME=/run/devin-config",
        "--env", "XDG_DATA_HOME=/run/devin-data", "--env", f"HTTPS_PROXY={config['proxy_url']}",
        "--env", f"HTTP_PROXY={config['proxy_url']}", "--env", "NO_PROXY=localhost,127.0.0.1",
        config["container_image"], "--model", run["model"], "--print", "--prompt-file", "/workspace/TASK.md",
        "--export", "/artifacts/devin-session-export.json", "--permission-mode", "dangerous",
        "--respect-workspace-trust", "false",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--credential-file", type=Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm-paid", action="store_true")
    args = parser.parse_args()
    if args.confirm_paid and not args.execute:
        die("--confirm-paid requires --execute")
    if args.execute and not args.confirm_paid:
        die("refusing agent invocation without --confirm-paid")
    config = read_json(CONFIG_PATH)
    run = load_run(args.run_id)
    if config.get("status") != "frozen-ready-for-launch":
        die("Experiment 005 configuration is not frozen-ready-for-launch")
    workspace = args.workspace.expanduser().resolve()
    output = args.output_dir.expanduser().resolve()
    credential = args.credential_file.expanduser().resolve() if args.credential_file else None
    validate_paths(workspace, output, credential, args.execute)
    plan_credential = credential or Path("<credential-file>")
    cmd = docker_command(config, run, workspace, output, plan_credential)
    plan = {
        "experiment_id": "experiment-005", "run_id": args.run_id, "case_id": run["case_id"],
        "model": run["model"], "workspace": str(workspace), "output_dir": str(output),
        "command": cmd, "command_display": " ".join(shlex.quote(part) for part in cmd),
        "permission_mode": "dangerous", "effective_permission_mode": "Bypass",
        "fusion": "disabled", "devin_invoked": False,
    }
    output.mkdir(parents=True, exist_ok=True)
    if not args.execute:
        (output / "dry-run-plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(plan, indent=2))
        return 0
    started = datetime.now(timezone.utc)
    monotonic = time.monotonic()
    timed_out = False
    try:
        completed = subprocess.run(
            cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            timeout=config["limits"]["maximum_wall_time_seconds"],
        )
        returncode = completed.returncode
        stdout, stderr = completed.stdout or "", completed.stderr or ""
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = 124
        stdout, stderr = exc.stdout or "", exc.stderr or ""
    ended = datetime.now(timezone.utc)
    result = {
        **plan, "devin_invoked": True, "returncode": returncode, "timed_out": timed_out,
        "started_at_utc": started.isoformat(), "ended_at_utc": ended.isoformat(),
        "wall_time_seconds": time.monotonic() - monotonic,
    }
    (output / "devin.stdout.txt").write_text(stdout, encoding="utf-8")
    (output / "devin.stderr.txt").write_text(stderr, encoding="utf-8")
    (output / "container-run-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0 if returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
