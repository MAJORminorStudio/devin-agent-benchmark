#!/usr/bin/env python3
"""Publish sanitized E003 evidence after all paired runs are closed."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "artifacts" / "experiment-003"
PRIVATE_ROOT: Path | None = None


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def clean_patch(value: str) -> str:
    return re.sub(r"[ \t]+$", "", value, flags=re.MULTILINE)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sanitize(value: Any) -> Any:
    if isinstance(value, str):
        if PRIVATE_ROOT is not None:
            value = value.replace(str(PRIVATE_ROOT), "/research-private")
        value = value.replace(str(Path.home()), "/user")
        value = re.sub(r"(?i)(?:[^\s/]+/)*credentials\.toml", "[REDACTED_CREDENTIAL_PATH]", value)
        value = re.sub(r"(?i)(authorization\s*:\s*bearer\s+)[^\s]+", r"\1[REDACTED_TOKEN]", value)
        value = re.sub(r"(?i)(cookie\s*:\s*)[^\r\n]+", r"\1[REDACTED_COOKIE]", value)
        value = re.sub(r"\b(?:ghp_|github_pat_)[A-Za-z0-9_-]+\b", "[REDACTED_TOKEN]", value)
        value = re.sub(r"\bsk-[A-Za-z0-9]{20,}\b", "[REDACTED_TOKEN]", value)
        return value
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, dict):
        return {key: sanitize(child) for key, child in value.items()}
    return value


def observations(step: dict[str, Any]) -> dict[str, str]:
    return {
        str(item.get("source_call_id")): str(item.get("content", ""))
        for item in step.get("observation", {}).get("results", [])
        if isinstance(item, dict)
    }


def public_session(session: dict[str, Any]) -> dict[str, Any]:
    steps = []
    for step in session.get("steps", []):
        if step.get("source") == "system":
            continue
        item: dict[str, Any] = {"step_id": step.get("step_id"), "timestamp": step.get("timestamp"), "source": step.get("source")}
        if step.get("message"):
            item["message"] = sanitize(step["message"])
        calls = []
        obs = observations(step)
        for call in step.get("tool_calls", []):
            call_id = str(call.get("tool_call_id"))
            public_call: dict[str, Any] = {"tool_call_id": call_id, "function_name": call.get("function_name"), "arguments": sanitize(call.get("arguments", {}))}
            if call_id in obs:
                content = sanitize(obs[call_id])
                public_call["observation"] = {"content": content[:4000], "content_sha256": sha256_bytes(obs[call_id].encode()), "content_length": len(obs[call_id])}
            calls.append(public_call)
        if calls:
            item["tool_calls"] = calls
        steps.append(item)
    return {"schema_version": 1, "session_id": session.get("session_id"), "steps": steps, "final_metrics": sanitize(session.get("final_metrics", {}))}


def public_evaluation(evaluation: dict[str, Any]) -> dict[str, Any]:
    keep = {key: evaluation.get(key) for key in ("evaluation_version", "evaluated_at_utc", "experiment_id", "case_id", "task_success", "evaluation_status", "changed_files", "patch", "reference_patch_compared", "metadata_project")}
    for name in ("public", "heldout", "regression"):
        data = evaluation.get(name, {})
        keep[name] = sanitize(data)
    return sanitize(keep)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    private = args.private_root.resolve()
    global PRIVATE_ROOT
    PRIVATE_ROOT = private
    summary = read_json(ROOT / "results" / "experiment-003-summary.json")
    runs_manifest = read_json(ROOT / "manifests" / "experiment-003-runs.json")
    freeze = read_json(ROOT / "manifests" / "experiment-003-freeze.json")
    if args.clean and PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir(parents=True, exist_ok=True)
    run_entries = []
    for record in summary["runs"]:
        run_id = record["run_id"]
        raw = private / "results" / run_id
        out = PUBLIC / run_id
        out.mkdir(parents=True, exist_ok=True)
        session = read_json(raw / "devin-session-export.json")
        evaluation = read_json(raw / "evaluation" / "evaluation-result.json")
        prompt = (private / "prompts" / f"{record['case_id']}.md").read_text(encoding="utf-8")
        metadata = {"schema_version": 1, "experiment_id": "experiment-003", "run_id": run_id, "case_id": record["case_id"], "condition": record["condition"], "model": record["model"], "session_id": record["session_id"], "prompt_sha256": sha256_bytes(prompt.encode()), "timing": {"started_at_utc": json.loads((raw / "container-run-result.json").read_text())["started_at_utc"], "ended_at_utc": json.loads((raw / "container-run-result.json").read_text())["ended_at_utc"], "wall_time_seconds": record["wall_time_seconds"]}, "termination_reason": record["termination_reason"], "interventions": 0, "metrics": {"steps": record["steps"], "tool_calls": record["tool_calls"], "tokens": record["tokens"]}, "patch": {"files_changed": record["files_changed"], "source_files_changed": record["source_files_changed"], "generated_or_environment_files": record["generated_or_environment_files"], "lines_added": record["lines_added"], "lines_deleted": record["lines_deleted"], "sha256": record["patch_sha256"]}, "evaluator": {"status": record["evaluation_status"], "task_success": record["task_success"], "public": record["public"], "heldout": record["heldout"], "regression": record["regression"]}, "reference_comparison": {"performed_after_pair_closure": True, "matches_human_reference_patch": record["matches_human_reference_patch"], "reference_patch_sha256": record["reference_patch_sha256"]}, "cost": None, "acus": None, "security_note": "Sanitized derivative; hidden reasoning and private paths are omitted."}
        write_json(out / "run-metadata.json", metadata)
        write_text(out / "prompt.md", prompt)
        write_text(out / "agent.patch", clean_patch((raw / "evaluation" / "agent.patch").read_text(encoding="utf-8", errors="replace")))
        write_json(out / "evaluation-result.json", public_evaluation(evaluation))
        write_json(out / "session-summary.json", {"schema_version": 1, "session_id": record["session_id"], "model": record["model"], "steps": record["steps"], "tool_calls": record["tool_calls"], "tool_calls_by_function": record["tool_calls_by_function"], "final_metrics": record["tokens"], "rejected_tool_calls": [], "intervention_count": 0})
        write_json(out / "tool-timeline.json", public_session(session))
        for filename in ("devin.stdout.txt", "devin.stderr.txt"):
            write_text(out / filename, sanitize((raw / filename).read_text(encoding="utf-8", errors="replace")))
        reference = private / "cases" / record["case_id"] / "reference.patch"
        write_text(out / "human-reference.patch", clean_patch(reference.read_text(encoding="utf-8", errors="replace")))
        hashes = {}
        for path in sorted(out.iterdir()):
            hashes[path.name] = {"sha256": sha256_bytes(path.read_bytes()), "bytes": path.stat().st_size}
        write_json(out / "artifact-hashes.json", {"schema_version": 1, "run_id": run_id, "published_files": hashes, "sanitization": "Private paths and high-confidence secrets were redacted; hidden reasoning and full workspaces were not published."})
        run_entries.append({"run_id": run_id, "case_id": record["case_id"], "condition": record["condition"], "model": record["model"], "published_files": {p.name: {"sha256": sha256_bytes(p.read_bytes()), "bytes": p.stat().st_size} for p in sorted(out.iterdir())}})
    case_descriptions = {"E003-N01": "Filesystem discovery must respect project boundaries when links point outside the root.", "E003-N02": "Tag-filtered catalogue views must be invalidated after record removal.", "E003-N03": "Nested record export must recursively convert values in supported containers.", "E003-N04": "Async session close must await worker cleanup and remain idempotent.", "E003-N05": "A line protocol parser must recover when a newer transaction begins before the previous one completes."}
    write_json(PUBLIC / "case-descriptions.json", case_descriptions)
    write_json(PUBLIC / "MANIFEST.json", {"schema_version": 1, "experiment_id": "experiment-003", "status": "completed", "control_commit": summary["control_commit"], "freeze_manifest_sha256": summary["freeze_manifest_sha256"], "novelty": "newly constructed and withheld cases; no training-data absence claim", "runs": run_entries, "publication_note": "Sanitized evidence only. Raw session exports and private evaluator source remain outside the public repository."})
    write_text(PUBLIC / "README.md", "# Experiment 003 public artifacts\n\nExperiment 003 is the five-case paired pilot on newly constructed software defects. Each case was run once with SWE-2 Medium and once with SWE-2 Max. The public derivatives include prompts, patches, evaluator outcomes, sanitized observable tool timelines, and run metadata. Hidden reasoning, private evaluator source, credentials, full workspaces, and raw environment dumps are excluded.\n\nMedium scored 5/5 and Max scored 5/5. See `../../reports/experiment-003-results.md` and `../../results/experiment-002-003-summary.json` for analysis.\n\nRun order is preserved in `../../manifests/experiment-003-runs.json`.\n")
    print(json.dumps({"published": len(run_entries), "output": str(PUBLIC), "freeze_status": freeze["freeze_status"]}, indent=2))


if __name__ == "__main__":
    main()
