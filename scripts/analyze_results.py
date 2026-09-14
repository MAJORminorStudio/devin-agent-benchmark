#!/usr/bin/env python3
"""Summarize completed Experiment 001 paired results without significance tests."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]


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
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) else None


def median_mean(values: List[float]) -> Dict[str, Any]:
    return {"n": len(values), "median": statistics.median(values) if values else None, "mean": statistics.mean(values) if values else None}


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


def analyze(runs_manifest_path: Path, results_root: Path) -> Dict[str, Any]:
    runs_manifest = read_json(runs_manifest_path)
    runs = runs_manifest.get("runs", [])
    if not isinstance(runs, list) or len(runs) != 10:
        die("frozen run manifest must contain ten runs")
    by_id = {run["run_id"]: run for run in runs}
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
        patch_sizes = []
        steps = []
        costs = []
        for record in completed:
            patch = record.get("patch", {}) if isinstance(record.get("patch"), dict) else {}
            counts = patch.get("line_counts", {}) if isinstance(patch.get("line_counts"), dict) else {}
            additions = numeric(counts.get("additions"))
            deletions = numeric(counts.get("deletions"))
            if additions is not None or deletions is not None:
                patch_sizes.append((additions or 0) + (deletions or 0))
            step_value = numeric(record.get("steps"))
            if step_value is None and isinstance(record.get("agent"), dict):
                step_value = numeric(record["agent"].get("steps"))
            if step_value is not None:
                steps.append(step_value)
            usage = record.get("provider_fields", {}) if isinstance(record.get("provider_fields"), dict) else {}
            cost_value = numeric(usage.get("cost"))
            if cost_value is not None:
                costs.append(cost_value)
        by_condition[condition] = {
            "model": condition_runs[0]["model"],
            "solved": successes,
            "total": len(condition_runs),
            "completed_records": len(completed),
            "wall_time_seconds": median_mean(elapsed),
            "patch_size_lines": median_mean(patch_sizes),
            "steps": median_mean(steps),
            "usage_cost": median_mean(costs),
        }

    paired: Dict[str, str] = {}
    for case_id in sorted({run["case_id"] for run in runs}):
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

    case_table = []
    for case_id in sorted({run["case_id"] for run in runs}):
        row = {"case_id": case_id}
        for condition in ("M", "X"):
            run = next(item for item in runs if item["case_id"] == case_id and item["condition"] == condition)
            record = records.get(run["run_id"], {})
            row[condition] = {"run_id": run["run_id"], "model": run["model"], "pass": record.get("pass"), "elapsed_seconds": record.get("elapsed_seconds"), "termination_reason": record.get("termination_reason") or record.get("invocation", {}).get("termination_reason")}
        case_table.append(row)

    return {
        "experiment_id": runs_manifest["experiment_id"],
        "analysis_type": "exploratory paired evaluation",
        "statistical_significance_claims": False,
        "results_root": str(results_root),
        "completed_runs": len(records),
        "overall": {"Medium": by_condition["M"], "Max": by_condition["X"]},
        "paired_outcomes": paired,
        "case_level": case_table,
        "frozen_run_order": runs_manifest["run_order"],
    }


def markdown(summary: Dict[str, Any]) -> str:
    lines = [
        "# Experiment 001 results summary",
        "",
        "Exploratory paired evaluation; n=5. This report makes no statistical-significance claims.",
        "",
        f"Completed runs: {summary['completed_runs']}/10",
        "",
        "| Condition | Solved | Total | Median wall time (s) | Mean wall time (s) |",
        "|---|---:|---:|---:|---:|",
    ]
    for label in ("Medium", "Max"):
        row = summary["overall"][label]
        timing = row["wall_time_seconds"]
        lines.append(f"| {label} | {row['solved']} | {row['total']} | {timing['median'] if timing['median'] is not None else '—'} | {timing['mean'] if timing['mean'] is not None else '—'} |")
    lines.extend(["", "## Paired outcomes", "", "| Case | Outcome |", "|---|---|"])
    for case_id, outcome in summary["paired_outcomes"].items():
        lines.append(f"| {case_id} | {outcome} |")
    lines.extend(["", "## Case-level results", "", "| Case | Medium | Max |", "|---|---|---|"])
    for row in summary["case_level"]:
        def status(condition: str) -> str:
            value = row[condition]["pass"]
            return "pending" if value is None else ("pass" if value else "fail")
        lines.append(f"| {row['case_id']} | {status('M')} | {status('X')} |")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-manifest", type=Path, default=REPO_ROOT / "manifests/experiment-001-runs.json")
    parser.add_argument("--results-root", type=Path, default=REPO_ROOT / "results/runs/experiment-001")
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-markdown", type=Path)
    args = parser.parse_args(argv)
    summary = analyze(args.runs_manifest, args.results_root)
    if args.output_json:
        args.output_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.output_markdown:
        args.output_markdown.write_text(markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
