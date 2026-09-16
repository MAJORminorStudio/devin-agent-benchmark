#!/usr/bin/env python3
"""Validate E006 ground truth, determinism, workspace isolation, and freeze inputs.

This validator executes only local public/held-out ground-truth tests against
prepared buggy/fixed trees. It never invokes Devin, SWE-2, Docker, a paid
runner, or an agent-produced workspace.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = REPO_ROOT / ".benchmarks" / "private-run"
CASES_ROOT = PRIVATE_ROOT / "cases"
HISTORICAL_ROOT = PRIVATE_ROOT / "historical-cases"
EVALUATION_ROOT = PRIVATE_ROOT / "evaluation"
PATCH_ROOT = PRIVATE_ROOT / "reference-patches"
RESULT_ROOT = PRIVATE_ROOT / "results"
WORKSPACE_ROOT = PRIVATE_ROOT / "run-workspaces"
CONFIG_PATH = REPO_ROOT / "manifests" / "experiment-006-config.json"
RUNS_PATH = REPO_ROOT / "manifests" / "experiment-006-runs.json"
HIST_MANIFEST_PATH = PRIVATE_ROOT / "historical-manifest.json"
VENV_BIN = PRIVATE_ROOT.parent / "private-run" / "venv-py38" / "bin"

IGNORED_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
FORBIDDEN_NAMES = {
    ".git", "bug.info", "bug_patch.txt", "bug_buggy.txt", "bug_fixed.txt",
    "bugsinpy_bug.info", "bugsinpy_patchfile.info", "bugsinpy_fail.txt",
    "bugsinpy_alltest.txt", "test_behavior.py", "test_regression.py",
    "credentials.toml",
}
FORBIDDEN_TEXT = (
    b"private-run", b"swe-2", b"devin", b"reference-patch",
    b"fixed_commit", b"bug_patch", b"held-out evaluator",
)


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def load_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read JSON {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"expected JSON object: {path}")
    return value


def hash_tree(root: Path) -> str:
    digest = hashlib.sha256()
    if not root.is_dir():
        fail(f"missing tree: {root}")
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in IGNORED_PARTS for part in relative.parts):
            continue
        if path.is_file():
            digest.update(str(relative).encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    return digest.hexdigest()


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hash_paths(root: Path, paths: Iterable[Path]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(paths):
        path = root / relative
        if not path.is_file():
            fail(f"missing hash input: {path}")
        digest.update(str(relative).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def tree_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_file() and not any(part in IGNORED_PARTS for part in relative.parts):
            yield path


def run_command(command: str, cwd: Path, env: Mapping[str, str], timeout: int = 300) -> Dict[str, Any]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            env=dict(env),
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
        output = completed.stdout or ""
        returncode = completed.returncode
        status = "pass" if returncode == 0 else "fail"
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        returncode = 124
        status = "error"
        timed_out = True
    return {
        "command": command,
        "returncode": returncode,
        "status": status,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "output_tail": output[-3000:],
        "timed_out": timed_out,
    }


def environment(root: Path) -> Dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{VENV_BIN}:{env.get('PATH', '')}"
    env["PYTHONPATH"] = str(root / "src") if (root / "src").is_dir() else str(root)
    return env


def historical_case_map(manifest: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    return {str(case["case_id"]): case for case in manifest["cases"]}


def public_commands(case_id: str, root: Path, hist_case: Mapping[str, Any] | None) -> List[str]:
    if hist_case is not None:
        return [str(command) for command in hist_case["test_command"]]
    return ["python -m unittest discover -s tests -v"]


def evaluation_commands(case_id: str) -> Tuple[List[str], List[str]]:
    behavior = EVALUATION_ROOT / case_id / "test_behavior.py"
    regression = EVALUATION_ROOT / case_id / "test_regression.py"
    if not behavior.is_file() or not regression.is_file():
        fail(f"missing private evaluator for {case_id}")
    return (
        [f"python -m pytest -q {behavior}"],
        [f"python -m pytest -q {regression}"],
    )


def verify_side(
    case_id: str,
    side: str,
    config_case: Mapping[str, Any],
    hist_case: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    if hist_case is not None:
        root = HISTORICAL_ROOT / case_id / "verification" / side
    else:
        root = CASES_ROOT / case_id / side
    env = environment(root)
    public = [run_command(c, root, env) for c in public_commands(case_id, root, hist_case)]
    behavior_commands, regression_commands = evaluation_commands(case_id)
    behavior = [run_command(c, root, env) for c in behavior_commands]
    regression = [run_command(c, root, env) for c in regression_commands]
    groups = {"public": public, "held_out": behavior, "regression": regression}
    statuses = {name: ("pass" if all(item["status"] == "pass" for item in items) else ("error" if any(item["status"] == "error" for item in items) else "fail")) for name, items in groups.items()}
    return {
        "case_id": case_id,
        "side": side,
        "root": str(root),
        "groups": groups,
        "statuses": statuses,
        "signature": {
            name: [item["status"] + ":" + str(item["returncode"]) for item in items]
            for name, items in groups.items()
        },
    }


def expected_matrix_ok(matrix: Mapping[str, Any]) -> None:
    for case_id, sides in matrix.items():
        fixed = sides["fixed"]["statuses"]
        if any(fixed[group] != "pass" for group in ("public", "held_out", "regression")):
            fail(f"fixed ground truth is not green for {case_id}: {fixed}")
        buggy = sides["buggy"]["statuses"]
        for group in ("public", "held_out"):
            if buggy[group] != "fail":
                fail(f"buggy {group} does not fail for {case_id}: {buggy}")


def write_reference_patch(case_id: str, hist_case: Mapping[str, Any] | None) -> Path:
    destination = PATCH_ROOT / f"{case_id}.patch"
    PATCH_ROOT.mkdir(parents=True, exist_ok=True)
    if hist_case is not None:
        repo = HISTORICAL_ROOT / case_id / "ground-truth-repo-cache"
        result = subprocess.run(
            ["git", "-C", str(repo), "diff", "--no-ext-diff", hist_case["buggy_commit"], hist_case["fixed_commit"], "--"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode not in (0, 1):
            fail(f"could not create historical reference patch for {case_id}: {result.stderr.decode(errors='replace')}")
        content = result.stdout
    else:
        buggy = CASES_ROOT / case_id / "buggy"
        fixed = CASES_ROOT / case_id / "fixed"
        lines: List[str] = []
        relative_paths = sorted({p.relative_to(buggy) for p in tree_files(buggy)} | {p.relative_to(fixed) for p in tree_files(fixed)})
        for relative in relative_paths:
            if relative.parts[-1] in {"README.md", "pyproject.toml"} or "tests" in relative.parts:
                continue
            before = (buggy / relative).read_text(encoding="utf-8") if (buggy / relative).is_file() else ""
            after = (fixed / relative).read_text(encoding="utf-8") if (fixed / relative).is_file() else ""
            if before != after:
                lines.extend(difflib.unified_diff(
                    before.splitlines(keepends=True), after.splitlines(keepends=True),
                    fromfile=f"a/{relative}", tofile=f"b/{relative}",
                ))
        content = "".join(lines).encode("utf-8")
    destination.write_bytes(content)
    return destination


def audit_workspace(workspace: Path, fixed_tree: Path) -> List[str]:
    problems: List[str] = []
    if not workspace.is_dir():
        return ["workspace missing"]
    fixed_commit = b""
    metadata = fixed_tree.parent / "metadata" / "bug.info"
    if metadata.is_file():
        fixed_commit = re.search(rb'fixed_commit_id="([0-9a-f]+)"', metadata.read_bytes()).group(1) if re.search(rb'fixed_commit_id="([0-9a-f]+)"', metadata.read_bytes()) else b""
    for path in tree_files(workspace):
        relative = path.relative_to(workspace)
        if path.name in FORBIDDEN_NAMES:
            problems.append(f"forbidden artifact: {relative}")
        data = path.read_bytes()
        lowered = data.lower()
        if fixed_commit and fixed_commit in data:
            problems.append(f"fixed commit hash present: {relative}")
        for token in FORBIDDEN_TEXT:
            if token in lowered:
                problems.append(f"forbidden text {token.decode()} present: {relative}")
    return problems


def build_run_workspaces(runs: Sequence[Mapping[str, Any]], config_cases: Mapping[str, Mapping[str, Any]]) -> List[Dict[str, Any]]:
    if WORKSPACE_ROOT.exists():
        for child in WORKSPACE_ROOT.iterdir():
            if child.is_dir() and child.parent == WORKSPACE_ROOT:
                shutil.rmtree(child)
            elif child.is_file() or child.is_symlink():
                child.unlink()
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    audits: List[Dict[str, Any]] = []
    for run in runs:
        run_id = str(run["run_id"])
        case_id = str(run["case_id"])
        if case_id.startswith("E006-K"):
            template = HISTORICAL_ROOT / case_id / "agent-workspace"
            fixed_tree = HISTORICAL_ROOT / case_id / "verification" / "fixed"
        else:
            template = CASES_ROOT / case_id / "buggy"
            fixed_tree = CASES_ROOT / case_id / "fixed"
        workspace = WORKSPACE_ROOT / run_id
        shutil.copytree(template, workspace, symlinks=True)
        prompt_path = REPO_ROOT / str(config_cases[case_id]["prompt"])
        (workspace / "TASK.md").write_bytes(prompt_path.read_bytes())
        problems = audit_workspace(workspace, fixed_tree)
        audits.append({
            "run_id": run_id,
            "case_id": case_id,
            "condition": run["condition"],
            "workspace_sha256": hash_tree(workspace),
            "status": "pass" if not problems else "fail",
            "problems": problems,
        })
    return audits


def static_security_checks() -> Dict[str, Any]:
    public_files = [
        CONFIG_PATH, RUNS_PATH, REPO_ROOT / "scripts" / "experiment_006_container.py",
        REPO_ROOT / "scripts" / "validate_experiment_006.py",
        REPO_ROOT / "scripts" / "validate_experiment_006_runtime.py",
    ] + sorted((REPO_ROOT / "prompts" / "experiment-006").glob("*.md"))
    for path in public_files:
        if path.suffix == ".json":
            load_json(path)
        if path.suffix == ".py":
            result = subprocess.run([sys.executable, "-m", "py_compile", str(path)], check=False)
            if result.returncode != 0:
                fail(f"syntax check failed: {path}")
    scan_files = [path for path in public_files if path.is_file() and path.name != "validate_experiment_006.py"]
    public_text = b"".join(path.read_bytes() for path in scan_files)
    secret_patterns = [rb"AKIA[0-9A-Z]{16}", rb"gh[pousr]_[A-Za-z0-9]{20,}", rb"-----BEGIN .*PRIVATE KEY-----"]
    if any(re.search(pattern, public_text) for pattern in secret_patterns):
        fail("secret-like material found in public freeze inputs")
    runner_text = (REPO_ROOT / "scripts" / "experiment_006_container.py").read_text(encoding="utf-8")
    required_fragments = [
        '"--read-only"', '"--cap-drop", "ALL"', '"no-new-privileges:true"',
        '"--pids-limit"', '"--network"', '"--platform", "linux/arm64"',
        'if args.execute and not args.confirm_paid:',
        '"LD_LIBRARY_PATH="', '"E006_CASE_ID="',
    ]
    missing = [fragment for fragment in required_fragments if fragment not in runner_text]
    if missing:
        fail("container security guard missing: " + ", ".join(missing))
    status = subprocess.run(["git", "diff", "--name-only", "HEAD"], stdout=subprocess.PIPE, text=True, check=False)
    protected = [line for line in status.stdout.splitlines() if re.search(r"experiment-00[1-5]|v[123]", line)]
    if protected:
        fail("protected prior experiment path changed: " + ", ".join(protected))
    return {"json": "pass", "python_syntax": "pass", "secret_scan": "pass", "container_security": "pass", "protected_history": "pass"}


def main() -> int:
    config = load_json(CONFIG_PATH)
    runs_manifest = load_json(RUNS_PATH)
    hist_manifest = load_json(HIST_MANIFEST_PATH)
    config_cases = {str(case["experiment_case_id"]): case for case in config["cases"]}
    hist_cases = historical_case_map(hist_manifest)
    cases = [str(case["experiment_case_id"]) for case in config["cases"]]
    if set(cases) != set(config_cases) or len(cases) != 10:
        fail("configuration case set is not exactly ten unique cases")
    runs = runs_manifest["runs"]
    if len(runs) != 20 or len({run["run_id"] for run in runs}) != 20:
        fail("run manifest is not exactly twenty unique runs")
    if {run["condition"] for run in runs} != {"M", "X"}:
        fail("run manifest does not contain both conditions")
    if sum(run["condition"] == "M" for run in runs) != 10 or sum(run["condition"] == "X" for run in runs) != 10:
        fail("run manifest is not balanced")
    for case_id in cases:
        if case_id not in hist_cases and not case_id.startswith("E006-H"):
            fail(f"missing historical manifest entry: {case_id}")
        conditions = {run["condition"] for run in runs if run["case_id"] == case_id}
        if conditions != {"M", "X"}:
            fail(f"case does not have one run at each condition: {case_id}")

    matrix: Dict[str, Any] = {}
    for repetition in (1, 2):
        current: Dict[str, Any] = {}
        for case_id in cases:
            current[case_id] = {
                "buggy": verify_side(case_id, "buggy", config_cases[case_id], hist_cases.get(case_id)),
                "fixed": verify_side(case_id, "fixed", config_cases[case_id], hist_cases.get(case_id)),
            }
            if repetition == 1:
                matrix[case_id] = current[case_id]
        if repetition == 1:
            first_signature = {case_id: {side: value[side]["signature"] for side in ("buggy", "fixed")} for case_id, value in current.items()}
        else:
            second_signature = {case_id: {side: value[side]["signature"] for side in ("buggy", "fixed")} for case_id, value in current.items()}
    expected_matrix_ok(matrix)
    if first_signature != second_signature:
        fail("ground-truth repeat is not deterministic")

    for case_id in cases:
        write_reference_patch(case_id, hist_cases.get(case_id))
    audits = build_run_workspaces(runs, config_cases)
    if len(audits) != 20 or any(item["status"] != "pass" for item in audits):
        fail("one or more run workspace leak audits failed")
    prompt_hashes = {}
    for case_id in cases:
        prompt = REPO_ROOT / str(config_cases[case_id]["prompt"])
        prompt_hashes[case_id] = hash_file(prompt)
    case_hashes: Dict[str, Dict[str, str]] = {}
    audit_by_case = {case_id: next(item for item in audits if item["case_id"] == case_id) for case_id in cases}
    for case_id in cases:
        if case_id.startswith("E006-K"):
            source_root = HISTORICAL_ROOT / case_id / "verification"
            buggy_tree = source_root / "buggy"
            fixed_tree = source_root / "fixed"
            configured_tests = [Path(item) for item in config_cases[case_id].get("test_files", [])]
            public_hash = hash_paths(buggy_tree, configured_tests)
        else:
            source_root = CASES_ROOT / case_id
            buggy_tree = source_root / "buggy"
            fixed_tree = source_root / "fixed"
            public_hash = hash_tree(buggy_tree / "tests")
        case_hashes[case_id] = {
            "buggy_tree_sha256": hash_tree(buggy_tree),
            "fixed_tree_sha256": hash_tree(fixed_tree),
            "reference_patch_sha256": hash_file(PATCH_ROOT / f"{case_id}.patch"),
            "public_test_sha256": public_hash,
            "heldout_test_sha256": hash_file(EVALUATION_ROOT / case_id / "test_behavior.py"),
            "regression_test_sha256": hash_file(EVALUATION_ROOT / case_id / "test_regression.py"),
            "prompt_sha256": prompt_hashes[case_id],
            "agent_workspace_sha256": audit_by_case[case_id]["workspace_sha256"],
        }
    security = static_security_checks()
    result_root = RESULT_ROOT
    result_root.mkdir(parents=True, exist_ok=True)
    compact_matrix = {
        case_id: {
            side: {
                "statuses": value[side]["statuses"],
                "signature": value[side]["signature"],
            }
            for side in ("buggy", "fixed")
        }
        for case_id, value in matrix.items()
    }
    ground_truth = {
        "experiment_id": "experiment-006",
        "validator_version": "private-run-validator-v1",
        "agent_invocations": 0,
        "swe2_invocations": 0,
        "repetitions": 2,
        "deterministic": True,
        "matrix": compact_matrix,
        "repeat_signature": first_signature,
    }
    (result_root / "ground-truth.json").write_text(json.dumps(ground_truth, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    deterministic_result = {
        "experiment_id": "experiment-006",
        "repetitions": 2,
        "signature": first_signature,
        "deterministic": first_signature == second_signature,
    }
    (result_root / "deterministic-repeat.json").write_text(
        json.dumps(deterministic_result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (result_root / "leak-audits.json").write_text(json.dumps({"count": len(audits), "audits": audits}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for case_id in cases:
        config_cases[case_id]["_private_prompt_sha256"] = prompt_hashes[case_id]
    summary = {
        "experiment_id": "experiment-006",
        "status": "pass",
        "agent_invocations": 0,
        "swe2_invocations": 0,
        "case_count": 10,
        "run_count": 20,
        "ground_truth": "pass",
        "deterministic_repeat": "pass",
        "run_workspace_audits": len(audits),
        "run_workspace_audits_passed": sum(item["status"] == "pass" for item in audits),
        "prompt_pairs_identical": True,
        "prompt_sha256": prompt_hashes,
        "reference_patch_sha256": {case_id: hash_file(PATCH_ROOT / f"{case_id}.patch") for case_id in cases},
        "deterministic_result_sha256": hash_file(result_root / "deterministic-repeat.json"),
        "case_hashes": case_hashes,
        "security_checks": security,
    }
    (result_root / "validation-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
