#!/usr/bin/env python3
"""Shared evaluator-environment specification, readiness, and process setup."""

from __future__ import annotations

import hashlib
import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_MANIFEST = REPO_ROOT / "manifests" / "experiment-001.json"
EVALUATION_ROOT = REPO_ROOT / "evaluation" / "experiment-001"


def read_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def case_spec(case_id: str) -> Dict[str, Any]:
    manifest = read_json(CASE_MANIFEST)
    matches = [item for item in manifest.get("cases", []) if item.get("case_id") == case_id]
    if len(matches) != 1:
        raise ValueError(f"case not found or duplicated: {case_id}")
    metadata = read_json(EVALUATION_ROOT / case_id / "metadata.json")
    if metadata.get("case_id") != case_id:
        raise ValueError(f"case metadata mismatch: {case_id}")
    return {"case": matches[0], "metadata": metadata}


def environment_dir(env_root: Path, case_id: str) -> Path:
    return env_root.expanduser().resolve() / case_id


def python_bin(env_root: Path, case_id: str) -> Path:
    return environment_dir(env_root, case_id) / "bin" / "python"


def environment_record_path(env_root: Path, case_id: str) -> Path:
    return environment_dir(env_root, case_id) / ".evaluator-environment.json"


def spec_digest(spec: Mapping[str, Any]) -> str:
    payload = json.dumps(spec, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def command_strings(spec: Mapping[str, Any]) -> Iterable[str]:
    case = spec["case"]
    metadata = spec["metadata"]
    yield from case.get("test_command", [])
    yield from metadata.get("heldout_commands", [])
    yield from metadata.get("regression_commands", [])


def command_tools(spec: Mapping[str, Any]) -> Sequence[str]:
    tools = []
    for command in command_strings(spec):
        parts = shlex.split(str(command))
        if parts and parts[0] not in tools:
            tools.append(parts[0])
    return tools


def process_environment(
    env_root: Path,
    case_id: str,
    workspace: Optional[Path] = None,
    base: Optional[Mapping[str, str]] = None,
) -> Dict[str, str]:
    """Return an environment that resolves frozen commands inside the case venv."""

    env = dict(base) if base is not None else os.environ.copy()
    env_dir = environment_dir(env_root, case_id)
    bin_dir = env_dir / "bin"
    env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
    env["VIRTUAL_ENV"] = str(env_dir)
    env.pop("PYTHONPATH", None)
    env["PYTHONNOUSERSITE"] = "1"
    if workspace is not None:
        env["PYTHONPATH"] = str(workspace.resolve())
    return env


def _capture(args: Sequence[str], *, env: Mapping[str, str]) -> Dict[str, Any]:
    try:
        result = subprocess.run(
            list(args), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            check=False, env=dict(env), timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": list(args), "returncode": 127, "output": str(exc)}
    return {"command": list(args), "returncode": result.returncode, "output": result.stdout or ""}


def readiness(env_root: Path, case_id: str) -> Dict[str, Any]:
    """Check that a provisioned environment matches the frozen case spec."""

    env_root = env_root.expanduser().resolve()
    problems = []
    try:
        spec = case_spec(case_id)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"status": "error", "case_id": case_id, "problems": [str(exc)]}

    env_dir = environment_dir(env_root, case_id)
    python = python_bin(env_root, case_id)
    record_path = environment_record_path(env_root, case_id)
    if not env_dir.is_dir():
        problems.append(f"environment directory is missing: {env_dir}")
    if not python.is_file() or not os.access(python, os.X_OK):
        problems.append(f"environment Python is missing or not executable: {python}")
    record: Dict[str, Any] = {}
    if not record_path.is_file():
        problems.append(f"environment record is missing: {record_path}")
    else:
        try:
            record = read_json(record_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            problems.append(str(exc))
        if record.get("case_id") != case_id:
            problems.append("environment record case mismatch")
        if record.get("spec_sha256") != spec_digest(spec["metadata"].get("environment", {})):
            problems.append("environment record does not match frozen metadata")

    if python.is_file() and os.access(python, os.X_OK):
        env = process_environment(env_root, case_id)
        version = _capture([str(python), "--version"], env=env)
        if version["returncode"] != 0:
            problems.append(f"Python version probe failed: {version['output'].strip()}")
        else:
            expected = str(spec["metadata"].get("environment", {}).get("python", ""))
            actual = version["output"].strip()
            if expected and not actual.startswith(f"Python {expected}"):
                problems.append(f"Python version mismatch: expected {expected}, got {actual}")
        for tool in command_tools(spec):
            probe = _capture(
                [str(python), "-c", "import shutil,sys; sys.exit(0 if shutil.which(sys.argv[1]) else 1)", tool],
                env=env,
            )
            if probe["returncode"] != 0:
                problems.append(f"frozen command tool is unavailable: {tool}")

    return {
        "status": "pass" if not problems else "error",
        "case_id": case_id,
        "environment_root": str(env_dir),
        "python": str(python),
        "record_path": str(record_path),
        "spec_sha256": spec_digest(spec["metadata"].get("environment", {})),
        "requested_python": spec["metadata"].get("environment", {}).get("python"),
        "frozen_command_tools": list(command_tools(spec)),
        "record": record,
        "problems": problems,
    }


def require_ready(env_root: Path, case_id: str) -> Dict[str, Any]:
    result = readiness(env_root, case_id)
    if result["status"] != "pass":
        raise RuntimeError("evaluator environment is not ready: " + "; ".join(result["problems"]))
    return result
