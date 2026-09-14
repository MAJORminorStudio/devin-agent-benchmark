#!/usr/bin/env python3
"""Plan or run one Devin evaluation using the inspected local CLI.

The default operation is a dry-run. A real invocation requires both
``--execute`` and ``--confirm-paid`` so a future operator must make an
explicit checkpoint before spending Devin credits.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "manifests" / "experiment-001-config.json"


def die(message: str) -> None:
    raise SystemExit(f"error: {message}")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        die(f"could not read {path}: {exc}")
    if not isinstance(data, dict):
        die(f"expected an object in {path}")
    return data


def check_workspace(workspace: Path) -> Dict[str, Any]:
    workspace = workspace.expanduser().resolve()
    if workspace == Path(workspace.anchor) or not workspace.is_dir():
        die(f"workspace is not a directory: {workspace}")
    if REPO_ROOT == workspace or REPO_ROOT in workspace.parents:
        die("agent workspace must be outside the control repository")
    case_file = workspace / "CASE.json"
    task_file = workspace / "TASK.md"
    setup_file = workspace / "SETUP.md"
    if not case_file.is_file() or not task_file.is_file() or not setup_file.is_file():
        die("workspace is missing exporter-created CASE.json, TASK.md, or SETUP.md")
    case = read_json(case_file)
    forbidden = {"bug_id", "buggy_commit", "fixed_commit", "difficulty", "status", "reference_patch", "hidden_tests"}
    present = sorted(forbidden.intersection(case))
    if present:
        die("agent-visible CASE.json contains ground-truth fields: " + ", ".join(present))
    audit = workspace.parent / f"{workspace.name}.leak-audit.json"
    if not audit.is_file():
        die(f"leak audit is missing: {audit}")
    audit_data = read_json(audit)
    if audit_data.get("status") != "pass" or audit_data.get("destination") != str(workspace):
        die("workspace leak audit is not a passing audit for this exact destination")
    return case


def validate_model(config: Dict[str, Any], model: str) -> None:
    expected = config["agent"]["model"]
    if model != expected:
        die(f"model is frozen to {expected}; refusing {model}")
    if model.lower().startswith("fusion") or "fusion" in model.lower():
        die("Fusion models are forbidden for Experiment 001")


def run_capture(args: Sequence[str], *, cwd: Optional[Path] = None, timeout: int = 60) -> Dict[str, Any]:
    started = time.monotonic()
    try:
        process = subprocess.run(
            list(args), cwd=str(cwd) if cwd else None, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=timeout,
        )
        return {"command": list(args), "returncode": process.returncode, "output": process.stdout or "", "timed_out": False, "elapsed_seconds": round(time.monotonic() - started, 3)}
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return {"command": list(args), "returncode": 124, "output": output, "timed_out": True, "elapsed_seconds": round(time.monotonic() - started, 3)}
    except OSError as exc:
        return {"command": list(args), "returncode": 127, "output": str(exc), "timed_out": False, "elapsed_seconds": round(time.monotonic() - started, 3)}


def session_inventory(binary: str) -> Dict[str, Any]:
    return run_capture([binary, "list", "--format", "json"], timeout=60)


def invocation_command(binary: str, model: str, prompt_file: Path, export_file: Path, workspace: Path, config: Dict[str, Any]) -> List[str]:
    permission = config["agent"].get("permission_mode", "accept-edits")
    trust = "true" if config["agent"].get("workspace_trust_override", False) else "false"
    return [
        binary,
        "--model", model,
        "--print",
        "--prompt-file", str(prompt_file),
        "--export", str(export_file),
        "--permission-mode", permission,
        "--respect-workspace-trust", trust,
        str(workspace),
    ]


def plan_run(config: Dict[str, Any], case: Dict[str, Any], workspace: Path, output_dir: Path, binary: str, model: str) -> Dict[str, Any]:
    prompt_file = workspace / "TASK.md"
    export_file = output_dir / "devin-session-export.json"
    return {
        "plan_version": 1,
        "planned_at": now(),
        "experiment_id": config["experiment_id"],
        "experiment_case_id": case.get("experiment_case_id"),
        "case_id": case.get("case_id"),
        "workspace": str(workspace),
        "output_dir": str(output_dir),
        "cli_binary": binary,
        "cli_model": model,
        "model_family": config["agent"].get("model_family"),
        "fusion": {"enabled": False, "lock": config["agent"].get("fusion_lock_method")},
        "command": invocation_command(binary, model, prompt_file, export_file, workspace, config),
        "noninteractive": True,
        "paid_invocation": True,
        "requires_explicit_confirmation": ["--execute", "--confirm-paid"],
        "substantive_intervention_limit": config["intervention_policy"]["maximum_substantive_interventions"],
        "manual_checkpoints": [
            "Confirm the Devin subscription/credit budget before invoking.",
            "Record any human intervention in the result record; substantive debugging hints are forbidden.",
            "Capture any stable session ID, URL, usage/cost, repository branch, and PR URL only if the provider exposes them.",
        ],
        "unsupported_automatic_operations": [
            "No inspected CLI command creates a general cloud Devin task or handoff.",
            "No inspected CLI output exposes stable task IDs, URLs, ACUs, usage, cost, repository branch, or PR creation as runner flags.",
        ],
        "devin_invoked": False,
    }


def execute_run(config: Dict[str, Any], case: Dict[str, Any], workspace: Path, output_dir: Path, binary: str, model: str, timeout: int) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = workspace / "TASK.md"
    export_file = output_dir / "devin-session-export.json"
    command = invocation_command(binary, model, prompt_file, export_file, workspace, config)
    started_at = now()
    before = session_inventory(binary)
    process = run_capture(command, timeout=timeout)
    ended_at = now()
    after = session_inventory(binary)
    result = {
        "experiment_id": config["experiment_id"],
        "experiment_case_id": case.get("experiment_case_id"),
        "case_id": case.get("case_id"),
        "agent": {
            "name": config["agent"]["name"],
            "configuration": config["configuration_version"],
            "model": model,
            "model_family": config["agent"].get("model_family"),
            "fusion_enabled": False,
            "subscription_or_usage": {"available": False, "amount": None, "currency": None},
            "cli_version": config["agent"].get("cli_version"),
        },
        "prompt": prompt_file.read_text(encoding="utf-8"),
        "started_at": started_at,
        "ended_at": ended_at,
        "elapsed_seconds": process["elapsed_seconds"],
        "interventions": [],
        "patch": {"format": "unified-diff", "path": None, "sha256": None},
        "tests_before": {"status": "verified-in-phase-1", "source": "reproducibility.json"},
        "tests_after": {"status": "pending-post-session-evaluation"},
        "pass": None,
        "regression_status": "not-run",
        "evaluator_notes": "Runner capture only; post-session evaluator must be run separately.",
        "invocation": {"command": command, "returncode": process["returncode"], "timed_out": process["timed_out"], "stdout_stderr": process["output"], "export_path": str(export_file) if export_file.exists() else None},
        "session_inventory_before": before,
        "session_inventory_after": after,
        "provider_fields": {"session_id": None, "session_url": None, "usage": None, "cost": None, "repository_branch": None, "pull_request_url": None},
    }
    result_path = output_dir / "runner-result.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--devin-binary", default="devin")
    parser.add_argument("--model")
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--execute", action="store_true", help="actually invoke Devin; requires --confirm-paid")
    parser.add_argument("--confirm-paid", action="store_true", help="explicitly acknowledge that an invocation may consume paid credits")
    args = parser.parse_args(argv)
    if args.confirm_paid and not args.execute:
        die("--confirm-paid requires --execute")
    config = read_json(args.config)
    case = check_workspace(args.workspace)
    if case.get("case_id") != args.case_id:
        die(f"workspace CASE.json is for {case.get('case_id')}, not {args.case_id}")
    model = args.model or config["agent"]["model"]
    validate_model(config, model)
    workspace = args.workspace.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    if output_dir == workspace or workspace in output_dir.parents:
        die("runner output must not be inside the agent workspace")
    if not args.execute:
        output_dir.mkdir(parents=True, exist_ok=True)
        plan = plan_run(config, case, workspace, output_dir, args.devin_binary, model)
        plan_path = output_dir / "dry-run-plan.json"
        plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(plan, indent=2))
        return 0
    if not args.confirm_paid:
        die("refusing paid Devin invocation without --confirm-paid")
    result = execute_run(config, case, workspace, output_dir, args.devin_binary, model, args.timeout)
    print(json.dumps(result, indent=2))
    return 0 if result["invocation"]["returncode"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
