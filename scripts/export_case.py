#!/usr/bin/env python3
"""Export one validated BugsInPy case into a fail-closed agent workspace.

The exporter consumes a Phase 1 run root and emits only the buggy source tree,
the public regression tests already overlaid by the preparation harness, and
agent-safe task/setup files.  Ground truth remains in the control repository,
the Phase 1 run root, and the external BugsInPy checkout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bugsinpy_harness as harness  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
SAFE_METADATA_NAMES = {"CASE.json", "SETUP.md", "TASK.md"}
CONTROL_TOKENS = (
    "bug.info",
    "bug_patch.txt",
    "bug_buggy.txt",
    "bug_fixed.txt",
    "bugsinpy_patchfile.info",
    "bugsinpy_fail.txt",
    "bugsinpy_alltest.txt",
    "ground-truth-repo-cache",
    "buggy_commit",
    "fixed_commit",
    "reference patch",
)


def die(message: str) -> None:
    raise SystemExit(f"error: {message}")


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def reject_control_path(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    if is_within(resolved, REPO_ROOT):
        die(f"{label} must be outside the control repository: {resolved}")
    if resolved == Path(resolved.anchor):
        die(f"{label} may not be a filesystem root")
    return resolved


def load_case(manifest_path: Path, case_id: str) -> Dict[str, Any]:
    return harness.find_case(harness.load_manifest(manifest_path), case_id)


def read_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        die(f"could not read JSON {path}: {exc}")
    if not isinstance(value, dict):
        die(f"expected JSON object in {path}")
    return value


def safe_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        die(f"path escapes its expected root: {path}")


def file_digest(root: Path) -> Tuple[str, List[str]]:
    digest = hashlib.sha256()
    entries: List[str] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            target = os.readlink(path)
            digest.update(b"L\0" + rel.encode() + b"\0" + target.encode())
            entries.append(rel)
        elif path.is_file():
            digest.update(b"F\0" + rel.encode() + b"\0" + path.read_bytes())
            entries.append(rel)
    return digest.hexdigest(), entries


def copy_source_tree(source: Path, destination: Path) -> None:
    if not source.is_dir():
        die(f"validated agent workspace is missing: {source}")
    if (source / ".git").exists():
        die("validated agent workspace unexpectedly contains .git history")

    def ignore(directory: str, names: List[str]) -> set[str]:
        del directory
        return {name for name in names if name == ".git" or name in harness.FORBIDDEN_AGENT_NAMES}

    shutil.copytree(source, destination, symlinks=True, ignore=ignore)


def write_safe_files(destination: Path, case: Mapping[str, Any], metadata: Path) -> None:
    prompt_path = REPO_ROOT / "prompts" / "experiment-001" / f"{case['case_id']}.md"
    if prompt_path.is_file():
        prompt = prompt_path.read_text(encoding="utf-8")
    else:
        # Synthetic smoke cases may be defined entirely by a temporary test
        # manifest; production Experiment 001 cases still require their
        # committed standardized prompt file below.
        if str(case.get("experiment_case_id", "")).startswith("E001-"):
            die(f"standardized prompt is missing: {prompt_path}")
        prompt = str(case["task_prompt"]).rstrip() + "\n"
    if " ".join(str(case["task_prompt"]).split()) not in " ".join(prompt.split()):
        die(f"standardized prompt does not contain the manifest task for {case['case_id']}")

    test_files = list(case.get("test_files", []))
    missing_tests = [name for name in test_files if not (destination / name).is_file()]
    if missing_tests:
        die(f"public regression tests are missing from export: {', '.join(missing_tests)}")

    safe_case = {
        "experiment_case_id": case.get("experiment_case_id", case["case_id"]),
        "case_id": case["case_id"],
        "source": "BugsInPy",
        "project": case["project"],
        "original_repository": case["original_repository"],
        "python_version": case.get("python_version"),
        "public_test_files": test_files,
        "test_command": case["test_command"],
    }
    (destination / "CASE.json").write_text(
        json.dumps(safe_case, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (destination / "TASK.md").write_text(prompt.rstrip() + "\n", encoding="utf-8")

    requirements = metadata / "requirements.txt"
    setup_script = metadata / "setup.sh"
    setup_lines = [
        "# Agent workspace setup",
        "",
        f"Project: {case['project']}",
        f"Recommended Python: {case.get('python_version', 'see environment')}",
        "",
        "This directory is a sanitized buggy project checkout with its public regression test.",
        "Use the case-specific test command in CASE.json after installing dependencies.",
        "The benchmark evaluator owns the fixed reference and hidden evaluation tests.",
    ]
    if requirements.is_file():
        # Keep dependency provenance useful, but never turn a VCS requirement
        # into an instruction to clone a second project checkout.
        req_name = "requirements.txt"
        shutil.copyfile(requirements, destination / req_name)
        setup_lines.extend(["", f"Install the provided dependency pins with: pip install -r {req_name}"])
    if setup_script.is_file():
        setup_lines.extend(["", "The source benchmark setup script is available to the evaluator; run only the commands appropriate to this disposable environment."])
    (destination / "SETUP.md").write_text("\n".join(setup_lines) + "\n", encoding="utf-8")


def patch_additions(source_dir: Path, case: Mapping[str, Any]) -> List[Tuple[str, str]]:
    patch = source_dir / "projects" / case["project"] / "bugs" / str(case["bug_id"]) / "bug_patch.txt"
    if not patch.is_file():
        die(f"reference patch is missing from external BugsInPy source: {patch}")
    additions: List[Tuple[str, str]] = []
    current_path = ""
    for line_number, line in enumerate(harness.read_text(patch).splitlines(), start=1):
        if line.startswith("+++ "):
            current_path = line[4:].split("\t", 1)[0]
            if current_path.startswith("b/"):
                current_path = current_path[2:]
        elif line.startswith("+") and not line.startswith("+++"):
            content = line[1:].strip()
            if len(content) >= 24:
                additions.append((current_path or "<unknown>", content))
    return additions


def audit_export(
    destination: Path,
    case: Mapping[str, Any],
    source_dir: Path,
    *,
    buggy_baseline: Optional[Path] = None,
    audit_path: Optional[Path] = None,
) -> Dict[str, Any]:
    problems: List[str] = []
    destination = destination.resolve()
    external_source = harness.require_external_source(source_dir)
    if not destination.is_dir():
        problems.append("export directory is missing")
    if is_within(destination, REPO_ROOT):
        problems.append("export directory is inside the control repository")

    fixed_commit = str(case["fixed_commit"])
    buggy_commit = str(case["buggy_commit"])
    hidden_files = [str(item) for item in case.get("hidden_test_files", [])]
    additions = patch_additions(external_source, case)
    public_test_paths = {str(item).replace("\\", "/") for item in case.get("test_files", [])}
    control_strings = {
        str(REPO_ROOT),
        REPO_ROOT.name,
        "devin-agent-benchmark",
        fixed_commit,
        *CONTROL_TOKENS,
        *hidden_files,
    }
    if destination.is_dir():
        for path in sorted(destination.rglob("*"), key=lambda item: item.relative_to(destination).as_posix()):
            rel = path.relative_to(destination).as_posix()
            if path.is_symlink():
                try:
                    resolved = path.resolve()
                    if not is_within(resolved, destination):
                        problems.append(f"symlink escapes export: {rel}")
                except OSError as exc:
                    problems.append(f"unreadable symlink {rel}: {exc}")
                continue
            if path.name in harness.FORBIDDEN_AGENT_NAMES:
                problems.append(f"forbidden artifact name: {rel}")
            if path.is_dir():
                continue
            try:
                data = path.read_bytes()
            except OSError as exc:
                problems.append(f"unreadable export file {rel}: {exc}")
                continue
            text = data.decode("utf-8", errors="ignore")
            for token in control_strings:
                if token and token in text:
                    problems.append(f"control/ground-truth token in {rel}: {token}")
            if buggy_commit in text and rel in public_test_paths:
                # A public regression test may mention the buggy revision in a
                # fixture, but this is retained in the audit result for review.
                problems.append(f"buggy commit hash in public test {rel}")
            if rel not in public_test_paths:
                original_text = ""
                if buggy_baseline and (buggy_baseline / rel).is_file():
                    original_text = (buggy_baseline / rel).read_text(encoding="utf-8", errors="ignore")
                for patch_path, addition in additions:
                    if addition in text and addition not in original_text:
                        problems.append(f"reference patch fragment in {rel} (source path {patch_path})")
                        break
    git_dir = destination / ".git"
    if git_dir.exists():
        # A future provider may add a local .git directory. It is safe only if
        # it is a newly initialized history without source/reference commits.
        try:
            log = subprocess.run(
                ["git", "-C", str(destination), "log", "--all", "--format=%H%n%B"],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            )
            if log.returncode != 0:
                problems.append("could not inspect exported .git history")
            elif fixed_commit in log.stdout or buggy_commit in log.stdout:
                problems.append("exported .git history contains benchmark commit metadata")
            remote = subprocess.run(
                ["git", "-C", str(destination), "remote", "-v"],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            )
            if REPO_ROOT.name in remote.stdout:
                problems.append("exported .git remote points to the control repository")
        except OSError as exc:
            problems.append(f"could not inspect exported .git history: {exc}")
    digest, entries = file_digest(destination) if destination.is_dir() else (None, [])
    result: Dict[str, Any] = {
        "audit_version": 1,
        "audited_at_utc": utc_now(),
        "case_id": case["case_id"],
        "destination": str(destination),
        "fixed_commit_checked": True,
        "reference_patch_checked": True,
        "hidden_test_names_checked": hidden_files,
        "file_count": len(entries),
        "export_sha256": digest,
        "status": "pass" if not problems else "fail",
        "problems": problems,
    }
    if audit_path is None:
        audit_path = destination.parent / f"{destination.name}.leak-audit.json"
    audit_path = audit_path.expanduser().resolve()
    if is_within(audit_path, destination):
        die("audit report must not be written inside the agent-visible export")
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if problems:
        die("export leak audit failed: " + "; ".join(problems))
    return result


def export_case(
    manifest_path: Path,
    case_id: str,
    run_root: Path,
    source_dir: Path,
    destination: Path,
    force: bool,
) -> Dict[str, Any]:
    case = load_case(manifest_path, case_id)
    run_root = run_root.expanduser().resolve()
    destination = reject_control_path(destination, "export destination")
    source_dir = source_dir.expanduser().resolve()
    agent = run_root / "agent-workspace"
    if not agent.is_dir():
        die(f"run root is not a validated preparation output: {run_root}")
    if not (run_root / "prepare.json").is_file() or not (run_root / "reproducibility.json").is_file():
        die("run root is missing Phase 1 preparation/reproducibility records")
    if destination.exists():
        if not force:
            die(f"refusing to overwrite existing export: {destination}")
        if destination == destination.parent or destination == Path(destination.anchor):
            die("refusing unsafe forced export target")
        if destination.is_dir() and destination.is_symlink():
            die("refusing to overwrite a symlink export target")
        if destination.is_dir():
            shutil.rmtree(destination)
        else:
            destination.unlink()
        for sidecar in (
            destination.parent / f"{destination.name}.baseline",
            destination.parent / f"{destination.name}.baseline.json",
            destination.parent / f"{destination.name}.leak-audit.json",
            destination.parent / f"{destination.name}.export.json",
        ):
            if sidecar.is_dir() and not sidecar.is_symlink():
                shutil.rmtree(sidecar)
            elif sidecar.exists() or sidecar.is_symlink():
                sidecar.unlink()
    destination.parent.mkdir(parents=True, exist_ok=True)
    copy_source_tree(agent, destination)
    write_safe_files(destination, case, run_root / "metadata")
    audit = audit_export(destination, case, source_dir, buggy_baseline=run_root / "verification" / "buggy")
    baseline_digest, baseline_entries = file_digest(destination)
    baseline_path = destination.parent / f"{destination.name}.baseline"
    if baseline_path.exists():
        die(f"refusing to overwrite existing evaluator baseline: {baseline_path}")
    shutil.copytree(destination, baseline_path, symlinks=True)
    baseline = {
        "case_id": case["case_id"],
        "experiment_case_id": case.get("experiment_case_id"),
        "export_sha256": baseline_digest,
        "entries": baseline_entries,
        "created_at_utc": utc_now(),
        "agent_workspace": str(destination),
    }
    baseline_record_path = destination.parent / f"{destination.name}.baseline.json"
    baseline_record_path.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    record = {
        "case_id": case["case_id"],
        "experiment_case_id": case.get("experiment_case_id"),
        "source_run_root": str(run_root),
        "destination": str(destination),
        "audit_report": str(destination.parent / f"{destination.name}.leak-audit.json"),
        "baseline_dir": str(baseline_path),
        "baseline_record": str(baseline_record_path),
        "export_sha256": audit["export_sha256"],
        "agent_visible_contents": ["buggy source tree", "public regression tests", "CASE.json", "SETUP.md", "TASK.md", "requirements.txt if supplied by BugsInPy"],
    }
    record_path = destination.parent / f"{destination.name}.export.json"
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(export_case(args.manifest, args.case_id, args.run_root, args.source_dir, args.destination, args.force), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
