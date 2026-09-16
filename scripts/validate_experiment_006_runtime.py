#!/usr/bin/env python3
"""Validate the frozen E006 trees inside the repaired, immutable runtime.

This is a control-side validator. It starts disposable containers with the
case source and private evaluator mounted separately, and it never invokes
Devin, SWE-2, or an agent-produced workspace.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = REPO_ROOT / ".benchmarks" / "private-run"
CASES_ROOT = PRIVATE_ROOT / "cases"
HISTORICAL_ROOT = PRIVATE_ROOT / "historical-cases"
EVALUATION_ROOT = PRIVATE_ROOT / "evaluation"
CONFIG_PATH = REPO_ROOT / "manifests" / "experiment-006-config.json"
RUNS_PATH = REPO_ROOT / "manifests" / "experiment-006-runs.json"
HIST_MANIFEST_PATH = PRIVATE_ROOT / "historical-manifest.json"
BASELINE_PATH = PRIVATE_ROOT / "results" / "ground-truth.json"
RESULT_PATH = PRIVATE_ROOT / "results" / "runtime-validation.json"
IGNORED_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".tox"}
MARKER = "__E006_RUNTIME_RESULT__"


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def load_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ignore_caches(_directory: str, names: List[str]) -> Iterable[str]:
    return [name for name in names if name in IGNORED_NAMES]


def source_tree(case_id: str, side: str) -> Path:
    if case_id.startswith("E006-K"):
        return HISTORICAL_ROOT / case_id / "verification" / side
    return CASES_ROOT / case_id / side


def commands_for_case(case_id: str, config_case: Mapping[str, Any], hist_case: Mapping[str, Any] | None) -> List[str]:
    if hist_case is not None:
        return [str(command) for command in hist_case["test_command"]]
    return [str(config_case["public_test_command"])]


def runtime_env(config: Mapping[str, Any], case_id: str) -> Mapping[str, str]:
    runtime = config["runtime"]["case_environments"][case_id]
    version = str(runtime["python"])
    venv = str(runtime["venv"])
    path = "/opt/e006/venvs/{}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin".format(venv)
    source_path = "/workspace/src" if case_id.startswith("E006-H") else "/workspace"
    return {
        "PATH": path,
        "LD_LIBRARY_PATH": str(runtime["runtime_lib"]),
        "PYTHONPATH": source_path,
        "PYTHONDONTWRITEBYTECODE": "1",
        "E006_CASE_ID": case_id,
        "E006_EXPECTED_PYTHON": version,
    }


def docker_prefix(config: Mapping[str, Any], workspace: Path, evaluator: Path, artifacts: Path, case_id: str) -> List[str]:
    isolation = config["isolation_contract"]
    env = runtime_env(config, case_id)
    command = [
        "docker", "run", "--rm", "--init", "--platform", "linux/arm64", "--read-only",
        "--cap-drop", "ALL", "--security-opt", "no-new-privileges:true", "--pids-limit",
        str(isolation["pids_limit"]), "--memory", str(isolation["memory"]), "--cpus",
        str(isolation["cpus"]), "--workdir", "/workspace", "--network", str(isolation["network"]),
        "--mount", f"type=bind,src={workspace},dst=/workspace", "--mount",
        f"type=bind,src={evaluator},dst=/control/evaluation/{case_id},ro", "--mount",
        f"type=bind,src={artifacts},dst=/artifacts", "--tmpfs", "/run:rw,noexec,nosuid,size=512m",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=1g",
    ]
    for key, value in {
        "HOME": "/root",
        "XDG_CONFIG_HOME": "/run/devin-config",
        "XDG_DATA_HOME": "/run/devin-data",
        "HTTPS_PROXY": str(isolation["egress_proxy"]),
        "HTTP_PROXY": str(isolation["egress_proxy"]),
        "NO_PROXY": "localhost,private-network",
        **env,
    }.items():
        command.extend(["--env", f"{key}={value}"])
    command.extend(["--entrypoint", "/bin/sh", str(config["agent"]["container_image"])])
    return command


def shell_script(commands: Sequence[tuple[str, str]]) -> str:
    lines = ["set +e", "python --version", f"printf '{MARKER}version:%s\\n' $?"]
    for label, command in commands:
        lines.extend([
            f"printf '{MARKER}start:{label}\\n'",
            command,
            "rc=$?",
            f"printf '{MARKER}result:{label}:%s\\n' \"$rc\"",
        ])
    return "\n".join(lines)


def parse_container_output(output: str, commands: Sequence[tuple[str, str]]) -> Dict[str, Any]:
    version_match = re.search(rf"{re.escape(MARKER)}version:(\d+)", output)
    if not version_match:
        fail("runtime container did not report its Python version")
    results: Dict[str, Any] = {"python_returncode": int(version_match.group(1))}
    for label, command in commands:
        match = re.search(rf"{re.escape(MARKER)}result:{re.escape(label)}:(\d+)", output)
        if not match:
            fail(f"runtime container did not report result for {label}")
        results[label] = {
            "command": command,
            "returncode": int(match.group(1)),
            "status": "pass" if int(match.group(1)) == 0 else "fail",
        }
    return results


def run_case(
    config: Mapping[str, Any],
    case_id: str,
    side: str,
    config_case: Mapping[str, Any],
    hist_case: Mapping[str, Any] | None,
    repetition: int,
    work_root: Path,
) -> Dict[str, Any]:
    workspace = work_root / f"{case_id}-{side}-workspace"
    artifacts = work_root / f"{case_id}-{side}-artifacts"
    evaluator = work_root / f"{case_id}-{side}-evaluator"
    shutil.copytree(source_tree(case_id, side), workspace, symlinks=True, ignore=ignore_caches)
    shutil.copytree(EVALUATION_ROOT / case_id, evaluator, symlinks=True, ignore=ignore_caches)
    artifacts.mkdir()
    prompt = REPO_ROOT / str(config_case["prompt"])
    (workspace / "TASK.md").write_bytes(prompt.read_bytes())

    public = commands_for_case(case_id, config_case, hist_case)
    commands = [(f"public-{index}", command) for index, command in enumerate(public, 1)]
    commands.extend([
        ("held-out", f"python -m pytest -q /control/evaluation/{case_id}/test_behavior.py"),
        ("regression", f"python -m pytest -q /control/evaluation/{case_id}/test_regression.py"),
    ])
    script = shell_script(commands)
    command = docker_prefix(config, workspace, evaluator, artifacts, case_id) + ["-c", script]
    started = time.monotonic()
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
        timeout=300,
    )
    elapsed = round(time.monotonic() - started, 3)
    parsed = parse_container_output(completed.stdout or "", commands)
    version = str(config["runtime"]["case_environments"][case_id]["python"])
    version_text = (completed.stdout or "").split(f"{MARKER}version:", 1)[0].splitlines()
    if parsed["python_returncode"] != 0:
        fail(f"Python version probe failed for {case_id}/{side}")
    if not any(version in line for line in version_text):
        fail(f"wrong Python version for {case_id}/{side}; expected {version}")
    statuses = {
        "public": "pass" if all(parsed[label]["status"] == "pass" for label, _ in commands if label.startswith("public-")) else "fail",
        "held_out": parsed["held-out"]["status"],
        "regression": parsed["regression"]["status"],
    }
    return {
        "case_id": case_id,
        "side": side,
        "repetition": repetition,
        "python": version,
        "runtime_venv": config["runtime"]["case_environments"][case_id]["venv"],
        "container_returncode": completed.returncode,
        "elapsed_seconds": elapsed,
        "statuses": statuses,
        "signature": {
            "public": [f"{parsed[label]['status']}:{parsed[label]['returncode']}" for label, _ in commands if label.startswith("public-")],
            "held_out": [f"{parsed['held-out']['status']}:{parsed['held-out']['returncode']}"],
            "regression": [f"{parsed['regression']['status']}:{parsed['regression']['returncode']}"],
        },
        "commands": {label: parsed[label] for label, _ in commands},
        "container_command_shape": {
            "platform": "linux/arm64",
            "network": config["isolation_contract"]["network"],
            "read_only_root": True,
            "capabilities": "all dropped",
            "no_new_privileges": True,
            "cpus": config["isolation_contract"]["cpus"],
            "memory": config["isolation_contract"]["memory"],
            "pids_limit": config["isolation_contract"]["pids_limit"],
            "control_evaluator_mounted": True,
            "agent_invoked": False,
        },
        "output_tail": (completed.stdout or "")[-3000:],
    }


def expected_ok(result: Mapping[str, Any], baseline: Mapping[str, Any]) -> None:
    case_id = str(result["case_id"])
    side = str(result["side"])
    expected = baseline["matrix"][case_id][side]
    if result["statuses"] != expected["statuses"]:
        fail(f"status drift for {case_id}/{side}: {result['statuses']} != {expected['statuses']}")
    if result["signature"] != expected["signature"]:
        fail(f"signature drift for {case_id}/{side}: {result['signature']} != {expected['signature']}")


def main() -> int:
    config = load_json(CONFIG_PATH)
    runs = load_json(RUNS_PATH)["runs"]
    hist_manifest = load_json(HIST_MANIFEST_PATH)
    baseline = load_json(BASELINE_PATH)
    config_cases = {str(case["experiment_case_id"]): case for case in config["cases"]}
    hist_cases = {str(case["case_id"]): case for case in hist_manifest["cases"]}
    cases = list(config_cases)
    if len(cases) != 10 or len(runs) != 20:
        fail("frozen E006 case/run counts changed")
    if not config["agent"]["container_image"].startswith("devin-e006:"):
        fail("runtime validator is not pointed at the repaired derived image")

    results: List[Dict[str, Any]] = []
    signatures: Dict[str, Dict[str, Dict[str, Any]]] = {}
    with tempfile.TemporaryDirectory(prefix="e006-runtime-validation-") as temp:
        temp_root = Path(temp)
        for repetition in (1, 2):
            repetition_root = temp_root / f"repetition-{repetition}"
            repetition_root.mkdir()
            for case_id in cases:
                for side in ("buggy", "fixed"):
                    result = run_case(
                        config, case_id, side, config_cases[case_id], hist_cases.get(case_id),
                        repetition, repetition_root,
                    )
                    expected_ok(result, baseline)
                    results.append(result)
                    signatures.setdefault(case_id, {}).setdefault(side, {})[str(repetition)] = result["signature"]

    for case_id in cases:
        for side in ("buggy", "fixed"):
            if signatures[case_id][side]["1"] != signatures[case_id][side]["2"]:
                fail(f"non-deterministic runtime signature for {case_id}/{side}")

    output = {
        "experiment_id": "experiment-006",
        "validator_version": "experiment-006-runtime-validator-v1",
        "image": config["agent"]["container_image"],
        "base_image": config["agent"]["base_container_image"],
        "agent_invocations": 0,
        "swe2_invocations": 0,
        "experimental_runs": 0,
        "cases": 10,
        "sides": 20,
        "repetitions": 2,
        "fresh_container_per_case_side_repetition": True,
        "fresh_workspace_and_evaluator_copies": True,
        "deterministic": True,
        "baseline_signature_match": True,
        "evaluator_access": "control-side only; never mounted in an agent session",
        "results": results,
    }
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    compact = {
        case_id: {
            side: {"statuses": baseline["matrix"][case_id][side]["statuses"], "signature": signatures[case_id][side]["1"]}
            for side in ("buggy", "fixed")
        }
        for case_id in cases
    }
    print(json.dumps({
        "image": output["image"],
        "cases": 10,
        "containers": len(results),
        "repetitions": 2,
        "deterministic": True,
        "baseline_signature_match": True,
        "matrix": compact,
        "result_sha256": sha256(RESULT_PATH),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
