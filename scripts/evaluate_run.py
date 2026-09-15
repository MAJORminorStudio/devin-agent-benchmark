#!/usr/bin/env python3
"""Evaluate one completed agent workspace without exposing evaluator ground truth.

Public tests run in the agent workspace. Optional hidden tests and a reference
patch are supplied only through evaluator-side paths after the agent session;
they are never copied into the agent workspace.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bugsinpy_harness as harness  # noqa: E402
import evaluator_environment as evaluator_env  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]


def die(message: str) -> None:
    raise SystemExit(f"error: {message}")


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def read_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        die(f"could not read JSON {path}: {exc}")
    if not isinstance(data, dict):
        die(f"expected JSON object in {path}")
    return data


def entry_map(root: Path) -> Dict[str, Tuple[str, bytes | str]]:
    entries: Dict[str, Tuple[str, bytes | str]] = {}
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            entries[rel] = ("symlink", os.readlink(path))
        elif path.is_file():
            entries[rel] = ("file", path.read_bytes())
    return entries


def patch_from_trees(baseline: Path, workspace: Path) -> Tuple[str, List[str], Dict[str, int]]:
    before = entry_map(baseline)
    after = entry_map(workspace)
    changed = sorted(set(before) | set(after))
    lines: List[str] = []
    changed_files: List[str] = []
    additions = deletions = 0
    for rel in changed:
        old = before.get(rel)
        new = after.get(rel)
        if old == new:
            continue
        changed_files.append(rel)
        if old and new and old[0] == "file" and new[0] == "file":
            old_bytes = old[1]
            new_bytes = new[1]
            assert isinstance(old_bytes, bytes) and isinstance(new_bytes, bytes)
            try:
                old_text = old_bytes.decode("utf-8").splitlines(keepends=True)
                new_text = new_bytes.decode("utf-8").splitlines(keepends=True)
            except UnicodeDecodeError:
                lines.append(f"Binary files a/{rel} and b/{rel} differ\n")
                continue
            diff = list(difflib.unified_diff(old_text, new_text, fromfile=f"a/{rel}", tofile=f"b/{rel}"))
            lines.extend(diff)
            additions += sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
            deletions += sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))
        elif old and old[0] == "file":
            lines.append(f"deleted file: {rel}\n")
            deletions += 1
        elif new and new[0] == "file":
            lines.append(f"new file: {rel}\n")
            additions += 1
        else:
            lines.append(f"symlink change: {rel}\n")
    return "".join(lines), changed_files, {"additions": additions, "deletions": deletions}


def fallback_git_patch(workspace: Path) -> Tuple[str, List[str], Dict[str, int]]:
    process = subprocess.run(
        ["git", "-C", str(workspace), "diff", "--no-ext-diff", "--binary", "HEAD"],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if process.returncode != 0:
        die(f"could not capture agent patch: {process.stderr.strip()}")
    status = subprocess.run(
        ["git", "-C", str(workspace), "status", "--short"],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    changed = [line[3:] for line in status.stdout.splitlines() if len(line) >= 4]
    additions = sum(1 for line in process.stdout.splitlines() if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in process.stdout.splitlines() if line.startswith("-") and not line.startswith("---"))
    return process.stdout, changed, {"additions": additions, "deletions": deletions}


def run_tests(
    commands: Sequence[str],
    cwd: Path,
    timeout: int,
    env: Optional[Mapping[str, str]] = None,
) -> Dict[str, Any]:
    return harness.execute_commands(commands, cwd, timeout, env=env)


def not_run_result(reason: str) -> Dict[str, Any]:
    return {"overall": "not-run", "commands": [], "reason": reason}


def evaluator_error_result(reason: str) -> Dict[str, Any]:
    return {"overall": "error", "commands": [], "error": reason}


def load_heldout_metadata(case: Mapping[str, Any], requested: Optional[Path]) -> Optional[Dict[str, Any]]:
    if requested is not None:
        path = requested.expanduser().resolve()
    elif case.get("heldout_test_files"):
        path = REPO_ROOT / "evaluation" / "experiment-001" / str(case["case_id"]) / "metadata.json"
    else:
        return None
    try:
        metadata = read_json(path)
    except SystemExit as exc:
        return {"_error": str(exc), "_path": str(path)}
    if metadata.get("case_id") != case.get("case_id"):
        return {"_error": f"held-out metadata case mismatch in {path}", "_path": str(path)}
    commands = metadata.get("heldout_commands")
    files = metadata.get("heldout_test_files")
    if not isinstance(commands, list) or not commands or not all(isinstance(item, str) for item in commands):
        return {"_error": f"held-out commands are missing or invalid in {path}", "_path": str(path)}
    if not isinstance(files, list) or not files or not all(isinstance(item, str) for item in files):
        return {"_error": f"held-out file list is missing or invalid in {path}", "_path": str(path)}
    base = path.parent
    for filename in files:
        candidate = (base / filename).resolve()
        try:
            candidate.relative_to(base.resolve())
        except ValueError:
            return {"_error": f"held-out test escapes metadata directory: {filename}", "_path": str(path)}
        if not candidate.is_file():
            return {"_error": f"held-out test is missing: {candidate}", "_path": str(path)}
    manifest_names = {Path(str(item)).name for item in case.get("heldout_test_files", [])}
    if manifest_names and not manifest_names.issubset({Path(item).name for item in files}):
        return {"_error": f"manifest and held-out metadata file lists disagree in {path}", "_path": str(path)}
    metadata["_path"] = str(path)
    metadata["_directory"] = str(base)
    return metadata


def host_evaluator_environment(workspace: Path) -> Dict[str, str]:
    environment = os.environ.copy()
    existing = environment.get("PYTHONPATH")
    paths = [str(workspace)]
    if existing:
        paths.append(existing)
    environment["PYTHONPATH"] = os.pathsep.join(paths)
    return environment


def score_evaluation(
    public_result: Mapping[str, Any],
    heldout_result: Mapping[str, Any],
    regression_result: Mapping[str, Any],
) -> Dict[str, Any]:
    """Apply the frozen success rule without treating not-run as success."""
    public_pass = public_result.get("overall") == "pass"
    heldout_pass = heldout_result.get("overall") == "pass"
    regression_pass = regression_result.get("overall") in ("pass", "not-run")
    evaluation_status = (
        "EVALUATION_ERROR"
        if heldout_result.get("overall") in ("error", "not-run")
        or regression_result.get("overall") == "error"
        else "OK"
    )
    task_success = public_pass and heldout_pass and regression_pass if evaluation_status == "OK" else None
    if evaluation_status == "EVALUATION_ERROR":
        regression_status = "inconclusive"
    elif regression_pass:
        regression_status = "clean"
    else:
        regression_status = "regression"
    return {
        "evaluation_status": evaluation_status,
        "task_success": task_success,
        "pass": task_success,
        "regression_status": regression_status,
    }


def reference_metrics(agent_patch: str, reference_patch: Path) -> Dict[str, Any]:
    # This comparison is intentionally limited to non-content metrics. The
    # reference patch never enters the agent workspace or result notes.
    reference_text = harness.read_text(reference_patch)
    agent_paths = {line[4:].split("\t", 1)[0] for line in agent_patch.splitlines() if line.startswith("+++ ")}
    reference_paths = {line[4:].split("\t", 1)[0] for line in reference_text.splitlines() if line.startswith("+++ ")}
    return {
        "reference_patch_checked_after_session": True,
        "reference_patch_path": str(reference_patch),
        "reference_file_count": len(reference_paths),
        "agent_file_count": len(agent_paths),
        "path_overlap_count": len(agent_paths & reference_paths),
    }


def load_case(manifest: Path, case_id: str) -> Dict[str, Any]:
    return harness.find_case(harness.load_manifest(manifest), case_id)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--baseline-dir", type=Path)
    parser.add_argument("--hidden-workspace", type=Path)
    parser.add_argument("--hidden-command", action="append", default=[])
    parser.add_argument("--heldout-metadata", type=Path)
    parser.add_argument("--reference-patch", type=Path)
    parser.add_argument("--env-root", type=Path, help="provisioned evaluator environment root")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args(argv)

    case = load_case(args.manifest, args.case_id)
    run_root = args.run_root.expanduser().resolve()
    workspace = args.workspace.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    if REPO_ROOT == workspace or REPO_ROOT in workspace.parents:
        die("agent workspace must be outside the control repository")
    if not workspace.is_dir():
        die(f"workspace not found: {workspace}")
    if output_dir == workspace or workspace in output_dir.parents:
        die("evaluation output must not be inside the agent workspace")

    evaluator_readiness: Optional[Dict[str, Any]] = None
    if case.get("heldout_test_files"):
        if args.env_root is None:
            die("--env-root is required for frozen cases with held-out evaluation")
        try:
            evaluator_readiness = evaluator_env.require_ready(args.env_root, case["case_id"])
        except RuntimeError as exc:
            die(str(exc))
        evaluation_environment = evaluator_env.process_environment(
            args.env_root, case["case_id"], workspace=workspace
        )
    else:
        evaluation_environment = host_evaluator_environment(workspace)
    output_dir.mkdir(parents=True, exist_ok=True)

    runner_record_path = output_dir / "runner-result.json"
    runner_record = read_json(runner_record_path) if runner_record_path.is_file() else {}

    audit_path = workspace.parent / f"{workspace.name}.leak-audit.json"
    if not audit_path.is_file() or read_json(audit_path).get("status") != "pass":
        die("a passing exporter leak audit is required before evaluation")

    baseline = args.baseline_dir.expanduser().resolve() if args.baseline_dir else workspace.parent / f"{workspace.name}.baseline"
    if baseline.is_dir():
        patch_text, changed_files, patch_counts = patch_from_trees(baseline, workspace)
    elif (workspace / ".git").is_dir():
        patch_text, changed_files, patch_counts = fallback_git_patch(workspace)
    else:
        die(f"baseline directory is required for a workspace without .git: {baseline}")

    patch_path = output_dir / "agent.patch"
    patch_path.write_text(patch_text, encoding="utf-8")
    patch_sha = hashlib.sha256(patch_text.encode("utf-8")).hexdigest()
    before_path = run_root / "reproducibility.json"
    tests_before = read_json(before_path) if before_path.is_file() else {"status": "not-recorded"}
    tests_after = run_tests(case["test_command"], workspace, args.timeout, env=evaluation_environment)

    heldout_metadata = load_heldout_metadata(case, args.heldout_metadata)
    hidden_result: Dict[str, Any]
    if args.hidden_command:
        if not args.hidden_workspace:
            die("--hidden-workspace is required when hidden tests are requested")
        hidden_workspace = args.hidden_workspace.expanduser().resolve()
        if hidden_workspace == workspace or workspace in hidden_workspace.parents:
            die("hidden evaluator workspace must be separate from the agent workspace")
        if not hidden_workspace.is_dir():
            die(f"hidden evaluator workspace not found: {hidden_workspace}")
        hidden_result = run_tests(
            args.hidden_command,
            hidden_workspace,
            args.timeout,
            env=evaluation_environment,
        )
    elif heldout_metadata is None:
        hidden_result = not_run_result("no held-out suite configured")
    elif "_error" in heldout_metadata:
        hidden_result = evaluator_error_result(str(heldout_metadata["_error"]))
    else:
        hidden_workspace = Path(str(heldout_metadata["_directory"])).resolve()
        if hidden_workspace == workspace or workspace in hidden_workspace.parents:
            hidden_result = evaluator_error_result("held-out evaluator directory overlaps agent workspace")
        else:
            hidden_result = run_tests(
                [str(command) for command in heldout_metadata["heldout_commands"]],
                hidden_workspace,
                args.timeout,
                env=evaluation_environment,
            )

    regression_result: Dict[str, Any] = not_run_result("no regression suite configured")
    if heldout_metadata and "_error" not in heldout_metadata:
        regression_commands = heldout_metadata.get("regression_commands", [])
        if not isinstance(regression_commands, list) or not all(isinstance(item, str) for item in regression_commands):
            regression_result = evaluator_error_result("regression command list is invalid")
        elif regression_commands:
            regression_result = run_tests(regression_commands, workspace, args.timeout, env=evaluation_environment)

    reference: Dict[str, Any] = {"reference_patch_checked_after_session": False}
    if args.reference_patch:
        reference_path = args.reference_patch.expanduser().resolve()
        if not reference_path.is_file() or is_agent_visible(reference_path, workspace):
            die("reference patch must be a separate evaluator-side file")
        reference = reference_metrics(patch_text, reference_path)

    score = score_evaluation(tests_after, hidden_result, regression_result)
    overall_pass = score["task_success"]

    runner_agent = runner_record.get("agent") if isinstance(runner_record.get("agent"), dict) else {}
    result = {
        "experiment_id": "experiment-001",
        "experiment_case_id": case.get("experiment_case_id"),
        "case_id": case["case_id"],
        "run_id": runner_record.get("run_id"),
        "condition": runner_record.get("condition"),
        "effort_level": runner_record.get("effort_level"),
        "agent": runner_agent or {"name": "Devin", "configuration": "see runner-result.json", "model": "recorded by runner", "subscription_or_usage": {"available": False, "amount": None, "currency": None}},
        "prompt": (workspace / "TASK.md").read_text(encoding="utf-8"),
        "started_at": runner_record.get("started_at"),
        "ended_at": runner_record.get("ended_at", utc_now()),
        "elapsed_seconds": runner_record.get("elapsed_seconds"),
        "steps": runner_record.get("steps"),
        "interventions": runner_record.get("interventions", []),
        "patch": {"format": "unified-diff", "path": str(patch_path), "sha256": patch_sha, "changed_files": changed_files, "line_counts": patch_counts},
        "tests_before": tests_before,
        "tests_after": tests_after,
        "hidden_tests": hidden_result,
        "heldout_tests": hidden_result,
        "regression_tests": regression_result,
        "evaluation_status": score["evaluation_status"],
        "task_success": overall_pass,
        "pass": overall_pass,
        "regression_status": score["regression_status"],
        "termination_reason": runner_record.get("termination_reason") or ("timeout" if runner_record.get("invocation", {}).get("timed_out") else None),
        "evaluator_notes": "Evaluator-side result. Reference patch and hidden tests, when supplied, were not copied into the agent workspace.",
        "evaluator_environment": evaluator_readiness,
        "reference_comparison": reference,
    }
    result_path = output_dir / "evaluation-result.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if score["evaluation_status"] == "EVALUATION_ERROR":
        return 2
    return 0 if overall_pass else 1


def is_agent_visible(path: Path, workspace: Path) -> bool:
    try:
        path.relative_to(workspace)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
