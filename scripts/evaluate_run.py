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


def run_tests(commands: Sequence[str], cwd: Path, timeout: int) -> Dict[str, Any]:
    return harness.execute_commands(commands, cwd, timeout)


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
    parser.add_argument("--reference-patch", type=Path)
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
    tests_after = run_tests(case["test_command"], workspace, args.timeout)

    hidden_result: Dict[str, Any] = {"overall": "not-run", "commands": []}
    if args.hidden_command:
        if not args.hidden_workspace:
            die("--hidden-workspace is required when hidden tests are requested")
        hidden_workspace = args.hidden_workspace.expanduser().resolve()
        if hidden_workspace == workspace or workspace in hidden_workspace.parents:
            die("hidden evaluator workspace must be separate from the agent workspace")
        if not hidden_workspace.is_dir():
            die(f"hidden evaluator workspace not found: {hidden_workspace}")
        hidden_result = run_tests(args.hidden_command, hidden_workspace, args.timeout)

    reference: Dict[str, Any] = {"reference_patch_checked_after_session": False}
    if args.reference_patch:
        reference_path = args.reference_patch.expanduser().resolve()
        if not reference_path.is_file() or is_agent_visible(reference_path, workspace):
            die("reference patch must be a separate evaluator-side file")
        reference = reference_metrics(patch_text, reference_path)

    public_pass = tests_after.get("overall") == "pass"
    hidden_pass = hidden_result.get("overall") in ("pass", "not-run")
    overall_pass = public_pass and hidden_pass
    if hidden_result.get("overall") == "not-run":
        regression_status = "not-run" if not public_pass else "inconclusive"
    elif overall_pass:
        regression_status = "clean"
    elif public_pass:
        regression_status = "regression"
    else:
        regression_status = "inconclusive"

    runner_agent = runner_record.get("agent") if isinstance(runner_record.get("agent"), dict) else {}
    result = {
        "experiment_id": "experiment-001",
        "experiment_case_id": case.get("experiment_case_id"),
        "case_id": case["case_id"],
        "agent": runner_agent or {"name": "Devin", "configuration": "see runner-result.json", "model": "recorded by runner", "subscription_or_usage": {"available": False, "amount": None, "currency": None}},
        "prompt": (workspace / "TASK.md").read_text(encoding="utf-8"),
        "started_at": runner_record.get("started_at"),
        "ended_at": runner_record.get("ended_at", utc_now()),
        "elapsed_seconds": runner_record.get("elapsed_seconds"),
        "interventions": runner_record.get("interventions", []),
        "patch": {"format": "unified-diff", "path": str(patch_path), "sha256": patch_sha, "changed_files": changed_files, "line_counts": patch_counts},
        "tests_before": tests_before,
        "tests_after": tests_after,
        "hidden_tests": hidden_result,
        "pass": overall_pass,
        "regression_status": regression_status,
        "evaluator_notes": "Evaluator-side result. Reference patch and hidden tests, when supplied, were not copied into the agent workspace.",
        "reference_comparison": reference,
    }
    result_path = output_dir / "evaluation-result.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if overall_pass else 1


def is_agent_visible(path: Path, workspace: Path) -> bool:
    try:
        path.relative_to(workspace)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
