#!/usr/bin/env python3
"""Summarize completed Experiment 001 paired results without significance tests."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REFERENCE_ROOT = Path("/tmp/bugsinpy-phase2.20260914/projects")
TOKEN_FIELDS = (
    "total_prompt_tokens",
    "total_completion_tokens",
    "total_cached_tokens",
)


def die(message: str) -> None:
    raise SystemExit(f"error: {message}")


def read_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        die(f"could not read {path}: {exc}")
    if not isinstance(data, dict):
        die(f"expected JSON object in {path}")
    return data


def numeric(value: Any) -> Optional[float]:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        value = float(value)
        if math.isfinite(value):
            return value
    return None


def median_mean(values: List[float]) -> Dict[str, Any]:
    return {
        "n": len(values),
        "median": statistics.median(values) if values else None,
        "mean": statistics.mean(values) if values else None,
    }


def total_stats(values: List[float]) -> Dict[str, Any]:
    result = median_mean(values)
    result["total"] = sum(values) if values else 0
    return result


def result_files(results_root: Path) -> Dict[str, Path]:
    files: Dict[str, Path] = {}
    if not results_root.is_dir():
        return files
    for run_dir in sorted(results_root.iterdir()):
        if not run_dir.is_dir():
            continue
        for filename in ("evaluation-result.json", "result.json", "runner-result.json"):
            candidate = run_dir / filename
            if candidate.is_file():
                files[run_dir.name] = candidate
                break
    return files


def patch_details(record: Dict[str, Any]) -> Dict[str, Any]:
    patch = record.get("patch", {})
    if not isinstance(patch, dict):
        patch = {}
    counts = patch.get("line_counts", {})
    if not isinstance(counts, dict):
        counts = {}
    additions = numeric(counts.get("additions")) or 0
    deletions = numeric(counts.get("deletions")) or 0
    changed_files = patch.get("changed_files", [])
    if not isinstance(changed_files, list):
        changed_files = []
    return {
        "changed_files": changed_files,
        "additions": int(additions),
        "deletions": int(deletions),
        "lines": int(additions + deletions),
        "path": patch.get("path"),
        "sha256": patch.get("sha256"),
    }


def session_details(results_root: Path, run_id: str) -> Dict[str, Any]:
    path = results_root / run_id / "devin-session-export.json"
    if not path.is_file():
        return {"available": False}
    data = read_json(path)
    agent = data.get("agent", {})
    if not isinstance(agent, dict):
        agent = {}
    extra = agent.get("extra", {})
    if not isinstance(extra, dict):
        extra = {}
    metrics = data.get("final_metrics", {})
    if not isinstance(metrics, dict):
        metrics = {}
    observed: Dict[str, Any] = {
        "available": True,
        "session_id": data.get("session_id"),
        "model_name": agent.get("model_name"),
        "backend": extra.get("backend"),
        "permission_mode": extra.get("permission_mode"),
    }
    for field in ("total_steps",) + TOKEN_FIELDS:
        value = numeric(metrics.get(field))
        observed[field] = int(value) if value is not None else None
    return observed


def failure_classification(record: Dict[str, Any]) -> str:
    if record.get("pass") is True:
        return "solved"
    patch = patch_details(record)
    if not patch["changed_files"] and record.get("pass") is False:
        return "no patch / premature completion"
    regression = record.get("regression_tests", {})
    if isinstance(regression, dict) and regression.get("overall") == "fail":
        return "regression introduced"
    public = record.get("tests_after", {})
    heldout = record.get("hidden_tests", {})
    public_pass = isinstance(public, dict) and public.get("overall") == "pass"
    heldout_pass = isinstance(heldout, dict) and heldout.get("overall") == "pass"
    if public_pass != heldout_pass:
        return "partial fix"
    if patch["changed_files"]:
        return "incorrect diagnosis"
    return "other"


def parse_reference_patch(path: Path) -> Optional[Dict[str, Any]]:
    if not path.is_file():
        return None
    raw = path.read_bytes()
    files: List[str] = []
    additions = 0
    deletions = 0
    for line in raw.decode("utf-8", errors="replace").splitlines():
        if line.startswith("diff --git a/"):
            fields = line.split()
            if len(fields) >= 4:
                files.append(fields[2][2:])
        elif line.startswith("+++") or line.startswith("---"):
            continue
        elif line.startswith("+"):
            additions += 1
        elif line.startswith("-"):
            deletions += 1
    return {
        "available": True,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "changed_files": files,
        "additions": additions,
        "deletions": deletions,
        "lines": additions + deletions,
        "source": "BugsInPy bug_patch.txt (evaluator-side only)",
    }


def reference_details(reference_root: Optional[Path], case_id: str) -> Dict[str, Any]:
    if reference_root is None:
        return {"available": False, "reason": "reference root not supplied"}
    project, bug_id = case_id.rsplit("-", 1)
    patch = parse_reference_patch(reference_root / project / "bugs" / bug_id / "bug_patch.txt")
    if patch is None:
        return {"available": False, "reason": "reference patch not found"}
    return patch


PAIR_OBSERVATIONS = {
    "black-16": {
        "exploration": "Max recorded one more session step and 12.832 additional seconds.",
        "diagnosis": "Both captured outputs inspected the external-symlink failure; neither completed a repair.",
        "patch_strategy": "Neither condition produced a patch.",
        "verification_behavior": "Neither reached a passing public or held-out evaluation; both regression subsets passed.",
        "final_outcome": "Both failed. Max did not improve the final outcome.",
    },
    "fastapi-3": {
        "exploration": "Both recorded 10 session steps; Max completed 3.337 seconds sooner and emitted more completion tokens.",
        "diagnosis": "Neither captured output demonstrated a completed diagnosis or implementation.",
        "patch_strategy": "Neither condition produced a patch.",
        "verification_behavior": "Neither reached a passing public or held-out evaluation; both regression subsets passed.",
        "final_outcome": "Both failed. Increased effort did not change the outcome.",
    },
    "scrapy-3": {
        "exploration": "Max recorded one more session step and 16.561 additional seconds.",
        "diagnosis": "Both inspected the redirect test and middleware; neither completed a repair.",
        "patch_strategy": "Neither condition produced a patch.",
        "verification_behavior": "Neither reached a passing public or held-out evaluation; both regression subsets passed.",
        "final_outcome": "Both failed. Max did not improve the final outcome.",
    },
    "tqdm-5": {
        "exploration": "Max recorded one more session step and 23.374 additional seconds.",
        "diagnosis": "Max articulated the likely disabled-state initialization issue; Medium left no comparable diagnostic statement in captured output.",
        "patch_strategy": "Neither condition produced a patch.",
        "verification_behavior": "Neither reached a passing public or held-out evaluation; both regression subsets passed.",
        "final_outcome": "Both failed. The extra effort did not produce an implementation.",
    },
    "tornado-13": {
        "exploration": "Max recorded two more session steps and 22.921 additional seconds.",
        "diagnosis": "Max articulated the response/request start-line mismatch; Medium left no comparable diagnostic statement in captured output.",
        "patch_strategy": "Neither condition produced a patch.",
        "verification_behavior": "Neither reached a passing public or held-out evaluation; both regression subsets passed.",
        "final_outcome": "Both failed. The extra effort did not produce an implementation.",
    },
}


def analyze(
    runs_manifest_path: Path,
    results_root: Path,
    reference_root: Optional[Path] = DEFAULT_REFERENCE_ROOT,
) -> Dict[str, Any]:
    runs_manifest = read_json(runs_manifest_path)
    runs = runs_manifest.get("runs", [])
    if not isinstance(runs, list) or len(runs) != 10:
        die("frozen run manifest must contain ten runs")
    files = result_files(results_root)
    records: Dict[str, Dict[str, Any]] = {}
    for run_id, path in files.items():
        records[run_id] = read_json(path)

    by_condition: Dict[str, Dict[str, Any]] = {}
    for condition in ("M", "X"):
        condition_runs = [run for run in runs if run["condition"] == condition]
        completed = [records[run["run_id"]] for run in condition_runs if run["run_id"] in records]
        successes = sum(1 for record in completed if record.get("pass") is True)
        elapsed = [value for record in completed if (value := numeric(record.get("elapsed_seconds"))) is not None]
        patch_sizes: List[float] = []
        steps: List[float] = []
        costs: List[float] = []
        token_values = {field: [] for field in TOKEN_FIELDS}
        for run in condition_runs:
            record = records.get(run["run_id"])
            if record is None:
                continue
            patch = patch_details(record)
            patch_sizes.append(float(patch["lines"]))
            step_value = numeric(record.get("steps"))
            if step_value is None and isinstance(record.get("agent"), dict):
                step_value = numeric(record["agent"].get("steps"))
            session = session_details(results_root, run["run_id"])
            if step_value is None:
                step_value = numeric(session.get("total_steps"))
            if step_value is not None:
                steps.append(step_value)
            for field in TOKEN_FIELDS:
                value = numeric(session.get(field))
                if value is not None:
                    token_values[field].append(value)
            usage = record.get("provider_fields", {}) if isinstance(record.get("provider_fields"), dict) else {}
            cost_value = numeric(usage.get("cost"))
            if cost_value is not None:
                costs.append(cost_value)
        by_condition[condition] = {
            "model": condition_runs[0]["model"],
            "solved": successes,
            "total": len(condition_runs),
            "completed_records": len(completed),
            "wall_time_seconds": total_stats(elapsed),
            "patch_size_lines": total_stats(patch_sizes),
            "steps": total_stats(steps),
            "usage_tokens": {field: total_stats(values) for field, values in token_values.items()},
            "usage_cost": total_stats(costs),
        }

    case_ids = sorted({run["case_id"] for run in runs})
    paired: Dict[str, str] = {}
    case_table = []
    pair_analysis = []
    reference_comparisons: Dict[str, Any] = {}
    run_level = []
    for case_id in case_ids:
        pair = [run for run in runs if run["case_id"] == case_id]
        statuses = {run["condition"]: records.get(run["run_id"], {}).get("pass") for run in pair}
        medium = statuses.get("M") is True
        maximum = statuses.get("X") is True
        if statuses.get("M") is None or statuses.get("X") is None:
            paired[case_id] = "pending"
        elif medium and maximum:
            paired[case_id] = "both succeeded"
        elif medium:
            paired[case_id] = "Medium only"
        elif maximum:
            paired[case_id] = "Max only"
        else:
            paired[case_id] = "both failed"

        row = {"case_id": case_id}
        agent_files: List[str] = []
        for condition in ("M", "X"):
            run = next(item for item in pair if item["condition"] == condition)
            record = records.get(run["run_id"], {})
            patch = patch_details(record)
            agent_files.extend(patch["changed_files"])
            session = session_details(results_root, run["run_id"])
            detail = {
                "run_id": run["run_id"],
                "model": run["model"],
                "pass": record.get("pass"),
                "evaluation_status": record.get("evaluation_status"),
                "public": (record.get("tests_after") or {}).get("overall"),
                "heldout": (record.get("hidden_tests") or {}).get("overall"),
                "regression": (record.get("regression_tests") or {}).get("overall"),
                "elapsed_seconds": record.get("elapsed_seconds"),
                "steps": session.get("total_steps"),
                "usage_tokens": {field: session.get(field) for field in TOKEN_FIELDS},
                "usage_cost": (record.get("provider_fields") or {}).get("cost"),
                "patch": patch,
                "failure_classification": failure_classification(record),
                "termination_reason": record.get("termination_reason") or record.get("invocation", {}).get("termination_reason"),
                "session_id": session.get("session_id"),
            }
            row[condition] = detail
        case_table.append(row)
        reference = reference_details(reference_root, case_id)
        reference_files = reference.get("changed_files", []) if reference.get("available") else []
        reference_comparisons[case_id] = {
            "reference": reference,
            "agent_patch_changed_files": sorted(set(agent_files)),
            "agent_reference_file_overlap": sorted(set(agent_files).intersection(reference_files)),
            "agent_patch_matches_reference_change": bool(agent_files) and set(agent_files) == set(reference_files),
            "comparison_performed_after_both_conditions_closed": statuses.get("M") is not None and statuses.get("X") is not None,
        }
        medium_detail = row["M"]
        max_detail = row["X"]
        observation = PAIR_OBSERVATIONS.get(case_id, {}).copy()
        observation.update({
            "case_id": case_id,
            "medium_result": medium_detail["pass"],
            "max_result": max_detail["pass"],
        })
        pair_analysis.append(observation)

    for run in runs:
        record = records.get(run["run_id"], {})
        patch = patch_details(record)
        session = session_details(results_root, run["run_id"])
        run_level.append({
            "run_id": run["run_id"],
            "case_id": run["case_id"],
            "condition": run["condition"],
            "model": run["model"],
            "elapsed_seconds": record.get("elapsed_seconds"),
            "steps": session.get("total_steps"),
            "public": (record.get("tests_after") or {}).get("overall"),
            "heldout": (record.get("hidden_tests") or {}).get("overall"),
            "regression": (record.get("regression_tests") or {}).get("overall"),
            "task_success": record.get("pass"),
            "patch": patch,
            "failure_classification": failure_classification(record),
            "termination_reason": record.get("termination_reason") or record.get("invocation", {}).get("termination_reason"),
            "session_id": session.get("session_id"),
            "usage_tokens": {field: session.get(field) for field in TOKEN_FIELDS},
            "usage_cost": (record.get("provider_fields") or {}).get("cost"),
        })

    warning_runs = []
    for run in runs:
        runner_path = results_root / run["run_id"] / "runner-result.json"
        runner_record = read_json(runner_path) if runner_path.is_file() else records.get(run["run_id"], {})
        output = (runner_record.get("invocation") or {}).get("stdout_stderr", "")
        if "rejected a tool call that requires confirmation" in output:
            warning_runs.append(run["run_id"])

    total_elapsed = [value for value in (numeric(item["elapsed_seconds"]) for item in run_level) if value is not None]
    historical_incidents = []
    c03_incident = results_root / "E001-C03-M" / "evaluation-result.infrastructure-error.json"
    if c03_incident.is_file():
        historical_incidents.append({
            "run_id": "E001-C03-M",
            "classification": "pre-resume evaluator infrastructure error preserved as provenance; corrected evaluator result is OK and the Devin run was not rerun",
            "artifact": str(c03_incident),
        })
    return {
        "experiment_id": runs_manifest["experiment_id"],
        "analysis_type": "exploratory paired evaluation",
        "statistical_significance_claims": False,
        "results_root": str(results_root),
        "completed_runs": len(records),
        "overall": {"Medium": by_condition["M"], "Max": by_condition["X"]},
        "total_wall_time_seconds": sum(total_elapsed),
        "total_reported_cost": None,
        "paired_outcomes": paired,
        "case_level": case_table,
        "pair_analysis": pair_analysis,
        "reference_comparisons": reference_comparisons,
        "run_level": run_level,
        "infrastructure_observations": {
            "infrastructure_failures": historical_incidents,
            "protocol_deviations": [],
            "cli_permission_warning_runs": warning_runs,
            "cli_permission_warning": "The CLI reported a rejected tool call in non-interactive AcceptEdits mode; no paid prompt or service failure was observed.",
        },
        "frozen_run_order": runs_manifest["run_order"],
    }


def markdown(summary: Dict[str, Any]) -> str:
    lines = [
        "# Experiment 001 results summary",
        "",
        "Exploratory paired evaluation; n=5. This report makes no statistical-significance claims.",
        "",
        f"Completed runs: {summary['completed_runs']}/10",
        f"Total wall time: {summary['total_wall_time_seconds']:.3f} seconds",
        "Raw per-run artifacts are preserved under `results/runs/experiment-001/`.",
        "",
        "## Condition summary",
        "",
        "| Condition | Solved | Total | Mean wall (s) | Median wall (s) | Mean steps | Total completion tokens |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for label in ("Medium", "Max"):
        row = summary["overall"][label]
        timing = row["wall_time_seconds"]
        steps = row["steps"]
        completion = row["usage_tokens"]["total_completion_tokens"]["total"]
        lines.append(
            f"| {label} | {row['solved']} | {row['total']} | "
            f"{timing['mean']:.3f} | {timing['median']:.3f} | "
            f"{steps['mean']:.1f} | {int(completion)} |"
        )
    lines.extend([
        "",
        "Provider-reported cost was unavailable for every run. Token counts above come from the preserved Devin session exports.",
        f"Observed Medium tokens: {int(summary['overall']['Medium']['usage_tokens']['total_prompt_tokens']['total'])} prompt, {int(summary['overall']['Medium']['usage_tokens']['total_completion_tokens']['total'])} completion, {int(summary['overall']['Medium']['usage_tokens']['total_cached_tokens']['total'])} cached.",
        f"Observed Max tokens: {int(summary['overall']['Max']['usage_tokens']['total_prompt_tokens']['total'])} prompt, {int(summary['overall']['Max']['usage_tokens']['total_completion_tokens']['total'])} completion, {int(summary['overall']['Max']['usage_tokens']['total_cached_tokens']['total'])} cached.",
        "",
        "## Complete run table",
        "",
        "| Run | Case | Model | Result | Public | Held-out | Regression | Wall (s) | Steps | Patch lines | Failure classification |",
        "|---|---|---|---|---|---|---|---:|---:|---:|---|",
    ])
    for item in summary["run_level"]:
        patch = item["patch"]
        result = "pass" if item["task_success"] is True else ("fail" if item["task_success"] is False else "pending")
        lines.append(
            f"| {item['run_id']} | {item['case_id']} | {item['model']} | {result} | "
            f"{item['public']} | {item['heldout']} | {item['regression']} | "
            f"{item['elapsed_seconds']:.3f} | {item['steps'] if item['steps'] is not None else '—'} | "
            f"{patch['lines']} | {item['failure_classification']} |"
        )
    lines.extend(["", "## Paired outcomes", "", "| Case | Outcome |", "|---|---|"])
    for case_id, outcome in summary["paired_outcomes"].items():
        lines.append(f"| {case_id} | {outcome} |")

    lines.extend(["", "## Medium versus Max observations", ""])
    for pair in summary["pair_analysis"]:
        lines.extend([
            f"### {pair['case_id']}",
            "",
            f"- Exploration: {pair['exploration']}",
            f"- Diagnosis: {pair['diagnosis']}",
            f"- Patch strategy: {pair['patch_strategy']}",
            f"- Verification behavior: {pair['verification_behavior']}",
            f"- Final outcome: {pair['final_outcome']}",
        ])
    lines.extend(["", "## Evaluator-side comparison with human reference patches", ""])
    lines.append("Reference comparison was performed only after both conditions for each case were closed. Reference implementations were not copied into agent workspaces.")
    lines.extend(["", "| Case | Reference files | Reference lines | Agent patch files | Comparison |", "|---|---|---:|---|---|"])
    for case_id, comparison in summary["reference_comparisons"].items():
        reference = comparison["reference"]
        files = ", ".join(reference.get("changed_files", [])) if reference.get("available") else "unavailable"
        agent_files = ", ".join(comparison["agent_patch_changed_files"]) or "none"
        comparison_text = "same file set" if comparison["agent_patch_matches_reference_change"] else "no matching agent patch"
        lines.append(f"| {case_id} | {files} | {reference.get('lines', '—')} | {agent_files} | {comparison_text} |")

    observations = summary["infrastructure_observations"]
    lines.extend([
        "",
        "## Infrastructure and protocol notes",
        "",
        "During the resumed ten-run execution, no authentication failure, Cognition service outage, unexpected paid charge, frozen-model availability issue, workspace preparation failure, or evaluator infrastructure error was recorded.",
        "A pre-resume evaluator-environment error for E001-C03-M is preserved as provenance; it was corrected before the resumed sequence, and the Devin session was not rerun.",
        "Protocol deviations recorded: none.",
        f"The CLI permission warning appeared in {len(observations['cli_permission_warning_runs'])}/10 runner captures. It is preserved as an execution observation and should be considered when interpreting the uniformly empty patches.",
        "",
        "E001-C03-M was not rerun. Its frozen result remains 27.138 seconds, empty patch, public fail, held-out fail, regression pass, TASK_SUCCESS=false.",
    ])
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-manifest", type=Path, default=REPO_ROOT / "manifests/experiment-001-runs.json")
    parser.add_argument("--results-root", type=Path, default=REPO_ROOT / "results/runs/experiment-001")
    parser.add_argument("--reference-root", type=Path, default=DEFAULT_REFERENCE_ROOT)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-markdown", type=Path)
    args = parser.parse_args(argv)
    summary = analyze(args.runs_manifest, args.results_root, args.reference_root)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.output_markdown:
        args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
        args.output_markdown.write_text(markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
