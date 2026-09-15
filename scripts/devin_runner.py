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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import evaluator_environment as evaluator_env  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "manifests" / "experiment-001-config.json"
DEFAULT_RUN_MANIFEST = REPO_ROOT / "manifests" / "experiment-001-runs.json"


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


def validate_model(config: Dict[str, Any], model: str, expected: Optional[str] = None) -> None:
    frozen_models = {item["model"] for item in config.get("conditions", {}).values()}
    if model not in frozen_models:
        die(f"model is not one of the frozen Experiment 001 models: {model}")
    if expected and model != expected:
        die(f"run manifest freezes model to {expected}; refusing {model}")
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


def session_inventory(binary: str, *, cwd: Optional[Path] = None) -> Dict[str, Any]:
    return run_capture([binary, "list", "--format", "json"], cwd=cwd, timeout=60)


def invocation_command(binary: str, model: str, prompt_file: Path, export_file: Path, workspace: Path, config: Dict[str, Any]) -> List[str]:
    # The installed CLI reserves positional PATH arguments for desktop mode
    # and rejects them together with --print. The workspace is therefore
    # supplied as subprocess cwd; --prompt-file preserves prompt bytes.
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
    ]


def plan_run(config: Dict[str, Any], case: Dict[str, Any], workspace: Path, output_dir: Path, binary: str, model: str, run: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    prompt_file = workspace / "TASK.md"
    export_file = output_dir / "devin-session-export.json"
    return {
        "plan_version": 1,
        "planned_at": now(),
        "experiment_id": config["experiment_id"],
        "experiment_case_id": case.get("experiment_case_id"),
        "case_id": case.get("case_id"),
        "run_id": run.get("run_id") if run else None,
        "condition": run.get("condition") if run else None,
        "workspace": str(workspace),
        "output_dir": str(output_dir),
        "cli_binary": binary,
        "cli_model": model,
        "model_family": config["agent"].get("model_family"),
        "fusion": {"enabled": False, "lock": config["agent"].get("fusion_lock_method")},
        "command": invocation_command(binary, model, prompt_file, export_file, workspace, config),
        "working_directory": str(workspace),
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


def execute_run(config: Dict[str, Any], case: Dict[str, Any], workspace: Path, output_dir: Path, binary: str, model: str, timeout: int, run: Optional[Dict[str, Any]] = None, evaluator_readiness: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = workspace / "TASK.md"
    export_file = output_dir / "devin-session-export.json"
    command = invocation_command(binary, model, prompt_file, export_file, workspace, config)
    started_at = now()
    before = session_inventory(binary, cwd=workspace)
    process = run_capture(command, cwd=workspace, timeout=timeout)
    ended_at = now()
    after = session_inventory(binary, cwd=workspace)
    result = {
        "experiment_id": config["experiment_id"],
        "experiment_case_id": case.get("experiment_case_id"),
        "case_id": case.get("case_id"),
        "run_id": run.get("run_id") if run else None,
        "condition": run.get("condition") if run else None,
        "effort_level": run.get("effort_level") if run else config.get("agent", {}).get("effort_level"),
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
        "steps": None,
        "interventions": [],
        "patch": {"format": "unified-diff", "path": None, "sha256": None},
        "tests_before": {"status": "verified-in-phase-1", "source": "reproducibility.json"},
        "tests_after": {"status": "pending-post-session-evaluation"},
        "pass": None,
        "regression_status": "not-run",
        "termination_reason": "timeout" if process["timed_out"] else ("completed" if process["returncode"] == 0 else "process-exit"),
        "evaluator_notes": "Runner capture only; post-session evaluator must be run separately.",
        "evaluator_environment": evaluator_readiness,
        "invocation": {"command": command, "working_directory": str(workspace), "returncode": process["returncode"], "timed_out": process["timed_out"], "stdout_stderr": process["output"], "export_path": str(export_file) if export_file.exists() else None},
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
    identifier = parser.add_mutually_exclusive_group(required=True)
    identifier.add_argument("--run-id", help="frozen run ID, for example E001-C03-M")
    identifier.add_argument("--case-id", help="legacy case-only dry-run mode")
    parser.add_argument("--runs-manifest", type=Path, default=DEFAULT_RUN_MANIFEST)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--devin-binary", default="devin")
    parser.add_argument("--evaluator-env-root", type=Path, help="provisioned evaluator environment root; required for real frozen runs")
    parser.add_argument("--model")
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--execute", action="store_true", help="actually invoke Devin; requires --confirm-paid")
    parser.add_argument("--confirm-paid", action="store_true", help="explicitly acknowledge that an invocation may consume paid credits")
    args = parser.parse_args(argv)
    if args.confirm_paid and not args.execute:
        die("--confirm-paid requires --execute")
    config = read_json(args.config)
    run: Optional[Dict[str, Any]] = None
    if args.run_id:
        runs_manifest = read_json(args.runs_manifest)
        matches = [item for item in runs_manifest.get("runs", []) if item.get("run_id") == args.run_id]
        if len(matches) != 1:
            die(f"frozen run ID not found or duplicated: {args.run_id}")
        run = matches[0]
        expected_case_id = run.get("case_id")
        model = run.get("model")
        if not isinstance(model, str) or not isinstance(expected_case_id, str):
            die(f"invalid frozen run record: {args.run_id}")
    else:
        expected_case_id = args.case_id
        model = args.model or config["agent"]["model"]
    case = check_workspace(args.workspace)
    if case.get("case_id") != expected_case_id:
        die(f"workspace CASE.json is for {case.get('case_id')}, not {expected_case_id}")
    if args.model and args.model != model:
        die(f"model is frozen by the run manifest to {model}; refusing {args.model}")
    validate_model(config, model, expected=model if run else None)
    workspace = args.workspace.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    if output_dir == workspace or workspace in output_dir.parents:
        die("runner output must not be inside the agent workspace")
    if output_dir == REPO_ROOT:
        die("runner output must not be the control repository root")
    if output_dir.exists() and any(output_dir.iterdir()):
        die(f"runner output must be empty/fresh: {output_dir}")
    if not args.execute:
        output_dir.mkdir(parents=True, exist_ok=True)
        plan = plan_run(config, case, workspace, output_dir, args.devin_binary, model, run)
        plan_path = output_dir / "dry-run-plan.json"
        plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(plan, indent=2))
        return 0
    if not args.confirm_paid:
        die("refusing paid Devin invocation without --confirm-paid")
    if args.evaluator_env_root is None:
        die("--evaluator-env-root is required before a real frozen invocation")
    evaluator_readiness = evaluator_env.readiness(args.evaluator_env_root, expected_case_id)
    if evaluator_readiness["status"] != "pass":
        die("evaluator environment is not ready; refusing to launch Devin: " + "; ".join(evaluator_readiness["problems"]))
    result = execute_run(config, case, workspace, output_dir, args.devin_binary, model, args.timeout, run, evaluator_readiness)
    print(json.dumps(result, indent=2))
    return 0 if result["invocation"]["returncode"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
