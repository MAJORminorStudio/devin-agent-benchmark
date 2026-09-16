#!/usr/bin/env python3
"""Run the disposable, non-benchmark E002 permission validation case."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Sequence


DEFAULT_IMAGE = "devin-e002:3000.10.21@sha256:bb045374bc655c185cced99a6cb769a6695c88527fb432456eb8e0d6dd0e4bb6"


def die(message: str) -> None:
    raise SystemExit(f"error: {message}")


def docker_command(
    *, workspace: Path, output_dir: Path, credential_file: Path,
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
        "--model", "swe-2-medium",
        "--print",
        "--prompt-file", "/workspace/TASK.md",
        "--export", "/artifacts/devin-session-export.json",
        "--permission-mode", "dangerous",
        "--respect-workspace-trust", "false",
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--credential-file", type=Path, required=True)
    parser.add_argument("--image", default=DEFAULT_IMAGE)
    parser.add_argument("--network", default="e002-internal-validation")
    parser.add_argument("--proxy-url", default="http://egress-proxy:3128")
    args = parser.parse_args(argv)

    workspace = args.workspace.resolve()
    output_dir = args.output_dir.resolve()
    credential_file = args.credential_file.resolve()
    if not (workspace / "TASK.md").is_file():
        die("synthetic workspace is missing TASK.md")
    if not credential_file.is_file() or credential_file.name != "credentials.toml":
        die("credential file must be an existing credentials.toml")
    if output_dir.exists() and any(output_dir.iterdir()):
        die("synthetic output directory must be fresh")
    output_dir.mkdir(parents=True, exist_ok=True)

    command = docker_command(
        workspace=workspace, output_dir=output_dir,
        credential_file=credential_file, image=args.image,
        network=args.network, proxy_url=args.proxy_url,
    )
    started = time.monotonic()
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, check=False)
    elapsed = time.monotonic() - started
    (output_dir / "devin.stdout.txt").write_text(completed.stdout or "", encoding="utf-8")
    (output_dir / "devin.stderr.txt").write_text(completed.stderr or "", encoding="utf-8")
    result = {
        "validation": "experiment-002-synthetic-permission",
        "model": "swe-2-medium",
        "permission_mode": "dangerous",
        "effective_mode": "Bypass",
        "network": args.network,
        "proxy_url": args.proxy_url,
        "command": command,
        "returncode": completed.returncode,
        "elapsed_seconds": elapsed,
        "stdout_path": str(output_dir / "devin.stdout.txt"),
        "stderr_path": str(output_dir / "devin.stderr.txt"),
        "export_path": str(output_dir / "devin-session-export.json") if (output_dir / "devin-session-export.json").exists() else None,
    }
    (output_dir / "synthetic-run-result.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))
    return 0 if completed.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
