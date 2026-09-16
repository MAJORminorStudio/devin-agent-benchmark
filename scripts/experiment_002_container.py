#!/usr/bin/env python3
"""Plan or execute one E002 run in a disposable Docker container.

The default operation is a dry-run. Real execution requires both --execute
and --confirm-paid. This runner is separate from the immutable E001 runner.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "manifests" / "experiment-002-config.json"
RUNS_PATH = REPO_ROOT / "manifests" / "experiment-002-runs.json"
DEFAULT_IMAGE = "devin-e002:3000.10.21@sha256:bb045374bc655c185cced99a6cb769a6695c88527fb432456eb8e0d6dd0e4bb6"


def die(message: str) -> None:
    raise SystemExit(f"error: {message}")


def read_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        die(f"could not read {path}: {exc}")
    if not isinstance(value, dict):
        die(f"expected JSON object in {path}")
    return value


def frozen_run(run_id: str) -> Dict[str, Any]:
    runs = read_json(RUNS_PATH).get("runs", [])
    matches = [run for run in runs if run.get("run_id") == run_id]
    if len(matches) != 1:
        die(f"run ID is absent or duplicated: {run_id}")
    return matches[0]


def validate_workspace(workspace: Path) -> None:
    workspace = workspace.resolve()
    if not workspace.is_dir():
        die(f"workspace is not a directory: {workspace}")
    if REPO_ROOT == workspace or REPO_ROOT in workspace.parents:
        die("workspace must be outside the control repository")
    if not (workspace / "TASK.md").is_file():
        die("workspace is missing TASK.md")
    case_file = workspace / "CASE.json"
    if case_file.is_file():
        case = read_json(case_file)
        forbidden = {"bug_id", "buggy_commit", "fixed_commit", "reference_patch", "hidden_tests"}
        present = sorted(forbidden.intersection(case))
        if present:
            die("agent-visible CASE.json contains ground truth: " + ", ".join(present))


def validate_credential_file(path: Path) -> None:
    path = path.resolve()
    if not path.is_file():
        die(f"credential file is missing: {path}")
    if path.name != "credentials.toml":
        die("credential mount must be a credentials.toml file")
    if REPO_ROOT in path.parents or REPO_ROOT == path:
        die("credential file must not be in the control repository")


def docker_command(
    *, run: Dict[str, Any], workspace: Path, output_dir: Path, credential_file: Path,
    image: str, network: str, proxy_url: str,
) -> List[str]:
    return [
        "docker", "run", "--rm", "--init",
        "--platform", "linux/arm64",
        "--read-only",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges:true",
        "--pids-limit", "512",
        "--memory", "4g",
        "--cpus", "4",
        "--workdir", "/workspace",
        "--network", network,
        "--mount", f"type=bind,src={workspace},dst=/workspace",
        "--mount", f"type=bind,src={output_dir},dst=/artifacts",
        "--mount", f"type=bind,src={credential_file},dst=/run/devin-data/devin/credentials.toml,ro",
        "--tmpfs", "/run:rw,noexec,nosuid,size=512m",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=1g",
        "--env", "HOME=/root",
        "--env", "XDG_CONFIG_HOME=/run/devin-config",
        "--env", "XDG_DATA_HOME=/run/devin-data",
        "--env", f"HTTPS_PROXY={proxy_url}",
        "--env", f"HTTP_PROXY={proxy_url}",
        "--env", "NO_PROXY=localhost,private-network",
        image,
        "--model", run["model"],
        "--print",
        "--prompt-file", "/workspace/TASK.md",
        "--export", "/artifacts/devin-session-export.json",
        "--permission-mode", "dangerous",
        "--respect-workspace-trust", "false",
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--credential-file", type=Path, required=True)
    parser.add_argument("--image", default=DEFAULT_IMAGE)
    parser.add_argument("--network", default="e002-internal")
    parser.add_argument("--proxy-url", default="http://egress-proxy:3128")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm-paid", action="store_true")
    args = parser.parse_args(argv)
    if args.confirm_paid and not args.execute:
        die("--confirm-paid requires --execute")
    run = frozen_run(args.run_id)
    workspace = args.workspace.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    credential_file = args.credential_file.expanduser().resolve()
    config = read_json(CONFIG_PATH)
    frozen_image = config.get("agent", {}).get("container_image")
    if args.image != frozen_image:
        die("image does not match the frozen Experiment 002 image reference")
    validate_workspace(workspace)
    validate_credential_file(credential_file)
    if credential_file == workspace or workspace in credential_file.parents:
        die("credential file must be outside the agent workspace")
    if credential_file == output_dir or output_dir in credential_file.parents:
        die("credential file must be outside the artifact directory")
    if REPO_ROOT == output_dir or REPO_ROOT in output_dir.parents:
        die("artifact directory must be outside the control repository")
    if output_dir == workspace or workspace in output_dir.parents:
        die("output directory must be outside the agent workspace")
    if output_dir.exists() and any(output_dir.iterdir()):
        die(f"output directory must be empty/fresh: {output_dir}")
    command = docker_command(
        run=run, workspace=workspace, output_dir=output_dir,
        credential_file=credential_file, image=args.image,
        network=args.network, proxy_url=args.proxy_url,
    )
    plan = {
        "experiment_id": "experiment-002",
        "run_id": args.run_id,
        "model": run["model"],
        "workspace": str(workspace),
        "output_dir": str(output_dir),
        "command": command,
        "command_display": " ".join(shlex.quote(part) for part in command),
        "permission_mode": "dangerous",
        "effective_mode": "Bypass",
        "network": {"agent_network": args.network, "proxy": args.proxy_url},
        "docker_socket_mounted": False,
        "privileged": False,
        "devin_invoked": False,
    }
    if not args.execute:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "dry-run-plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(plan, indent=2))
        return 0
    if not args.confirm_paid:
        die("refusing Devin invocation without --confirm-paid")
    output_dir.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(timezone.utc)
    started_monotonic = time.monotonic()
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    ended_at = datetime.now(timezone.utc)
    wall_time_seconds = time.monotonic() - started_monotonic
    (output_dir / "devin.stdout.txt").write_text(completed.stdout or "", encoding="utf-8")
    (output_dir / "devin.stderr.txt").write_text(completed.stderr or "", encoding="utf-8")
    result = {
        **plan,
        "devin_invoked": True,
        "returncode": completed.returncode,
        "started_at_utc": started_at.isoformat(),
        "ended_at_utc": ended_at.isoformat(),
        "wall_time_seconds": wall_time_seconds,
        "stdout_path": str(output_dir / "devin.stdout.txt"),
        "stderr_path": str(output_dir / "devin.stderr.txt"),
        "export_path": str(output_dir / "devin-session-export.json") if (output_dir / "devin-session-export.json").exists() else None,
    }
    (output_dir / "container-run-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if completed.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
