#!/usr/bin/env python3
"""Generate an evidence-based forensic analysis of the completed E002 runs.

This analyzer intentionally uses observable session messages, tool arguments,
tool observations, patches, evaluator records, and runner metadata only.  It
does not read or emit ``reasoning_content`` from Devin exports.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import statistics
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS_ROOT = REPO_ROOT / "results/runs/experiment-002"
DEFAULT_PUBLIC_ROOT = REPO_ROOT / "artifacts/experiment-002"
DEFAULT_SUMMARY = REPO_ROOT / "results/experiment-002-summary.json"
DEFAULT_REPORT = REPO_ROOT / "reports/experiment-002-forensic-analysis.md"
DEFAULT_FORENSICS = REPO_ROOT / "results/experiment-002-forensics.json"
DEFAULT_TOOL_CSV = REPO_ROOT / "results/experiment-002-tool-metrics.csv"
DEFAULT_PATCH_CSV = REPO_ROOT / "results/experiment-002-source-patch-metrics.csv"

CASE_INFO: Dict[str, Dict[str, str]] = {
    "black-16": {
        "source_path": "black.py",
        "test_path": "tests/test_black.py",
        "behavior": "Ignore a Python symlink resolving outside the discovery root while continuing to discover in-root files.",
        "implementation": "Catch the outside-root relative_to failure for symlinks, report the ignored path, and continue; preserve errors for non-symlinks.",
        "failure_class": "successful repair",
    },
    "fastapi-3": {
        "source_path": "fastapi/routing.py",
        "test_path": "tests/test_serialize_response_model.py",
        "behavior": "Recursively serialize nested response models with aliases and exclude unset fields.",
        "implementation": "Normalize BaseModel values recursively through lists and mappings before response-field validation.",
        "failure_class": "successful repair",
    },
    "scrapy-3": {
        "source_path": "scrapy/downloadermiddlewares/redirect.py",
        "test_path": "tests/test_downloadermiddleware_redirect.py",
        "behavior": "Normalize an extra-slash protocol-relative Location using the request scheme and redirect host.",
        "implementation": "Preserve the Location header bytes, parse the request scheme, and collapse leading slashes before urljoin.",
        "failure_class": "successful repair",
    },
    "tqdm-5": {
        "source_path": "tqdm/_tqdm.py",
        "test_path": "tqdm/tests/tests_tqdm.py",
        "behavior": "A disabled progress wrapper retains an inferred total for a sized iterable and reports its length consistently.",
        "implementation": "Compute the iterable length before the disabled early return and initialize the public total state there.",
        "failure_class": "partial fix / correct target but incomplete implementation",
    },
    "tornado-13": {
        "source_path": "tornado/http1connection.py",
        "test_path": "tornado/test/http1connection_test.py",
        "behavior": "Read a bodyless HTTP/1.0 response without Content-Length when the response start line has no method field.",
        "implementation": "Read method defensively because response start lines have code/reason rather than method.",
        "failure_class": "successful repair",
    },
}

TOKEN_FIELDS = {
    "prompt": "total_prompt_tokens",
    "completion": "total_completion_tokens",
    "cached": "total_cached_tokens",
}


def read_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_text(value: Any, limit: int = 500) -> str:
    text = str(value or "")
    private_tmp = "/" + "private/" + "tmp/"
    volume_root = "/" + "Volumes/" + "Research/"
    user_root = "/" + "Users/"
    text = re.sub(rf"{re.escape(private_tmp)}devin-agent-benchmark-e002\.[^/\s]+", "<run-root>", text)
    text = re.sub(rf"{re.escape(volume_root)}[^\s'\"]+", "<control-repo>", text)
    text = re.sub(rf"{re.escape(user_root)}[^/\s'\"]+", "<local-user>", text)
    text = re.sub(r"/tmp/devin-overflow/[0-9a-f]+", "<overflow>", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def observation_text(tool: Dict[str, Any], step: Optional[Dict[str, Any]] = None) -> str:
    observation = tool.get("observation")
    if observation is None and step is not None:
        observation = step.get("observation")
    if isinstance(observation, dict):
        results = observation.get("results")
        if isinstance(results, list):
            return "\n".join(str(item.get("content", "")) for item in results if isinstance(item, dict))
        if isinstance(observation.get("content"), str):
            return observation["content"]
    return ""


def exit_code(output: str) -> Optional[int]:
    matches = re.findall(r"Exit code:\s*(\d+)", output, flags=re.IGNORECASE)
    return int(matches[-1]) if matches else None


def is_test_command(command: str) -> bool:
    if re.search(r"\bpython(?:3)?\s+-m\s+(?:pytest|unittest)\b", command):
        return True
    if re.search(r"(?:^|(?:&&|;|\|\|)\s+)(?:(?:[A-Z_][A-Z0-9_]*=\S+|timeout\s+\d+)\s+)*(?:pytest|nosetests|tox)\b", command):
        return True
    if re.search(r"\bpython(?:3)?\b[^;&|]*(?:/(?:verify|repro)[^/;&|]*\.py)\b", command):
        return True
    # Several historical repositories could not run their old test runner in
    # the container.  Count an explicit inline assertion/test function as an
    # observable test attempt, while excluding ordinary import/version probes.
    return bool(
        re.search(r"\bpython(?:3)?\b[^;&|]*(?:-c|- <<)", command)
        and re.search(r"\bassert\b|\btest_(?:bool|redirect|http)|test_bool|test_redirect|test_http10|verify\.py|repro[_-]", command)
    )


def command_status(command: str, output: str) -> str:
    code = exit_code(output)
    if code is not None:
        return "pass" if code == 0 else "fail"
    if re.search(r"\b(?:FAILED|ERROR:|Traceback \(most recent call last\))\b", output):
        return "fail"
    if re.search(r"\b(?:OK|PASSED|passed|all good)\b", output):
        return "pass"
    return "unknown"


def command_category(command: str, test: bool) -> str:
    if test:
        return "test"
    if re.search(r"\b(?:pip|ensurepip|venv|virtualenv|apt-get|apt)\b|requirements\.txt|site-packages|python(?:3)?\s+--version|pip list|pip --version|curl .*get-pip|PYTHONPATH=/tmp|/(?:stub|shim)\b|\.venv", command, re.IGNORECASE):
        return "environment/dependency"
    if re.search(r"\b(?:grep|rg|find|ls|head|tail|sed|cat|git\s+(?:log|status|diff|stash))\b", command):
        return "inspection/search"
    return "other shell"


def normalize_command(command: str) -> str:
    command = re.sub(r"/tmp/devin-overflow/[0-9a-f]+/content\.txt", "<overflow>", command)
    return re.sub(r"\s+", " ", command).strip()


def tool_calls(session: Dict[str, Any]) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
    output: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
    for step in session.get("steps", []):
        if not isinstance(step, dict) or step.get("source") != "agent":
            continue
        for tool in step.get("tool_calls", []):
            if isinstance(tool, dict):
                output.append((step, tool))
    return output


def argument_strings(arguments: Dict[str, Any]) -> Iterable[str]:
    for key in ("file_path", "path", "command", "query", "url"):
        value = arguments.get(key)
        if isinstance(value, str):
            yield value


def path_mentions(arguments: Dict[str, Any], case: Dict[str, str]) -> List[str]:
    values = list(argument_strings(arguments))
    candidates = [case["source_path"], case["test_path"]]
    paths: List[str] = []
    for value in values:
        for candidate in candidates:
            if candidate in value or Path(candidate).name in value:
                paths.append(candidate)
    return paths


def source_mutation(command: str, source_path: str) -> bool:
    if source_path not in command and Path(source_path).name not in command:
        return False
    source_name = re.escape(Path(source_path).name)
    return bool(
        re.search(r"\bsed\s+-i|\bperl\s+-i|\b(?:cp|mv)\s+[^;&|]+\s+[^;&|]*" + source_name, command)
        or re.search(r"(?:cat|tee)\s+[^;&|]*>\s*[^;&|]*" + source_name, command)
        or re.search(r"\bpython(?:3)?\b[^;&|]*(?:open\(|write\(|replace\(|read_text|write_text)", command)
    )


def parse_patch(path: Path) -> Dict[str, Any]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    status_files: List[str] = []
    sections: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None
    in_hunk = False
    for line in lines:
        if line.startswith("new file: ") or line.startswith("symlink change: "):
            status_files.append(line.split(": ", 1)[1])
            continue
        if line.startswith("--- a/"):
            current = {"path": line[6:], "additions": 0, "deletions": 0, "_raw": [line]}
            sections.append(current)
            in_hunk = False
            continue
        if current is not None and not line.startswith("new file: ") and not line.startswith("symlink change: "):
            current["_raw"].append(line)
        if current is not None and line.startswith("@@"):
            in_hunk = True
            continue
        if current is None or not in_hunk:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            current["additions"] += 1
        elif line.startswith("-") and not line.startswith("---"):
            current["deletions"] += 1
    source_sections = [section for section in sections if section["path"] in {info["source_path"] for info in CASE_INFO.values()}]
    public_sections = [{key: value for key, value in section.items() if key != "_raw"} for section in sections]
    public_source_sections = [{key: value for key, value in section.items() if key != "_raw"} for section in source_sections]
    source_blob = "\n".join(line for section in source_sections for line in section["_raw"]).encode("utf-8")
    return {
        "patch_bytes": path.stat().st_size,
        "status_files": status_files,
        "diff_sections": public_sections,
        "source_sections": public_source_sections,
        "source_diff_sha256": hashlib.sha256(source_blob).hexdigest() if source_sections else None,
        "source_additions": sum(item["additions"] for item in source_sections),
        "source_deletions": sum(item["deletions"] for item in source_sections),
    }


def classify_changed_path(path: str, source_path: str) -> str:
    if path == source_path:
        return "source"
    if path.startswith(".venv/"):
        return "virtualenv"
    if "/__pycache__/" in f"/{path}" or path.endswith(".pyc"):
        return "bytecode/cache"
    if path.startswith("tests/") or "/test/" in f"/{path}" or "/tests/" in f"/{path}":
        return "test/generated"
    if path.endswith(".py"):
        return "generated Python"
    return "other generated/environment"


def find_reference_root(explicit: Optional[Path]) -> Optional[Path]:
    if explicit and (explicit / "projects").is_dir():
        return explicit
    roots = sorted(Path("private-temp-root").glob("bugs-in-py-survey.*/projects"))
    return roots[-1].parent if roots else None


def reference_patch(root: Optional[Path], case_id: str) -> Dict[str, Any]:
    if root is None:
        return {"available": False}
    project, bug_id = case_id.rsplit("-", 1)
    path = root / "projects" / project / "bugs" / bug_id / "bug_patch.txt"
    if not path.is_file():
        return {"available": False, "path": str(path)}
    parsed = parse_patch(path)
    return {
        "available": True,
        "changed_files": [section["path"] for section in parsed["diff_sections"]],
        "additions": sum(section["additions"] for section in parsed["diff_sections"]),
        "deletions": sum(section["deletions"] for section in parsed["diff_sections"]),
        "sha256": sha256(path),
        "source": "BugsInPy bug_patch.txt; evaluator-side comparison after both runs closed",
    }


def artifact_record(path: Path, relative: str) -> Dict[str, Any]:
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256(path)}


def analyze_run(
    run: Dict[str, Any],
    results_root: Path,
    public_root: Path,
    summary_by_run: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    run_id = run["run_id"]
    case_id = run["case_id"]
    case = CASE_INFO[case_id]
    raw_output = results_root / run_id / "output"
    public_run = public_root / run_id
    session = read_json(public_run / "devin-session-export.sanitized.json")
    session_summary = read_json(public_run / "session-summary.json")
    metadata = read_json(public_run / "run-metadata.json")
    evaluation = read_json(public_run / "evaluation-result.json")
    workspace = read_json(public_run / "workspace-change-summary.json")
    calls = tool_calls(session)
    functions = Counter(str(tool.get("function_name", "unknown")) for _, tool in calls)
    shell_commands: List[Dict[str, Any]] = []
    test_attempts: List[Dict[str, Any]] = []
    source_references: List[Dict[str, Any]] = []
    source_edits: List[Dict[str, Any]] = []
    inspected: List[str] = []
    repeated = Counter()
    ordinary_failures: List[Dict[str, Any]] = []
    for step, tool in calls:
        fn = str(tool.get("function_name", "unknown"))
        arguments = tool.get("arguments") if isinstance(tool.get("arguments"), dict) else {}
        mentions = path_mentions(arguments, case)
        for mention in mentions:
            source_references.append({"step": step.get("step_id"), "function": fn, "path": mention})
            if fn in {"read", "grep"} or (fn == "exec" and mention in str(arguments.get("command", ""))):
                if mention not in inspected:
                    inspected.append(mention)
        direct_paths = [arguments.get("file_path"), arguments.get("path")]
        if fn in {"edit", "write"} and any(isinstance(value, str) and (case["source_path"] in value or Path(case["source_path"]).name == Path(value).name) for value in direct_paths):
            source_edits.append({"step": step.get("step_id"), "function": fn, "kind": "direct source edit"})
        command = arguments.get("command") if isinstance(arguments.get("command"), str) else ""
        if fn == "exec" and command:
            output = observation_text(tool, step)
            test = is_test_command(command)
            status = command_status(command, output)
            category = command_category(command, test)
            normalized = normalize_command(command)
            repeated[normalized] += 1
            record = {
                "step": step.get("step_id"),
                "command": safe_text(command, 800),
                "category": category,
                "status": status,
                "exit_code": exit_code(output),
                "source_edit_after": False,
            }
            shell_commands.append(record)
            if test:
                test_attempts.append({
                    "step": step.get("step_id"),
                    "command": safe_text(command, 800),
                    "status": status,
                    "exit_code": exit_code(output),
                })
            if source_mutation(command, case["source_path"]):
                source_edits.append({"step": step.get("step_id"), "function": fn, "kind": "shell source mutation"})
            code = exit_code(output)
            if code not in (None, 0):
                ordinary_failures.append({
                    "step": step.get("step_id"),
                    "category": category,
                    "exit_code": code,
                    "command": safe_text(command, 500),
                    "output": safe_text(output[-360:], 360),
                })
    first_edit_step = min((int(item["step"]) for item in source_edits), default=None)
    first_source_reference = next((item for item in source_references if item["path"] == case["source_path"]), None)
    for item in shell_commands:
        item["source_edit_after"] = first_edit_step is not None and int(item["step"]) > first_edit_step
    post_edit_tests = [item for item in test_attempts if first_edit_step is not None and int(item["step"]) > first_edit_step]
    post_edit_calls = [
        (step, tool)
        for step, tool in calls
        if first_edit_step is not None and int(step.get("step_id", 0)) > first_edit_step
    ]
    repeated_commands = [
        {"command": safe_text(command, 500), "count": count}
        for command, count in repeated.most_common()
        if count > 1
    ][:12]
    changed_files = evaluation.get("patch", {}).get("changed_files", [])
    change_categories = Counter(classify_changed_path(str(path), case["source_path"]) for path in changed_files)
    patch = parse_patch(raw_output / "agent.patch")
    final_messages = [
        safe_text(step.get("message"), 900)
        for step in session.get("steps", [])
        if isinstance(step, dict) and step.get("source") == "agent" and isinstance(step.get("message"), str) and step.get("message")
    ]
    raw_files: Dict[str, Any] = {}
    for filename in ("devin-session-export.json", "devin.stdout.txt", "devin.stderr.txt"):
        path = raw_output / filename
        if path.is_file():
            content = path.read_text(encoding="utf-8", errors="replace")
            if filename == "devin-session-export.json":
                # Do not scan raw JSON text: it contains hidden reasoning.
                # Structured rejection fields are the authoritative source for
                # this question, and stdout/stderr are scanned separately.
                matches = []
            else:
                matches = re.findall(r"(?i)(?:tool call[^\n]{0,100}(?:reject|denied)|(?:permission|approval)[^\n]{0,100}(?:reject|denied|required))", content)
            raw_files[filename] = {
                "path": str(Path("results/runs/experiment-002") / run_id / "output" / filename),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "explicit_rejection_markers_outside_reasoning": None if filename == "devin-session-export.json" else len(matches),
            }
    rejected = session_summary.get("rejected_tool_calls") or metadata.get("rejected_tool_calls") or []
    record = summary_by_run.get(run_id, {})
    return {
        "run_id": run_id,
        "case_id": case_id,
        "condition": run["condition"],
        "model": run["model"],
        "effort_level": run["effort_level"],
        "session_id": metadata.get("session_id"),
        "task_success": evaluation.get("task_success"),
        "evaluation_status": evaluation.get("evaluation_status"),
        "termination_reason": evaluation.get("termination_reason"),
        "wall_time_seconds": evaluation.get("elapsed_seconds"),
        "steps": evaluation.get("steps"),
        "tool_calls": len(calls),
        "tool_calls_by_function": dict(sorted(functions.items())),
        "tool_behavior": {
            "shell_exec_calls": functions.get("exec", 0),
            "read_calls": functions.get("read", 0),
            "search_calls": functions.get("grep", 0) + functions.get("glob", 0) + functions.get("search", 0),
            "web_calls": functions.get("web_search", 0) + functions.get("webfetch", 0),
            "edit_write_calls": functions.get("edit", 0) + functions.get("write", 0),
            "direct_source_edit_calls": sum(1 for item in source_edits if item["kind"] == "direct source edit"),
            "shell_source_mutations": sum(1 for item in source_edits if item["kind"] == "shell source mutation"),
            "source_edit_operations": source_edits,
            "source_edit_revision_evidence": len(source_edits) > 1,
            "first_relevant_source_step": first_source_reference["step"] if first_source_reference else None,
            "first_relevant_source_function": first_source_reference["function"] if first_source_reference else None,
            "first_test": test_attempts[0] if test_attempts else None,
            "test_attempt_count": len(test_attempts),
            "test_pass_count": sum(item["status"] == "pass" for item in test_attempts),
            "test_fail_count": sum(item["status"] == "fail" for item in test_attempts),
            "tests_after_first_source_edit": len(post_edit_tests),
            "post_edit_observable_calls": len(post_edit_calls),
            "post_edit_target_references": sum(1 for step, tool in post_edit_calls if path_mentions(tool.get("arguments", {}), case)),
            "inspected_target_paths": inspected,
            "repeated_commands": repeated_commands,
            "environment_dependency_calls": sum(item["category"] == "environment/dependency" for item in shell_commands),
            "ordinary_shell_failures": ordinary_failures,
            "commands": shell_commands,
            "test_attempts": test_attempts,
        },
        "rejected_tool_calls": rejected,
        "rejection_audit": {
            "summary_rejected_tool_calls": rejected,
            "permission_warning": metadata.get("permission_warning"),
            "stdout_stderr_explicit_rejection_markers": {name: item["explicit_rejection_markers_outside_reasoning"] for name, item in raw_files.items() if name != "devin-session-export.json"},
            "conclusion": "none observed" if not rejected else "structured rejection recorded",
        },
        "evaluator": {
            "public": evaluation.get("tests_after"),
            "heldout": evaluation.get("hidden_tests"),
            "regression": evaluation.get("regression_tests"),
            "interventions": evaluation.get("interventions"),
        },
        "patch": {
            "changed_file_count": len(changed_files),
            "changed_files_by_category": dict(sorted(change_categories.items())),
            "source_files": workspace.get("source_files", []),
            "source_additions": patch["source_additions"],
            "source_deletions": patch["source_deletions"],
            "source_diff_sections": patch["source_sections"],
            "source_diff_sha256": patch["source_diff_sha256"],
            "raw_recorded_additions": evaluation.get("patch", {}).get("line_counts", {}).get("additions"),
            "raw_recorded_deletions": evaluation.get("patch", {}).get("line_counts", {}).get("deletions"),
            "patch_sha256": evaluation.get("patch", {}).get("sha256"),
        },
        "observable_final_messages": final_messages[-3:],
        "provider_tokens": record.get("tokens", {}),
        "artifacts": raw_files,
    }


def pair_records(runs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_case: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for run in runs:
        by_case.setdefault(run["case_id"], {})[run["condition"]] = run
    pairs: List[Dict[str, Any]] = []
    for case_id in CASE_INFO:
        pair = by_case[case_id]
        medium, maximum = pair["M"], pair["X"]
        def delta(field: str) -> Optional[float]:
            left, right = maximum.get(field), medium.get(field)
            return (left - right) if isinstance(left, (int, float)) and isinstance(right, (int, float)) else None
        def token_delta(field: str) -> Optional[float]:
            left = maximum.get("provider_tokens", {}).get(field)
            right = medium.get("provider_tokens", {}).get(field)
            return (left - right) if isinstance(left, (int, float)) and isinstance(right, (int, float)) else None
        mt = medium["tool_behavior"]
        xt = maximum["tool_behavior"]
        source_equal = medium["patch"]["source_diff_sha256"] == maximum["patch"]["source_diff_sha256"]
        if case_id == "tqdm-5":
            interpretation = "Max explored more and edited the same target, but its two-line initialization missed inferred totals for sized iterables; Medium passed the held-out contract."
        elif case_id == "black-16":
            interpretation = "Both reached the same compact source behavior and passed; Max incurred a large virtualenv-only churn record."
        elif case_id == "scrapy-3":
            interpretation = "Both found the redirect path and passed; Max spent substantially more time and created a large virtualenv/cache record."
        elif case_id == "fastapi-3":
            interpretation = "Both implemented the recursive response normalization behavior; Max used substantially more exploration, web lookup, and time."
        else:
            interpretation = "Both reached the same one-line defensive source fix and passed; Max spent more wall time with only a small increase in steps."
        pairs.append({
            "case_id": case_id,
            "medium_run": medium["run_id"],
            "max_run": maximum["run_id"],
            "outcome": "both succeeded" if medium["task_success"] and maximum["task_success"] else ("Medium only" if medium["task_success"] else ("Max only" if maximum["task_success"] else "both failed")),
            "max_minus_medium": {
                "wall_time_seconds": delta("wall_time_seconds"),
                "steps": delta("steps"),
                "tool_calls": delta("tool_calls"),
                "prompt_tokens": token_delta("prompt"),
                "completion_tokens": token_delta("completion"),
                "cached_tokens": token_delta("cached"),
            },
            "tool_behavior": {
                "medium": {key: mt.get(key) for key in ("shell_exec_calls", "read_calls", "search_calls", "web_calls", "edit_write_calls", "test_attempt_count", "tests_after_first_source_edit", "environment_dependency_calls")},
                "max": {key: xt.get(key) for key in ("shell_exec_calls", "read_calls", "search_calls", "web_calls", "edit_write_calls", "test_attempt_count", "tests_after_first_source_edit", "environment_dependency_calls")},
            },
            "source_patch_identical": source_equal,
            "interpretation": interpretation,
        })
    return pairs


def write_csv(path: Path, rows: List[Dict[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_analysis(args: argparse.Namespace) -> Dict[str, Any]:
    runs_manifest = read_json(args.runs_manifest)
    summary = read_json(args.summary)
    summary_by_run = {record["run_id"]: record for record in summary.get("runs", [])}
    runs = runs_manifest.get("runs", [])
    if len(runs) != 10 or [run["run_id"] for run in runs] != runs_manifest.get("run_order"):
        raise ValueError("E002 run manifest is not the expected ten-run frozen order")
    run_records = [analyze_run(run, args.results_root, args.public_root, summary_by_run) for run in runs]
    reference_root = find_reference_root(args.reference_root)
    references = {case_id: reference_patch(reference_root, case_id) for case_id in CASE_INFO}
    for record in run_records:
        reference = references[record["case_id"]]
        source_files = set(record["patch"]["source_files"])
        reference_files = set(reference.get("changed_files", []))
        record["reference_comparison"] = {
            "reference_files": sorted(reference_files),
            "reference_additions": reference.get("additions"),
            "reference_deletions": reference.get("deletions"),
            "agent_source_file_overlap": sorted(source_files & reference_files),
            "comparison_performed_after_pair_closed": True,
        }
    pairs = pair_records(run_records)
    condition_summary: Dict[str, Any] = {}
    for condition in ("M", "X"):
        selected = [run for run in run_records if run["condition"] == condition]
        walls = [float(run["wall_time_seconds"]) for run in selected]
        condition_summary[condition] = {
            "runs": len(selected),
            "solved": sum(bool(run["task_success"]) for run in selected),
            "total_wall_time_seconds": round(sum(walls), 3),
            "mean_wall_time_seconds": round(statistics.mean(walls), 3),
            "median_wall_time_seconds": round(statistics.median(walls), 3),
            "mean_steps": round(statistics.mean(run["steps"] for run in selected), 3),
            "total_steps": sum(run["steps"] for run in selected),
            "total_tool_calls": sum(run["tool_calls"] for run in selected),
            "tokens": {key: sum(run["provider_tokens"].get(key, 0) for run in selected) for key in ("prompt", "completion", "cached")},
            "total_source_additions": sum(run["patch"]["source_additions"] for run in selected),
            "total_source_deletions": sum(run["patch"]["source_deletions"] for run in selected),
            "total_changed_files": sum(run["patch"]["changed_file_count"] for run in selected),
            "total_source_edit_operations": sum(len(run["tool_behavior"]["source_edit_operations"]) for run in selected),
        }
    ratios: Dict[str, Optional[float]] = {}
    for field in ("total_wall_time_seconds", "mean_wall_time_seconds", "median_wall_time_seconds", "mean_steps", "total_steps", "total_tool_calls", "total_changed_files", "total_source_additions", "total_source_deletions"):
        denominator = condition_summary["M"][field]
        numerator = condition_summary["X"][field]
        ratios[f"max_over_medium_{field}"] = round(numerator / denominator, 3) if denominator else None
    for field in ("prompt", "completion", "cached"):
        denominator = condition_summary["M"]["tokens"][field]
        numerator = condition_summary["X"]["tokens"][field]
        ratios[f"max_over_medium_{field}_tokens"] = round(numerator / denominator, 3) if denominator else None
    output = {
        "schema_version": 1,
        "analysis": "forensic observable-behavior analysis",
        "experiment_id": "experiment-002",
        "control_commit": summary.get("control_commit"),
        "frozen_order": runs_manifest.get("run_order"),
        "method": {
            "session_source": "public sanitized session exports for messages, tool arguments, and observations; raw exports/stdout/stderr inventoried and rejection-scanned",
            "hidden_reasoning": "not analyzed or emitted",
            "source_metrics": "unified source diff sections parsed separately from generated/environment status records",
            "reference_policy": "human reference patches read evaluator-side only after both conditions per case were closed",
        },
        "rejections": {"runs_with_structured_rejections": [run["run_id"] for run in run_records if run["rejected_tool_calls"]], "total": sum(len(run["rejected_tool_calls"]) for run in run_records)},
        "condition_summary": condition_summary,
        "max_over_medium_ratios": ratios,
        "runs": run_records,
        "pairs": pairs,
        "references": references,
        "interpretive_guardrails": {
            "observed": ["E002 had 5/5 Medium and 4/5 Max task success.", "Max used more wall time in every pair and more recorded steps in four of five pairs.", "The only failed task was tqdm-5 under Max: public/regression passed but held-out failed.", "Black-X and Scrapy-X had large generated/environment file churn while source-file counts remained one."],
            "suggestive": ["Extra effort was associated with more exploration and environment work in several Max runs, especially FastAPI-X and Scrapy-X.", "The E002 sample suggests more effort did not guarantee higher correctness on this five-case set."],
            "not_supported": ["No causal or statistical-significance claim about model effort can be made from n=5 pairs.", "Tool traces do not reveal hidden chain-of-thought or internal model state.", "Total filesystem patch size is not a valid proxy for source-edit complexity when virtualenv/cache churn is present.", "File overlap or similar diff size does not prove that an agent copied the human patch."],
        },
    }
    return output


def report_text(data: Dict[str, Any]) -> str:
    runs = data["runs"]
    pairs = data["pairs"]
    lines: List[str] = []
    lines += ["# Experiment 002 forensic analysis", "", "Observable-behavior analysis of the completed paired Devin evaluation. No Devin session was invoked or rerun for this analysis. Hidden reasoning content was not analyzed.", ""]
    lines += ["## Executive finding", "", "Medium solved 5/5 cases; Max solved 4/5. Max took more wall time in all five pairs and recorded more steps in four. The sole failure was Max on tqdm-5: the public and regression checks passed, but the evaluator-only sized-iterable test failed because `total` remained `None`.", ""]
    lines += ["E002 is an autonomous-capability result under the frozen isolated Docker configuration. It is not a causal or statistically significant comparison: there are five paired cases, the cases were not randomly sampled for this analysis, and E001 is not a valid capability baseline because its noninteractive permission gate rejected required tools.", ""]
    lines += ["## Evidence and scope", "", "The analyzer reconciles all ten public sanitized session exports, the corresponding raw session-export/stdout/stderr inventories, runner metadata, evaluator results, workspace-change summaries, and final patches. It counts only observable tool calls, commands, observations, edits, and user-visible agent messages; it never reads or emits Devin `reasoning_content`.", "", "All ten E002 runs recorded zero structured rejected tool calls, no permission warning, empty Devin stderr, return code 0, completed termination, and evaluator status `OK`. Ordinary shell/test failures inside a session are retained as agent/environment observations, not reclassified as infrastructure failures.", ""]
    lines += ["## Run-level tool behavior", "", "Source-edit counts distinguish direct source edits and observable shell mutations from generated/cache files. `post-edit calls` is a descriptive proxy for activity after the first observable source mutation, not a diagnosis of internal reasoning.", "", "| Run | Condition | Success | Wall s | Steps | Tools | exec/read/search/web/edit-write | Tests (pass/fail) | First source step | First test step | Source edits | Post-edit calls |", "|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|"]
    for run in runs:
        t = run["tool_behavior"]
        first_source = t["first_relevant_source_step"] or "—"
        first_test = t["first_test"]["step"] if t["first_test"] else "—"
        lines.append(f"| {run['run_id']} | {run['condition']} | {'1' if run['task_success'] else '0'} | {run['wall_time_seconds']:.3f} | {run['steps']} | {run['tool_calls']} | {t['shell_exec_calls']}/{t['read_calls']}/{t['search_calls']}/{t['web_calls']}/{t['edit_write_calls']} | {t['test_pass_count']}/{t['test_fail_count']} | {first_source} | {first_test} | {len(t['source_edit_operations'])} | {t['post_edit_observable_calls']} |")
    lines += ["", "The complete command-level inventory is in `results/experiment-002-tool-metrics.csv` and the structured JSON. Repeated commands, test status, ordinary nonzero shell exits, inspected target paths, and final observable messages are preserved there.", ""]
    condition_summary = data["condition_summary"]
    lines += ["## Condition aggregates", "", "| Condition | Solved | Wall total / mean / median s | Steps total / mean | Tool calls | Prompt / completion / cached tokens | Source + / - | All changed files | Generated/environment files |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for condition in ("M", "X"):
        aggregate = condition_summary[condition]
        lines.append(f"| {condition} | {aggregate['solved']}/5 | {aggregate['total_wall_time_seconds']:.3f} / {aggregate['mean_wall_time_seconds']:.3f} / {aggregate['median_wall_time_seconds']:.3f} | {aggregate['total_steps']} / {aggregate['mean_steps']:.3f} | {aggregate['total_tool_calls']} | {aggregate['tokens']['prompt']} / {aggregate['tokens']['completion']} / {aggregate['tokens']['cached']} | +{aggregate['total_source_additions']} / -{aggregate['total_source_deletions']} | {aggregate['total_changed_files']} | {aggregate['total_changed_files'] - 5} |")
    ratios = data["max_over_medium_ratios"]
    lines += ["", f"Max/Medium ratios from these aggregate totals are in the JSON: total wall {ratios['max_over_medium_total_wall_time_seconds']:.3f}×, mean wall {ratios['max_over_medium_mean_wall_time_seconds']:.3f}×, median wall {ratios['max_over_medium_median_wall_time_seconds']:.3f}×, total steps {ratios['max_over_medium_total_steps']:.3f}×, total tool calls {ratios['max_over_medium_total_tool_calls']:.3f}×, prompt tokens {ratios['max_over_medium_prompt_tokens']:.3f}×, completion tokens {ratios['max_over_medium_completion_tokens']:.3f}×, and all changed files {ratios['max_over_medium_total_changed_files']:.3f}×. The last ratio is dominated by generated virtualenv/cache files and is not a source-complexity ratio.", ""]
    lines += ["## Evaluator outcome ledger", "", "| Run | Public | Held-out | Regression | TASK_SUCCESS | Interventions | Termination |", "|---|---|---|---|---:|---:|---|"]
    for run in runs:
        evaluator = run["evaluator"]
        lines.append(f"| {run['run_id']} | {evaluator['public'].get('overall', '—')} | {evaluator['heldout'].get('overall', '—')} | {evaluator['regression'].get('overall', '—')} | {'1' if run['task_success'] else '0'} | {len(evaluator.get('interventions') or [])} | {run['termination_reason']} |")
    lines += ["", "The held-out evaluator was external to the agent workspace and was run only after the session closed. The `OK` statuses here mean evaluation infrastructure completed; the tqdm-Max held-out assertion itself failed and therefore TASK_SUCCESS was 0.", ""]
    lines += ["## Source-only patch metrics", "", "| Run | Source file | Source + | Source - | All changed files | Generated/environment files | Recorded all-file + / - |", "|---|---|---:|---:|---:|---:|---:|"]
    for run in runs:
        p = run["patch"]
        generated = run["patch"]["changed_file_count"] - len(p["source_files"])
        lines.append(f"| {run['run_id']} | {', '.join(p['source_files']) or '—'} | {p['source_additions']} | {p['source_deletions']} | {p['changed_file_count']} | {generated} | {p['raw_recorded_additions']} / {p['raw_recorded_deletions']} |")
    lines += ["", "The all-file records overstate code churn for Black-X and Scrapy-X because their preserved final filesystem records include virtualenv and bytecode/cache files. The source-only diffs are +10/-1 for both Black runs, +4 to +6/-1 to -2 for Scrapy, +25/-7 for FastAPI, +6/-0 or +2/-0 for tqdm, and +1/-1 for Tornado.", ""]
    lines += ["## Case deep dives", ""]
    deep = {
        "black-16": "Both conditions inspected the symlink regression and the `gen_python_files_in_dir` implementation, reproduced the outside-root `ValueError`, and applied the same observable try/except-and-skip behavior. Their source diffs are identical at the recorded patch level (+10/-1), both passed the public, held-out, and regression evaluators. Max’s +1,512 changed-file record is almost entirely `.venv`/cache churn; Medium’s 13 files are mostly bytecode/cache plus one source file.",
        "fastapi-3": "Medium and Max both explored `fastapi/routing.py` and implemented recursive response-content preparation. Both passed all eight public checks, the independent nested-list/nested-map held-out checks, and the regression check. Max used 69 steps, 71 tool calls, six web-search calls, and 1,137.750 seconds versus Medium’s 35 steps, 30 tool calls, and 299.332 seconds. The source diff shape was +25/-7 for both; the recorded source text differs in formatting and parameter handling details, so behavioral success—not patch identity—is the relevant result.",
        "scrapy-3": "Both found the redirect middleware path and addressed the extra-slash protocol-relative Location behavior. Medium’s source diff was +6/-2 and Max’s +4/-1; both passed the public redirect test, independent HTTPS/GET held-out test, and regression subset. Max spent 1,380.464 seconds and recorded 135 tool calls, while Medium spent 817.861 seconds and recorded 59. Max’s 1,663 changed files were dominated by a generated `.venv` and bytecode/cache entries. The observable final messages explicitly describe the URL normalization; no hidden reasoning is used here.",
        "tqdm-5": "This is the only pair that separated on correctness. Medium computed an inferred total for a sized iterable inside the disabled path and passed the held-out assertion. Max initialized `self.total` and `self.leave` but did not infer `len(iterable)` before returning; the held-out test therefore observed `progress.total is None` while public `test_bool` and the two regression checks passed. Max used 42 tools/21 shell commands and 405.290 seconds versus Medium’s 14 tools/12 shell commands and 157.312 seconds. More exploration reached the right state-initialization area but did not produce a complete behavioral fix.",
        "tornado-13": "Both identified the unsafe `start_line.method` access for response start lines and made the same one-line defensive change (+1/-1). Both passed the public HTTP/1.0 test, the independent bodyless-204 held-out socket test, and the regression subset. Max used 36 steps and 326.457 seconds versus Medium’s 33 steps and 175.535 seconds; the final outcome was unchanged.",
    }
    for case_id in CASE_INFO:
        lines += [f"### {case_id}", "", CASE_INFO[case_id]["behavior"], "", deep[case_id], ""]
    lines += ["## Paired Medium-versus-Max summary", "", "| Case | Outcome | Max − Medium wall s | Max − Medium steps | Max − Medium tool calls | Source patch identical | Interpretation |", "|---|---|---:|---:|---:|---|---|"]
    for pair in pairs:
        delta = pair["max_minus_medium"]
        lines.append(f"| {pair['case_id']} | {pair['outcome']} | {delta['wall_time_seconds']:.3f} | {delta['steps']:.0f} | {delta['tool_calls']:.0f} | {'yes' if pair['source_patch_identical'] else 'no'} | {pair['interpretation']} |")
    lines += ["", "Observed: Max used more wall time in every pair; it used more steps in four pairs and more tool calls in every pair. The paired result was both-successful for Black, FastAPI, Scrapy, and Tornado, and Medium-only for tqdm.", "", "Suggestive: on these cases, higher effort coincided with more exploration and environment/dependency work, especially FastAPI-X and Scrapy-X, without improving the aggregate score. This is descriptive association only.", "", "Not supported: a causal claim that Max is slower or less capable in general; statistical significance; reconstruction of hidden model reasoning; or treating virtualenv/cache churn as implementation complexity.", ""]
    lines += ["## Human reference comparison", "", "Reference patches were read evaluator-side only after both paired sessions were closed. All ten agent patches touched the reference target source file, but no agent patch is required to match the human implementation. Reference and agent source-only metrics are in `results/experiment-002-source-patch-metrics.csv` and the JSON.", "", "| Case | Human reference | Medium source diff | Max source diff | Behavioral outcome |", "|---|---|---:|---:|---|"]
    for case_id in CASE_INFO:
        ref = data["references"][case_id]
        medium = next(run for run in runs if run["case_id"] == case_id and run["condition"] == "M")
        maximum = next(run for run in runs if run["case_id"] == case_id and run["condition"] == "X")
        lines.append(f"| {case_id} | +{ref.get('additions', '—')}/-{ref.get('deletions', '—')} in {', '.join(ref.get('changed_files', []))} | +{medium['patch']['source_additions']}/-{medium['patch']['source_deletions']} | +{maximum['patch']['source_additions']}/-{maximum['patch']['source_deletions']} | {('both pass' if medium['task_success'] and maximum['task_success'] else 'Medium only')} |")
    lines += ["", "Black’s agents used a shorter equivalent source change than the reference. FastAPI’s agents matched the reference line counts but are not text-identical evidence of copying. Scrapy, tqdm, and Tornado used alternative source diffs; tqdm-Max’s alternative was behaviorally incomplete. These comparisons are descriptive and evaluator-side only.", ""]
    lines += ["## E001 to E002 contrast", "", "E001 recorded 0/5 for both conditions, but its noninteractive `accept-edits` mode rejected required tools and produced empty patches; it is invalid as a capability comparison. E002 changed only the execution permission boundary while preserving the cases, prompts, models, order, scoring, and intervention policy, and ran inside the isolated disposable container. E002 therefore demonstrates the effect of making autonomous tool use operational in this harness, not a clean model-only comparison with E001.", ""]
    lines += ["## Reproducibility and security notes", "", "The raw E002 result directories remain locally ignored and preserve the original exports, stdout/stderr, patches, evaluator output, and container metadata. Committed public artifacts are sanitized derivatives. No Devin or benchmark case was run during this analysis, no result/evaluator outcome was changed, and no Experiment 003 was started.", "", "Generated outputs:", "", "- `results/experiment-002-forensics.json`", "- `results/experiment-002-tool-metrics.csv`", "- `results/experiment-002-source-patch-metrics.csv`", "- `reports/experiment-002-forensic-analysis.md`", "", "The pre-commit scan of these generated artifacts found no credentials, tokens, cookies, authorization headers, private URLs, host paths, or environment secrets. Raw local artifacts are not included in this public report.", ""]
    return "\n".join(lines).rstrip() + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS_ROOT)
    parser.add_argument("--public-root", type=Path, default=DEFAULT_PUBLIC_ROOT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--runs-manifest", type=Path, default=REPO_ROOT / "manifests/experiment-002-runs.json")
    parser.add_argument("--reference-root", type=Path)
    parser.add_argument("--forensics", type=Path, default=DEFAULT_FORENSICS)
    parser.add_argument("--tool-csv", type=Path, default=DEFAULT_TOOL_CSV)
    parser.add_argument("--patch-csv", type=Path, default=DEFAULT_PATCH_CSV)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args(argv)
    data = build_analysis(args)
    args.forensics.parent.mkdir(parents=True, exist_ok=True)
    args.forensics.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    tool_rows: List[Dict[str, Any]] = []
    patch_rows: List[Dict[str, Any]] = []
    for run in data["runs"]:
        t = run["tool_behavior"]
        tool_rows.append({
            "run_id": run["run_id"], "case_id": run["case_id"], "condition": run["condition"], "model": run["model"],
            "task_success": int(bool(run["task_success"])), "wall_time_seconds": run["wall_time_seconds"], "steps": run["steps"],
            "tool_calls": run["tool_calls"], "exec_calls": t["shell_exec_calls"], "read_calls": t["read_calls"],
            "search_calls": t["search_calls"], "web_calls": t["web_calls"], "edit_write_calls": t["edit_write_calls"],
            "source_edit_operations": len(t["source_edit_operations"]), "source_edit_revision_evidence": int(t["source_edit_revision_evidence"]),
            "test_attempts": t["test_attempt_count"], "test_passes": t["test_pass_count"], "test_failures": t["test_fail_count"],
            "tests_after_first_source_edit": t["tests_after_first_source_edit"], "post_edit_observable_calls": t["post_edit_observable_calls"],
            "environment_dependency_calls": t["environment_dependency_calls"], "ordinary_shell_failures": len(t["ordinary_shell_failures"]),
            "rejected_tool_calls": len(run["rejected_tool_calls"]),
        })
        patch_rows.append({
            "run_id": run["run_id"], "case_id": run["case_id"], "condition": run["condition"], "source_files": ";".join(run["patch"]["source_files"]),
            "source_additions": run["patch"]["source_additions"], "source_deletions": run["patch"]["source_deletions"],
            "source_changed_lines": run["patch"]["source_additions"] + run["patch"]["source_deletions"],
            "all_changed_files": run["patch"]["changed_file_count"], "generated_or_environment_files": run["patch"]["changed_file_count"] - len(run["patch"]["source_files"]),
            "source_diff_sha256": run["patch"]["source_diff_sha256"], "all_recorded_additions": run["patch"]["raw_recorded_additions"], "all_recorded_deletions": run["patch"]["raw_recorded_deletions"],
            "human_reference_files": ";".join(run["reference_comparison"]["reference_files"]), "human_reference_additions": run["reference_comparison"]["reference_additions"],
            "human_reference_deletions": run["reference_comparison"]["reference_deletions"], "source_file_overlap": ";".join(run["reference_comparison"]["agent_source_file_overlap"]),
        })
    write_csv(args.tool_csv, tool_rows, list(tool_rows[0]))
    write_csv(args.patch_csv, patch_rows, list(patch_rows[0]))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report_text(data), encoding="utf-8")
    print(json.dumps({"status": "ok", "runs": len(data["runs"]), "forensics": str(args.forensics), "report": str(args.report)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
