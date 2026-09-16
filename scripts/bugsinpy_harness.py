#!/usr/bin/env python3
"""Isolated BugsInPy preparation and verification harness.

The evaluator manifest and the fixed checkout are never copied into the agent
workspace. The agent workspace is produced from a single buggy git archive,
with only the BugsInPy regression-test files overlaid from the fixed revision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://github.com/reproducing-research-projects/BugsInPy.git"
SOURCE_COMMIT = "316b95e2353ecda832bad9b42f86fa7c2fcec8ac"
FORBIDDEN_AGENT_NAMES = {
    ".git",
    "bug.info",
    "bug_patch.txt",
    "bug_buggy.txt",
    "bug_fixed.txt",
    "bugsinpy_bug.info",
    "bugsinpy_patchfile.info",
    "bugsinpy_fail.txt",
    "bugsinpy_alltest.txt",
}


def die(message: str) -> None:
    raise SystemExit(f"error: {message}")


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def require_external_source(source_dir: Path) -> Path:
    source = source_dir.expanduser().resolve()
    if is_within(source, REPO_ROOT):
        die(f"BugsInPy source must be outside this repository: {source}")
    if not (source / ".git").is_dir():
        die(f"not a git checkout: {source}")
    return source


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "utf-8"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def parse_info(path: Path) -> Dict[str, str]:
    text = read_text(path)
    return {
        key: value
        for key, value in re.findall(
            r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\"([^\"]*)\"", text
        )
    }


def parse_test_files(value: str) -> List[str]:
    paths = [item.strip() for item in value.split(";") if item.strip()]
    for item in paths:
        candidate = Path(item)
        if candidate.is_absolute() or ".." in candidate.parts:
            die(f"unsafe test path in BugsInPy metadata: {item}")
    return paths


def load_manifest(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        die(f"invalid JSON manifest {path}: {exc}")
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        die("manifest must be an object with a cases array")
    required = {
        "case_id", "source", "project", "bug_id", "buggy_commit", "fixed_commit",
        "test_command", "expected_buggy_result", "expected_fixed_result",
        "task_prompt", "difficulty", "status",
    }
    for case in data["cases"]:
        if not isinstance(case, dict):
            die("each manifest case must be an object")
        missing = sorted(required - set(case))
        if missing:
            die(f"case {case.get('case_id', '<unknown>')} missing: {', '.join(missing)}")
        if not isinstance(case["test_command"], list) or not case["test_command"]:
            die(f"case {case['case_id']} must have a non-empty test_command array")
        if case["source"] != "BugsInPy":
            die(f"unsupported source for {case['case_id']}: {case['source']}")
    return data


def find_case(manifest: Mapping[str, Any], case_id: str) -> Dict[str, Any]:
    matches = [case for case in manifest["cases"] if case.get("case_id") == case_id]
    if len(matches) != 1:
        die(f"case not found or duplicated: {case_id}")
    return dict(matches[0])


def run_command(
    args: Sequence[str],
    cwd: Path,
    *,
    check: bool = True,
    stdout: Any = subprocess.PIPE,
) -> subprocess.CompletedProcess:
    result = subprocess.run(
        args, cwd=str(cwd), check=False, text=True, stdout=stdout, stderr=subprocess.PIPE
    )
    if check and result.returncode != 0:
        detail = (result.stderr or "").strip()
        die(f"command failed ({result.returncode}): {' '.join(args)}\n{detail}")
    return result


def git_output(repo: Path, *args: str) -> str:
    result = run_command(["git", "-C", str(repo), *args], repo, check=True)
    return (result.stdout or "").strip()


def clone_project(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        die(f"refusing to overwrite existing repository cache: {dest}")
    first = subprocess.run(
        ["git", "clone", "--filter=blob:none", "--no-checkout", "--no-tags", url, str(dest)],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if first.returncode == 0:
        return dest
    if dest.exists():
        shutil.rmtree(dest)
    second = subprocess.run(
        ["git", "clone", "--no-checkout", "--no-tags", url, str(dest)],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if second.returncode != 0:
        die(f"could not clone {url}: {(second.stderr or first.stderr).strip()}")
    return dest


def extract_git_archive(
    repo: Path, commit: str, dest: Path, paths: Optional[Sequence[str]] = None
) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    args = ["git", "-C", str(repo), "archive", commit]
    if paths:
        args.extend(["--", *paths])
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert process.stdout is not None
    try:
        with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
            for member in archive:
                target = (dest / member.name).resolve()
                if not is_within(target, dest):
                    die(f"archive contains unsafe path: {member.name}")
                archive.extract(member, path=str(dest), set_attrs=True)
    finally:
        process.stdout.close()
    stderr = process.stderr.read().decode("utf-8", errors="replace") if process.stderr else ""
    return_code = process.wait()
    if return_code != 0:
        die(f"git archive failed for {commit}: {stderr.strip()}")


def copy_metadata(source: Path, case: Mapping[str, Any], run_root: Path, info: Mapping[str, str]) -> None:
    metadata = run_root / "metadata"
    metadata.mkdir(parents=True, exist_ok=True)
    (metadata / "case.json").write_text(
        json.dumps(case, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    bug_dir = source / "projects" / case["project"] / "bugs" / str(case["bug_id"])
    (metadata / "bug.info").write_text(read_text(bug_dir / "bug.info"), encoding="utf-8")
    for name in ("requirements.txt", "setup.sh", "run_test.sh"):
        original = bug_dir / name
        if original.exists():
            (metadata / name).write_text(read_text(original), encoding="utf-8")
    project_info = source / "projects" / case["project"] / "project.info"
    (metadata / "source-project.info").write_text(read_text(project_info), encoding="utf-8")
    (metadata / "parsed-info.json").write_text(
        json.dumps(dict(info), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def audit_agent_workspace(agent: Path, fixed_commit: str) -> List[str]:
    problems: List[str] = []
    if (agent / ".git").exists():
        problems.append(".git history is present")
    if not agent.is_dir():
        problems.append("agent workspace is missing")
        return problems
    for path in agent.rglob("*"):
        if path.name in FORBIDDEN_AGENT_NAMES:
            problems.append(f"forbidden artifact: {path.relative_to(agent)}")
        if path.is_file():
            try:
                content = path.read_bytes()
            except OSError:
                continue
            if fixed_commit.encode("ascii") in content:
                problems.append(f"fixed commit hash present in: {path.relative_to(agent)}")
    return problems


def prepare_case(
    manifest: Mapping[str, Any],
    case: Mapping[str, Any],
    source_dir: Path,
    work_root: Path,
    force: bool,
) -> Path:
    del manifest  # Kept in the function signature to make the provenance explicit.
    source = require_external_source(source_dir)
    actual_source_commit = git_output(source, "rev-parse", "HEAD")
    expected_source_commit = case.get("source_commit", SOURCE_COMMIT)
    if actual_source_commit != expected_source_commit:
        die(f"unexpected BugsInPy source commit: {actual_source_commit}; expected {expected_source_commit}")
    bug_dir = source / "projects" / case["project"] / "bugs" / str(case["bug_id"])
    project_info_path = source / "projects" / case["project"] / "project.info"
    if not bug_dir.is_dir() or not project_info_path.is_file():
        die(f"BugsInPy case metadata not found: {case['project']}-{case['bug_id']}")
    info = parse_info(bug_dir / "bug.info")
    expected = {"buggy_commit_id": case["buggy_commit"], "fixed_commit_id": case["fixed_commit"]}
    for key, value in expected.items():
        if info.get(key) != value:
            die(f"manifest/source mismatch for {case['case_id']}: {key}")
    test_files = parse_test_files(info.get("test_file", ""))
    if not test_files:
        die(f"no test files in BugsInPy metadata for {case['case_id']}")
    if case.get("test_files") and case["test_files"] != test_files:
        die(f"manifest/source mismatch for {case['case_id']}: test_files")
    url = parse_info(project_info_path).get("github_url")
    if not url:
        die(f"no github_url for {case['project']}")

    case_root = (work_root / case["case_id"]).resolve()
    work_root_resolved = work_root.resolve()
    if case_root.exists():
        if not force:
            die(f"run root exists; choose another work root or pass --force: {case_root}")
        if not is_within(case_root, work_root_resolved) or case_root == work_root_resolved:
            die("refusing unsafe --force target")
        shutil.rmtree(case_root)
    case_root.mkdir(parents=True, exist_ok=False)
    repo_cache = case_root / "ground-truth-repo-cache"
    repo = clone_project(url, repo_cache)
    run_command(["git", "-C", str(repo), "cat-file", "-e", f"{case['buggy_commit']}^{{commit}}"], repo)
    run_command(["git", "-C", str(repo), "cat-file", "-e", f"{case['fixed_commit']}^{{commit}}"], repo)

    verification_buggy = case_root / "verification" / "buggy"
    verification_fixed = case_root / "verification" / "fixed"
    agent = case_root / "agent-workspace"
    extract_git_archive(repo, case["buggy_commit"], verification_buggy)
    extract_git_archive(repo, case["fixed_commit"], verification_fixed)
    extract_git_archive(repo, case["buggy_commit"], agent)
    # Tests are regression oracles, not implementation files. Only these paths
    # are copied from the fixed revision into the buggy and agent workspaces.
    extract_git_archive(repo, case["fixed_commit"], verification_buggy, test_files)
    extract_git_archive(repo, case["fixed_commit"], agent, test_files)
    copy_metadata(source, case, case_root, info)
    (case_root / "README.agent-workspace.txt").write_text(
        "Only agent-workspace/ is intended for an autonomous agent.\n"
        "The sibling verification/fixed tree and metadata are evaluator-only.\n",
        encoding="utf-8",
    )
    problems = audit_agent_workspace(agent, case["fixed_commit"])
    if problems:
        die("agent workspace safeguard failed: " + "; ".join(problems))
    digest = hashlib.sha256()
    for path in sorted(p for p in agent.rglob("*") if p.is_file()):
        digest.update(str(path.relative_to(agent)).encode())
        digest.update(path.read_bytes())
    record = {
        "case_id": case["case_id"],
        "prepared_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "buggy_commit": case["buggy_commit"],
        "fixed_commit": case["fixed_commit"],
        "test_files_overlaid_from_fixed": test_files,
        "agent_workspace_sha256": digest.hexdigest(),
        "agent_workspace_audit": "pass",
    }
    (case_root / "prepare.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return case_root


def classify(returncode: int, *, timed_out: bool = False) -> str:
    if timed_out:
        return "error"
    return "pass" if returncode == 0 else "fail"


def execute_commands(
    commands: Sequence[str],
    cwd: Path,
    timeout: int,
    env: Optional[Mapping[str, str]] = None,
) -> Dict[str, Any]:
    records: List[Dict[str, Any]] = []
    overall = "pass"
    for command in commands:
        started = time.monotonic()
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(cwd),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=timeout,
                check=False,
                env=dict(env) if env is not None else None,
            )
            timed_out = False
            output = result.stdout or ""
            returncode = result.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            output = exc.stdout or ""
            returncode = 124
        status = classify(returncode, timed_out=timed_out)
        if status == "error" or (overall == "pass" and status == "fail"):
            overall = status
        records.append(
            {
                "command": command,
                "returncode": returncode,
                "status": status,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "output": output,
            }
        )
    return {"overall": overall, "commands": records}


def verify_case(case: Mapping[str, Any], run_root: Path, side: str, timeout: int) -> Dict[str, Any]:
    if not run_root.is_dir():
        die(f"run root not found: {run_root}")
    agent_audit = audit_agent_workspace(run_root / "agent-workspace", case["fixed_commit"])
    if agent_audit:
        die("agent workspace safeguard failed before verification: " + "; ".join(agent_audit))
    sides = [side] if side != "both" else ["buggy", "fixed"]
    results: Dict[str, Any] = {
        "case_id": case["case_id"],
        "verified_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "test_command": case["test_command"],
        "expected": {"buggy": case["expected_buggy_result"], "fixed": case["expected_fixed_result"]},
        "sides": {},
    }
    for current in sides:
        workspace = run_root / "verification" / current
        if not workspace.is_dir():
            die(f"verification workspace not found: {workspace}")
        results["sides"][current] = execute_commands(case["test_command"], workspace, timeout)
    if "buggy" in results["sides"]:
        results["buggy_matches_expected"] = results["sides"]["buggy"]["overall"] == case["expected_buggy_result"]
    if "fixed" in results["sides"]:
        results["fixed_matches_expected"] = results["sides"]["fixed"]["overall"] == case["expected_fixed_result"]
    checks = [results[key] for key in ("buggy_matches_expected", "fixed_matches_expected") if key in results]
    results["reproducible"] = bool(checks) and all(checks)
    output_path = run_root / "reproducibility.json"
    output_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return results


def fetch_source(source_dir: Path, ref: str) -> None:
    source = source_dir.expanduser().resolve()
    if is_within(source, REPO_ROOT):
        die(f"source checkout must be outside this repository: {source}")
    if source.exists():
        die(f"refusing to overwrite existing path: {source}")
    source.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["git", "clone", "--filter=blob:none", "--no-checkout", SOURCE_URL, str(source)],
        text=True,
        check=False,
    )
    if result.returncode != 0:
        die("could not clone BugsInPy")
    run_command(["git", "-C", str(source), "checkout", "--quiet", ref], source)
    actual = git_output(source, "rev-parse", "HEAD")
    if actual != SOURCE_COMMIT:
        die(f"unexpected BugsInPy commit: {actual}; expected {SOURCE_COMMIT}")
    print(json.dumps({"source_dir": str(source), "commit": actual}, indent=2))


def survey(source_dir: Path) -> None:
    source = require_external_source(source_dir)
    rows = []
    for info_path in sorted((source / "projects").glob("*/bugs/*/bug.info")):
        case_info = parse_info(info_path)
        project = info_path.parents[2].name
        bug_id = info_path.parent.name
        patch = info_path.parent / "bug_patch.txt"
        rows.append(
            {
                "project": project,
                "bug_id": bug_id,
                "python_version": case_info.get("python_version"),
                "test_file": case_info.get("test_file"),
                "buggy_commit": case_info.get("buggy_commit_id"),
                "fixed_commit": case_info.get("fixed_commit_id"),
                "patch_lines": len(read_text(patch).splitlines()) if patch.exists() else None,
            }
        )
    print(
        json.dumps(
            {"dataset_commit": git_output(source, "rev-parse", "HEAD"), "bug_count": len(rows), "cases": rows},
            indent=2,
        )
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    fetch = sub.add_parser("fetch-source")
    fetch.add_argument("--source-dir", type=Path, required=True)
    fetch.add_argument("--ref", default="master")

    survey_parser = sub.add_parser("survey")
    survey_parser.add_argument("--source-dir", type=Path, required=True)

    prepare = sub.add_parser("prepare")
    prepare.add_argument("--manifest", type=Path, required=True)
    prepare.add_argument("--case-id", required=True)
    prepare.add_argument("--source-dir", type=Path, required=True)
    prepare.add_argument("--work-root", type=Path, required=True)
    prepare.add_argument("--force", action="store_true")

    verify = sub.add_parser("verify")
    verify.add_argument("--manifest", type=Path, required=True)
    verify.add_argument("--case-id", required=True)
    verify.add_argument("--run-root", type=Path, required=True)
    verify.add_argument("--side", choices=("buggy", "fixed", "both"), default="both")
    verify.add_argument("--timeout", type=int, default=300)

    args = parser.parse_args(argv)
    if args.command == "fetch-source":
        fetch_source(args.source_dir, args.ref)
    elif args.command == "survey":
        survey(args.source_dir)
    elif args.command == "prepare":
        manifest = load_manifest(args.manifest)
        case = find_case(manifest, args.case_id)
        root = prepare_case(manifest, case, args.source_dir, args.work_root, args.force)
        print(json.dumps({"case_id": args.case_id, "run_root": str(root), "agent_workspace": str(root / "agent-workspace")}, indent=2))
    elif args.command == "verify":
        manifest = load_manifest(args.manifest)
        case = find_case(manifest, args.case_id)
        print(json.dumps(verify_case(case, args.run_root.resolve(), args.side, args.timeout), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
