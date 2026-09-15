#!/usr/bin/env python3
"""Publish sanitized, per-run public evidence for Experiments 001 and 002.

This script deliberately reads only the benchmark repository, its ignored run
artifacts, and the frozen manifests/prompts. It never reads credentials or
any external research infrastructure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOT = ROOT / "artifacts"
E001_RAW = ROOT / "results" / "runs" / "experiment-001"
E002_RAW = ROOT / "results" / "runs" / "experiment-002"
E001_MANIFEST = ROOT / "manifests" / "experiment-001.json"
E001_RUNS = ROOT / "manifests" / "experiment-001-runs.json"
E002_CONFIG = ROOT / "manifests" / "experiment-002-config.json"
E002_RUNS = ROOT / "manifests" / "experiment-002-runs.json"


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def compact_text(value: str, limit: int = 4000) -> str:
    if len(value) <= limit:
        return value
    head = max(0, limit - 500)
    return value[:head] + "\n...[TRUNCATED FOR PUBLIC DERIVATIVE]...\n" + value[-450:]


def sanitize_string(value: str) -> str:
    """Remove machine-specific paths and high-confidence secrets only."""
    replacements = [
        (r"/private/tmp/devin-agent-benchmark-e002\.[^/\s]+/[^/\s]+/agent-workspace", "/agent-workspace"),
        (r"/private/tmp/devin-agent-benchmark-e002\.[^/\s]+/[^/\s]+/output", "/run-artifacts"),
        (r"/private/tmp/devin-agent-benchmark-e002\.[^/\s]+", "/experiment-002-local"),
        (r"/Volumes/Research/devin-agent-benchmark-e001-work/[^/\s]+", "/agent-workspace"),
        (r"/Volumes/Research/devin-agent-benchmark-evaluator-envs/[^/\s]+", "/evaluator-env"),
        (r"/Volumes/Research/devin-agent-benchmark", "/benchmark"),
        (r"/Users/dippo/\.local/share/devin/credentials\.toml", "[REDACTED_CREDENTIAL_PATH]"),
        (r"/Users/dippo/\.local/share/devin", "/devin-data"),
        (r"/Users/dippo/\.pyenv/versions/[^/\s]+", "/python-runtime"),
        (r"/Users/dippo", "/user"),
        (r"/private/var/folders/[^/]+/[^/]+/T/[^/\s]+", "/tmp/host-temp"),
        (r"/tmp/bench-[^/\s]+", "/tmp/benchmark-env"),
        (r"/tmp/devin-overflows-[^/\s]+", "/tmp/devin-overflow"),
        (r"(https?://)[^/\s:@]+:[^@/\s]+@", r"\1[REDACTED_PRIVATE_URL]@"),
    ]
    result = value
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result)

    secret_patterns = [
        (r"(?i)(authorization\s*:\s*bearer\s+)[^\s]+", r"\1[REDACTED_TOKEN]"),
        (r"(?i)(cookie\s*:\s*)[^\r\n]+", r"\1[REDACTED_COOKIE]"),
        (r"(?i)(set-cookie\s*:\s*)[^\r\n]+", r"\1[REDACTED_COOKIE]"),
        (r"\b(?:ghp_|github_pat_)[A-Za-z0-9_-]+\b", "[REDACTED_TOKEN]"),
        (r"\bAKIA[0-9A-Z]{16}\b", "[REDACTED_TOKEN]"),
        (r"\bsk-[A-Za-z0-9]{20,}\b", "[REDACTED_TOKEN]"),
        (r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", "[REDACTED_PRIVATE_KEY]"),
    ]
    for pattern, replacement in secret_patterns:
        result = re.sub(pattern, replacement, result, flags=re.DOTALL if "PRIVATE KEY" in pattern else 0)
    return result


def sanitize(value: Any, text_limit: Optional[int] = None) -> Any:
    if isinstance(value, str):
        result = sanitize_string(value)
        return compact_text(result, text_limit) if text_limit else result
    if isinstance(value, list):
        return [sanitize(item, text_limit=text_limit) for item in value]
    if isinstance(value, dict):
        return {key: sanitize(child, text_limit=text_limit) for key, child in value.items()}
    return value


def raw_paths(experiment: str, run_id: str) -> Tuple[Path, Dict[str, Path]]:
    root = (E001_RAW if experiment == "experiment-001" else E002_RAW) / run_id
    if experiment == "experiment-001":
        names = {
            "runner-result.json": root / "runner-result.json",
            "evaluation-result.json": root / "evaluation-result.json",
            "devin-session-export.json": root / "devin-session-export.json",
            "agent.patch": root / "agent.patch",
        }
        error = root / "evaluation-result.infrastructure-error.json"
        if error.exists():
            names["evaluation-result.infrastructure-error.json"] = error
    else:
        names = {
            "runner-result.json": root / "output" / "runner-result.json",
            "container-run-result.json": root / "output" / "container-run-result.json",
            "evaluation-result.json": root / "output" / "evaluation-result.json",
            "devin-session-export.json": root / "output" / "devin-session-export.json",
            "agent.patch": root / "output" / "agent.patch",
            "devin.stdout.txt": root / "output" / "devin.stdout.txt",
            "devin.stderr.txt": root / "output" / "devin.stderr.txt",
            "runner-adapter.stdout.txt": root / "output" / "runner-adapter.stdout.txt",
            "runner-adapter.stderr.txt": root / "output" / "runner-adapter.stderr.txt",
            "agent-workspace.baseline.json": root / "agent-workspace.baseline.json",
            "agent-workspace.export.json": root / "agent-workspace.export.json",
            "agent-workspace.leak-audit.json": root / "agent-workspace.leak-audit.json",
        }
    return root, {name: path for name, path in names.items() if path.exists()}


def case_records() -> Dict[str, Dict[str, Any]]:
    return {case["case_id"]: case for case in read_json(E001_MANIFEST)["cases"]}


def run_records(experiment: str) -> List[Dict[str, Any]]:
    path = E001_RUNS if experiment == "experiment-001" else E002_RUNS
    return read_json(path)["runs"]


def get_data(paths: Dict[str, Path], name: str) -> Dict[str, Any]:
    return read_json(paths[name])


def session_paths(paths: Dict[str, Path]) -> Path:
    return paths["devin-session-export.json"]


def observation_map(step: Dict[str, Any]) -> Dict[str, str]:
    results = step.get("observation", {}).get("results", [])
    result: Dict[str, str] = {}
    for item in results:
        if isinstance(item, dict):
            result[str(item.get("source_call_id"))] = str(item.get("content", ""))
    return result


def operation_for(function_name: str, arguments: Dict[str, Any]) -> Tuple[str, str]:
    command = str(arguments.get("command", arguments.get("cmd", "")))
    if function_name in {"read", "grep", "glob", "search"}:
        return "repository/source inspection", "repository inspection"
    if function_name == "exec":
        if re.search(r"pip|python --version|python3 --version|which python", command):
            return "shell execution", "dependency/environment inspection"
        if re.search(r"pytest|unittest|nose", command):
            return "shell execution", "target test execution"
        return "shell execution", "repository or shell command"
    return "tool execution", "other tool operation"


def rejected_calls(session: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    found: List[Dict[str, Any]] = []
    for step in session.get("steps", []):
        if step.get("source") != "agent":
            continue
        observations = observation_map(step)
        for tool_call in step.get("tool_calls", []):
            call_id = str(tool_call.get("tool_call_id"))
            content = observations.get(call_id, "")
            if not re.search(r"Tool execution was rejected|Tool call canceled because another tool call", content, re.I):
                continue
            arguments = tool_call.get("arguments", {})
            category, attempted = operation_for(str(tool_call.get("function_name")), arguments)
            if "canceled because another" in content:
                status = "canceled_after_rejection"
            else:
                status = "rejected"
            found.append(
                {
                    "step_id": step.get("step_id"),
                    "tool_call_id": call_id,
                    "function_name": tool_call.get("function_name"),
                    "arguments": sanitize(arguments),
                    "status": status,
                    "rejection_message": sanitize_string(content.strip()),
                    "requested_category": category,
                    "attempted_operation": attempted,
                }
            )
    return found, None


def permission_warning(runner: Dict[str, Any]) -> Optional[str]:
    text = str(runner.get("invocation", {}).get("stdout_stderr", ""))
    match = re.search(r"warning: rejected a tool call[^\n]*", text)
    return sanitize_string(match.group(0)) if match else None


def public_tool_timeline(session: Dict[str, Any]) -> Dict[str, Any]:
    steps: List[Dict[str, Any]] = []
    for step in session.get("steps", []):
        public: Dict[str, Any] = {
            "step_id": step.get("step_id"),
            "timestamp": step.get("timestamp"),
            "source": step.get("source"),
        }
        if step.get("model_name"):
            public["model_name"] = step.get("model_name")
        if step.get("metrics"):
            public["metrics"] = sanitize(step.get("metrics"))
        if step.get("source") == "system":
            public["kind"] = "system_context_omitted"
        else:
            for field in ("message", "reasoning_content"):
                if step.get(field):
                    public[field] = sanitize(step.get(field), text_limit=5000)
            calls = []
            observations = observation_map(step)
            for tool_call in step.get("tool_calls", []):
                call_id = str(tool_call.get("tool_call_id"))
                call = {
                    "tool_call_id": call_id,
                    "function_name": tool_call.get("function_name"),
                    "arguments": sanitize(tool_call.get("arguments", {})),
                }
                if call_id in observations:
                    content = sanitize_string(observations[call_id])
                    call["observation"] = {
                        "content": compact_text(content),
                        "content_sha256": sha256_bytes(observations[call_id].encode("utf-8")),
                        "content_length": len(observations[call_id]),
                    }
                calls.append(call)
            if calls:
                public["tool_calls"] = calls
        steps.append(public)
    return {"schema_version": 1, "steps": steps}


def session_summary(session: Dict[str, Any], runner: Dict[str, Any], patch: bytes) -> Dict[str, Any]:
    source_counts = Counter(str(step.get("source")) for step in session.get("steps", []))
    function_counts = Counter(
        str(call.get("function_name"))
        for step in session.get("steps", [])
        for call in step.get("tool_calls", [])
    )
    all_tool_calls = [
        call
        for step in session.get("steps", [])
        for call in step.get("tool_calls", [])
    ]
    timestamps = [step.get("timestamp") for step in session.get("steps", []) if step.get("timestamp")]
    rejected, _ = rejected_calls(session)
    return {
        "schema_version": 1,
        "session_id": session.get("session_id"),
        "agent": sanitize(runner.get("agent", {})),
        "model": runner.get("agent", {}).get("model"),
        "total_steps": len(session.get("steps", [])),
        "source_step_counts": dict(sorted(source_counts.items())),
        "tool_call_count": len(all_tool_calls),
        "tool_calls_by_function": dict(sorted(function_counts.items())),
        "first_step_timestamp": min(timestamps) if timestamps else None,
        "last_step_timestamp": max(timestamps) if timestamps else None,
        "final_metrics": sanitize(session.get("final_metrics", {})),
        "permission_warning": permission_warning(runner),
        "rejected_tool_calls": rejected,
        "patch_empty": len(patch) == 0,
        "patch_sha256": sha256_bytes(patch),
    }


def source_paths(changed: Iterable[str]) -> Tuple[List[str], List[str]]:
    source: List[str] = []
    generated: List[str] = []
    for path in changed:
        if (
            "__pycache__/" in path
            or path.endswith(".pyc")
            or path.startswith(".venv/")
            or path.startswith("testenv/")
            or path.startswith("/tmp/venv/")
        ):
            generated.append(path)
        else:
            source.append(path)
    return sorted(source), sorted(generated)


def build_run(experiment: str, record: Dict[str, Any], cases: Dict[str, Dict[str, Any]]) -> None:
    run_id = record["run_id"]
    public_dir = PUBLIC_ROOT / experiment / run_id
    if public_dir.exists():
        shutil.rmtree(public_dir)
    _, paths = raw_paths(experiment, run_id)
    runner = get_data(paths, "runner-result.json")
    evaluation = get_data(paths, "evaluation-result.json")
    session = get_data(paths, "devin-session-export.json")
    patch = paths["agent.patch"].read_bytes()
    case = cases[evaluation["case_id"]]
    rejected, _ = rejected_calls(session)
    prompt = str(runner.get("prompt", ""))
    changed = evaluation.get("patch", {}).get("changed_files", [])
    source_changed, generated_changed = source_paths(changed)

    metadata: Dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": experiment,
        "run_id": run_id,
        "experiment_case_id": evaluation.get("experiment_case_id"),
        "case": {
            "case_id": case.get("case_id"),
            "source": case.get("source"),
            "project": case.get("project"),
            "bug_id": case.get("bug_id"),
            "original_repository": case.get("original_repository"),
        },
        "condition": record.get("condition", evaluation.get("condition")),
        "model": runner.get("agent", {}).get("model"),
        "effort_level": record.get("effort_level", evaluation.get("effort_level")),
        "session_id": session.get("session_id") or runner.get("provider_fields", {}).get("session_id"),
        "frozen_prompt": prompt,
        "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
        "timing": {
            "started_at": runner.get("started_at", evaluation.get("started_at")),
            "ended_at": runner.get("ended_at", evaluation.get("ended_at")),
            "elapsed_seconds": evaluation.get("elapsed_seconds", runner.get("elapsed_seconds")),
        },
        "termination_reason": evaluation.get("termination_reason", runner.get("termination_reason")),
        "interventions": evaluation.get("interventions", runner.get("interventions", [])),
        "runner": {
            "cli_version": runner.get("agent", {}).get("cli_version"),
            "permission_mode": runner.get("agent", {}).get("permission_mode")
            or next(
                (
                    runner.get("invocation", {}).get("command", [])[index + 1]
                    for index, item in enumerate(runner.get("invocation", {}).get("command", []))
                    if item == "--permission-mode" and index + 1 < len(runner.get("invocation", {}).get("command", []))
                ),
                None,
            ),
            "effective_permission_mode": runner.get("agent", {}).get("effective_permission_mode"),
            "fusion_enabled": runner.get("agent", {}).get("fusion_enabled"),
            "returncode": runner.get("invocation", {}).get("returncode"),
            "timed_out": runner.get("invocation", {}).get("timed_out"),
            "working_directory": sanitize_string(str(runner.get("invocation", {}).get("working_directory", ""))),
            "command": sanitize(runner.get("invocation", {}).get("command", [])),
        },
        "permission_warning": permission_warning(runner),
        "rejected_tool_calls": rejected,
        "patch_proof": {
            "patch_byte_length": len(patch),
            "patch_sha256": sha256_bytes(patch),
            "changed_files": changed,
            "line_counts": evaluation.get("patch", {}).get("line_counts", {}),
        },
        "evaluator": {
            "status": evaluation.get("evaluation_status"),
            "task_success": evaluation.get("task_success"),
            "public": evaluation.get("tests_after", {}).get("overall"),
            "heldout": evaluation.get("heldout_tests", {}).get("overall"),
            "regression": evaluation.get("regression_status"),
        },
    }
    if experiment == "experiment-001":
        metadata["empty_patch_proof"] = metadata["patch_proof"]
    if experiment == "experiment-002":
        command = runner.get("invocation", {}).get("command", [])
        metadata["isolation"] = {
            "execution": "disposable Docker container",
            "platform": "linux/arm64" if "linux/arm64" in command else None,
            "read_only_root": "--read-only" in command,
            "capabilities_dropped": "--cap-drop" in command and "ALL" in command,
            "no_new_privileges": "no-new-privileges:true" in command,
            "docker_socket_mounted": False,
            "privileged": False,
            "network": "e002-internal",
            "egress_proxy": "allowlisted proxy; host credential path redacted",
            "workspace_mounts": "one sanitized workspace and one fresh artifact directory",
            "credential_mounts": "one read-only Devin credential file; host pathname redacted",
        }
        metadata["provider_metrics"] = sanitize(runner.get("agent", {}).get("provider_metrics", {}))
    write_json(public_dir / "run-metadata.json", sanitize(metadata))
    write_text(public_dir / "prompt.md", sanitize_string(prompt))

    eval_public = sanitize(evaluation)
    write_json(public_dir / "evaluation-result.json", eval_public)
    write_text(public_dir / "agent.patch", sanitize_string(patch.decode("utf-8", errors="replace")))
    write_json(public_dir / "tool-timeline.json", public_tool_timeline(session))
    write_json(public_dir / "session-summary.json", session_summary(session, runner, patch))

    if experiment == "experiment-001":
        combined = str(runner.get("invocation", {}).get("stdout_stderr", ""))
        write_text(public_dir / "stdout.txt", sanitize_string(combined))
        write_text(public_dir / "stderr.txt", "")
    else:
        write_text(public_dir / "stdout.txt", sanitize_string(paths.get("devin.stdout.txt", Path()).read_text(errors="replace") if paths.get("devin.stdout.txt") else ""))
        write_text(public_dir / "stderr.txt", sanitize_string(paths.get("devin.stderr.txt", Path()).read_text(errors="replace") if paths.get("devin.stderr.txt") else ""))

    source_stat = {
        "patch_sha256": sha256_bytes(patch),
        "patch_byte_length": len(patch),
        "patch_is_empty": len(patch) == 0,
        "changed_files": changed,
        "source_files_changed": source_changed,
        "generated_or_environment_files": generated_changed,
        "line_counts": evaluation.get("patch", {}).get("line_counts", {}),
        "evaluator_task_success": evaluation.get("task_success"),
        "reference_comparison": evaluation.get("reference_comparison"),
    }
    write_json(public_dir / "source-diff-stat.json", sanitize(source_stat))

    baseline = paths.get("agent-workspace.baseline.json")
    baseline_entries = None
    if baseline:
        baseline_entries = len(read_json(baseline).get("entries", []))
    workspace_summary = {
        "baseline_entry_count": baseline_entries,
        "observed_changed_entry_count": len(changed),
        "source_files": source_changed,
        "generated_or_environment_files": generated_changed,
        "classification_counts": {
            "source": len(source_changed),
            "generated_or_environment": len(generated_changed),
        },
        "note": "Counts are based on the preserved final patch/file-change record. Full workspace trees and dependency environments are not published.",
    }
    write_json(public_dir / "workspace-change-summary.json", sanitize(workspace_summary))

    raw_hashes = {}
    for name, path in paths.items():
        raw_hashes[name] = {"sha256": sha256_file(path), "bytes": path.stat().st_size}
    public_hashes = {}
    for path in sorted(public_dir.iterdir()):
        if path.name == "artifact-hashes.json":
            continue
        public_hashes[path.name] = {"sha256": sha256_file(path), "bytes": path.stat().st_size}
    excluded = [
        {
            "artifact_class": "raw runner/evaluator/session/output metadata",
            "reason": "Unchanged files contain machine-specific host paths and execution metadata; sanitized derivatives are published.",
            "public_replacement": "run-metadata.json, evaluation-result.json, tool-timeline.json, session-summary.json, stdout.txt, stderr.txt",
        },
    ]
    if experiment == "experiment-002":
        excluded.append(
            {
                "artifact_class": "full agent workspace and baseline/generated dependency trees",
                "reason": "Contains excessive generated dependency/bytecode data and machine-specific paths; not needed to reconstruct the experiment.",
                "public_replacement": "agent.patch, source-diff-stat.json, workspace-change-summary.json, sanitized session export",
            }
        )
    if "evaluation-result.infrastructure-error.json" in paths:
        excluded.append(
            {
                "artifact_class": "original evaluator infrastructure-error record",
                "reason": "Contains local evaluator paths; a sanitized copy is published as evaluation-result.infrastructure-error.json.",
                "public_replacement": "evaluation-result.infrastructure-error.json",
            }
        )
    write_json(public_dir / "artifact-hashes.json", {
        "schema_version": 1,
        "run_id": run_id,
        "raw_local_artifacts": raw_hashes,
        "published_artifacts": public_hashes,
        "excluded_local_artifacts": excluded,
        "sanitization": "Only high-confidence secrets and machine-specific/private paths were redacted; benchmark source, commands, tool behavior, failures, patches, and outcomes were retained.",
    })

    # Publish a sanitized copy of the original E001 evaluator infrastructure error.
    error_path = paths.get("evaluation-result.infrastructure-error.json")
    if error_path:
        write_json(public_dir / "evaluation-result.infrastructure-error.json", sanitize(read_json(error_path)))
        # Refresh hashes now that the extra artifact exists.
        hashes = read_json(public_dir / "artifact-hashes.json")
        hashes["published_artifacts"]["evaluation-result.infrastructure-error.json"] = {
            "sha256": sha256_file(public_dir / "evaluation-result.infrastructure-error.json"),
            "bytes": (public_dir / "evaluation-result.infrastructure-error.json").stat().st_size,
        }
        write_json(public_dir / "artifact-hashes.json", hashes)

    # A full sanitized export is useful and remains small enough for these runs.
    sanitized_session: Dict[str, Any] = {
        "schema_version": session.get("schema_version"),
        "session_id": session.get("session_id"),
        "agent": sanitize(session.get("agent", {})),
        "steps": [],
        "final_metrics": sanitize(session.get("final_metrics", {})),
    }
    for step in session.get("steps", []):
        if step.get("source") == "system":
            sanitized_session["steps"].append({
                "step_id": step.get("step_id"),
                "timestamp": step.get("timestamp"),
                "source": "system",
                "message": "[SYSTEM_CONTEXT_OMITTED]",
            })
        else:
            sanitized_session["steps"].append(sanitize(step))
    write_json(public_dir / "devin-session-export.sanitized.json", sanitized_session)
    hashes = read_json(public_dir / "artifact-hashes.json")
    hashes["published_artifacts"]["devin-session-export.sanitized.json"] = {
        "sha256": sha256_file(public_dir / "devin-session-export.sanitized.json"),
        "bytes": (public_dir / "devin-session-export.sanitized.json").stat().st_size,
    }
    write_json(public_dir / "artifact-hashes.json", hashes)


def build_readme(experiment: str, records: List[Dict[str, Any]]) -> None:
    if experiment == "experiment-001":
        text = """# Experiment 001 public artifacts

Experiment 001 is preserved here as important provenance, but is **INVALID AS A CAPABILITY COMPARISON**. It used noninteractive `accept-edits`; required tool calls were rejected, so all ten agent patches were empty. The corrected evaluator result for E001-C03-M and the original evaluator infrastructure error are both published.

Each run directory contains the frozen prompt, model/condition/timing metadata, exact permission warning, rejected or canceled tool-call records, sanitized session evidence, evaluator result, empty-patch proof, and SHA-256 hashes. System boilerplate and private machine paths are omitted or standardized; benchmark commands, source observations, failures, rejected calls, and outcomes are retained.

The unchanged raw records remain local under the ignored `results/runs/experiment-001/` directory because they contain machine-specific paths. Their hashes and public replacements are documented in every run's `artifact-hashes.json`.

Run order:

""" + "\n".join("{}. {}".format(i, record["run_id"]) for i, record in enumerate(records, 1)) + "\n"
    else:
        text = """# Experiment 002 public artifacts

Experiment 002 is the isolated autonomous execution experiment. All ten frozen runs used the disposable linux/arm64 Docker path with dangerous permission mode / effective Bypass, read-only root, dropped capabilities, no-new-privileges, no Docker socket, no host/control-repository mounts, a single sanitized workspace, and the restricted egress proxy. Fusion was disabled and there were no substantive interventions or retries.

Each run directory publishes the frozen prompt, model/effort, session/timing metadata, sanitized tool timeline and session export, stdout/stderr, patch, evaluator result, source-only diff statistics, workspace-change classification, and hashes. The full generated workspaces and unchanged raw runner/session files remain local because they contain machine-specific paths or excessive dependency/bytecode data; exclusions and hashes are documented per run.

This experiment scored Medium 5/5 and Max 4/5. The sole failure was E002-C04-X (tqdm): public and regression checks passed, but the held-out sized-iterable behavior remained incorrect.

Run order:

""" + "\n".join("{}. {}".format(i, record["run_id"]) for i, record in enumerate(records, 1)) + "\n"
    write_text(PUBLIC_ROOT / experiment / "README.md", text)


def build_manifest(experiment: str, records: List[Dict[str, Any]]) -> None:
    runs = []
    for record in records:
        run_id = record["run_id"]
        directory = PUBLIC_ROOT / experiment / run_id
        files = {}
        for path in sorted(directory.iterdir()):
            files[path.name] = {"sha256": sha256_file(path), "bytes": path.stat().st_size}
        runs.append({
            "run_id": run_id,
            "case_id": record.get("case_id"),
            "condition": record.get("condition"),
            "model": record.get("model"),
            "published_files": files,
        })
    data: Dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": experiment,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "publication_policy": "Sanitized public derivatives of E001/E002 evidence; no credentials or private machine metadata.",
        "runs": runs,
    }
    if experiment == "experiment-001":
        data.update({
            "status": "invalid_as_capability_comparison",
            "reason": "Noninteractive accept-edits permission gating rejected required tool calls and produced empty patches.",
        })
    else:
        data.update({
            "status": "completed",
            "container_image": "devin-e002:3000.10.21@sha256:bb045374bc655c185cced99a6cb769a6695c88527fb432456eb8e0d6dd0e4bb6",
            "proxy_image": "e002-egress-proxy@sha256:adb28774da6dcb69e90bc670bc8942fccc86bf7656b6ce33c7dc2a09c8ccc395",
        })
    write_json(PUBLIC_ROOT / experiment / "MANIFEST.json", data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true", help="replace existing public artifact directories")
    args = parser.parse_args()
    if args.clean and PUBLIC_ROOT.exists():
        shutil.rmtree(PUBLIC_ROOT)
    PUBLIC_ROOT.mkdir(parents=True, exist_ok=True)
    cases = case_records()
    for experiment in ("experiment-001", "experiment-002"):
        records = run_records(experiment)
        for record in records:
            build_run(experiment, record, cases)
        build_readme(experiment, records)
        build_manifest(experiment, records)
    print("published", sum(1 for _ in PUBLIC_ROOT.rglob("run-metadata.json")), "run directories")


if __name__ == "__main__":
    main()
