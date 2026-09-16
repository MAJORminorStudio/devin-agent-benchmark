#!/usr/bin/env python3
"""Provision isolated, evaluator-only virtual environments for Experiment 001."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

import evaluator_environment as evaluator  # noqa: E402


def run(args: Sequence[str], *, cwd: Optional[Path] = None) -> str:
    result = subprocess.run(
        list(args), cwd=str(cwd) if cwd else None, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    if result.returncode != 0:
        raise SystemExit(f"command failed ({result.returncode}): {' '.join(args)}\n{result.stdout}")
    return result.stdout or ""


def provision_case(case_id: str, env_root: Path, uv_binary: str, force: bool) -> Dict[str, Any]:
    spec = evaluator.case_spec(case_id)
    metadata = spec["metadata"]
    environment = metadata.get("environment", {})
    requested_python = str(environment.get("python", ""))
    if not requested_python:
        raise SystemExit(f"missing evaluator Python version for {case_id}")
    env_dir = evaluator.environment_dir(env_root, case_id)
    env_root.mkdir(parents=True, exist_ok=True)
    if env_dir.exists() and not force:
        raise SystemExit(f"environment exists; pass --force to rebuild: {env_dir}")
    env_dir.parent.mkdir(parents=True, exist_ok=True)
    venv_command = [uv_binary, "venv", "--no-project", "--clear", "--python", requested_python, str(env_dir)]
    venv_output = run(venv_command)
    python = evaluator.python_bin(env_root, case_id)
    install = [str(item) for item in environment.get("install", [])]
    install_command = [uv_binary, "pip", "install", "--exact", "--python", str(python), *install]
    install_output = run(install_command) if install else "(no third-party packages required)\n"
    version_output = run([str(python), "--version"]).strip()
    freeze_output = run([uv_binary, "pip", "freeze", "--python", str(python)])
    record = {
        "record_version": 1,
        "case_id": case_id,
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "environment_root": str(env_dir),
        "requested_python": requested_python,
        "python_version": version_output,
        "spec_sha256": evaluator.spec_digest(environment),
        "install": install,
        "commands": {
            "venv": venv_command,
            "install": install_command,
            "freeze": [uv_binary, "pip", "freeze", "--python", str(python)],
        },
        "outputs": {
            "venv": venv_output,
            "install": install_output,
            "freeze": freeze_output,
        },
    }
    evaluator.environment_record_path(env_root, case_id).write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    ready = evaluator.readiness(env_root, case_id)
    if ready["status"] != "pass":
        raise SystemExit("environment failed readiness: " + "; ".join(ready["problems"]))
    return {"case_id": case_id, "record": record, "readiness": ready}


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-root", type=Path, required=True)
    parser.add_argument("--uv", default="uv")
    parser.add_argument("--case-id", action="append")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    cases = args.case_id or ["black-16", "fastapi-3", "scrapy-3", "tqdm-5", "tornado-13"]
    results = [provision_case(case_id, args.env_root.expanduser().resolve(), args.uv, args.force) for case_id in cases]
    print(json.dumps({"status": "pass", "env_root": str(args.env_root.expanduser().resolve()), "cases": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
