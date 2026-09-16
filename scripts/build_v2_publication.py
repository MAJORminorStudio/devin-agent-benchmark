#!/usr/bin/env python3
"""Build the public v2 evidence package from closed canonical results.

The E003 case source and evaluator tests are released only after the ten runs
are closed.  This script copies those now-public artifacts into a clearly
separated evidence tree, reconstructs safe case metadata, and derives the v2
summary, CSV, charts, and report from the committed E002/E003 summaries.
It never reads raw Devin session exports.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
E003_PUBLIC = ROOT / "artifacts" / "experiment-003"
CHART_DIR = ROOT / "assets" / "charts"

E002_CASES = {
    "black-16": ("Black 16", "black", "16"),
    "fastapi-3": ("FastAPI 3", "fastapi", "3"),
    "scrapy-3": ("Scrapy 3", "scrapy", "3"),
    "tqdm-5": ("tqdm 5", "tqdm", "5"),
    "tornado-13": ("Tornado 13", "tornado", "13"),
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_public_tree(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for path in sorted(source.rglob("*")):
        if path.is_dir() or path.name in {".DS_Store"} or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def normalize_status(value: Any) -> str:
    if isinstance(value, bool):
        return "pass" if value else "fail"
    text = str(value).lower()
    if text in {"passed", "pass", "ok", "success"}:
        return "pass"
    if text in {"failed", "fail", "error"}:
        return "fail"
    return text


def e002_records() -> list[dict[str, Any]]:
    summary = read_json(ROOT / "results" / "experiment-002-summary.json")
    records = []
    for item in summary["runs"]:
        case_id = item["case_id"]
        label, project, bug_id = E002_CASES[case_id]
        records.append({
            "provenance": "historical",
            "experiment": "E002",
            "case_id": case_id,
            "label": label,
            "project": project,
            "bug_id": bug_id,
            "run_id": item["run_id"],
            "condition": item["condition"],
            "model": item["model"],
            "success": bool(item["task_success"]),
            "public": normalize_status(item["public_tests"]),
            "heldout": normalize_status(item["heldout_tests"]),
            "regression": normalize_status(item["regression_status"]),
            "wall_seconds": item["wall_time_seconds"],
            "steps": item["steps"],
            "tool_calls": item["tool_calls"],
            "prompt_tokens": item["tokens"]["prompt"],
            "completion_tokens": item["tokens"]["completion"],
            "cached_tokens": item["tokens"]["cached"],
            "source_files_changed": item["source_files_changed"],
            "lines_added": item["lines_added"],
            "lines_deleted": item["lines_deleted"],
            "files_changed": item["files_changed"],
            "generated_files": 0,
            "session_id": item["session_id"],
        })
    return records


def e003_records() -> list[dict[str, Any]]:
    summary = read_json(ROOT / "results" / "experiment-003-summary.json")
    projects = {
        "E003-N01": "asset-indexer",
        "E003-N02": "catalog-service",
        "E003-N03": "record-exporter",
        "E003-N04": "event-stream",
        "E003-N05": "line-protocol",
    }
    labels = {case["case_id"]: case["case_id"] for case in summary["case_set"]}
    records = []
    for item in summary["runs"]:
        records.append({
            "provenance": "novel",
            "experiment": "E003",
            "case_id": item["case_id"],
            "label": labels[item["case_id"]],
            "project": projects[item["case_id"]],
            "bug_id": "novel",
            "run_id": item["run_id"],
            "condition": item["condition"],
            "model": item["model"],
            "success": bool(item["task_success"]),
            "public": normalize_status(item["public"]),
            "heldout": normalize_status(item["heldout"]),
            "regression": normalize_status(item["regression"]),
            "wall_seconds": item["wall_time_seconds"],
            "steps": item["steps"],
            "tool_calls": item["tool_calls"],
            "prompt_tokens": item["tokens"]["prompt"],
            "completion_tokens": item["tokens"]["completion"],
            "cached_tokens": item["tokens"]["cached"],
            "source_files_changed": len(item["source_files_changed"]),
            "lines_added": item["lines_added"],
            "lines_deleted": item["lines_deleted"],
            "files_changed": len(item["files_changed"]),
            "generated_files": len(item["generated_or_environment_files"]),
            "session_id": item["session_id"],
        })
    return records


def stats(records: list[dict[str, Any]], field: str) -> dict[str, float | int]:
    values = [float(row[field]) for row in records]
    return {"n": len(values), "total": sum(values), "mean": statistics.mean(values), "median": statistics.median(values)}


def build_case_evidence(private_root: Path) -> list[dict[str, Any]]:
    cases = []
    descriptions = {
        "E003-N01": "Filesystem discovery must respect project boundaries when links point outside the root.",
        "E003-N02": "Tag-filtered catalogue views must be invalidated after record removal.",
        "E003-N03": "Nested record export must recursively convert values in supported containers.",
        "E003-N04": "Async session close must await worker cleanup and remain idempotent.",
        "E003-N05": "A line protocol parser must recover when a newer transaction begins before the previous one completes.",
    }
    for case_id in sorted(descriptions):
        source = private_root / "cases" / case_id
        metadata = read_json(source / "metadata.json")
        out = E003_PUBLIC / "cases" / case_id
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        copy_public_tree(source / "buggy", out / "buggy")
        copy_public_tree(source / "fixed", out / "fixed")
        copy_public_tree(private_root / "evaluation" / case_id, out / "evaluator")
        reference = (source / "reference.patch").read_text(encoding="utf-8", errors="replace")
        (out / "reference.patch").write_text(re.sub(r"[ \t]+$", "", reference, flags=re.MULTILINE), encoding="utf-8")
        public_metadata = {
            "schema_version": 1,
            "experiment_id": "experiment-003",
            "case_id": case_id,
            "project_name": metadata["project_name"],
            "category": metadata["category"],
            "description": descriptions[case_id],
            "commands": {
                "public": metadata["public_command"],
                "heldout": "PYTHONPATH=src python -m unittest discover -s evaluator -p 'test_behavior.py' -v",
                "regression": "PYTHONPATH=src python -m unittest discover -s evaluator -p 'test_regression.py' -v",
            },
            "expected_fixed_behavior": "public, held-out, and regression tests pass on the fixed source tree",
            "release_note": "The source, tests, and reference patch were embargoed until all ten E003 runs closed.",
        }
        write_json(out / "case-manifest.json", public_metadata)
        cases.append({
            "case_id": case_id,
            "project": metadata["project_name"],
            "category": metadata["category"],
            "description": descriptions[case_id],
            "buggy_tree": f"artifacts/experiment-003/cases/{case_id}/buggy/",
            "fixed_tree": f"artifacts/experiment-003/cases/{case_id}/fixed/",
            "public_tests": f"artifacts/experiment-003/cases/{case_id}/buggy/tests/",
            "heldout_tests": f"artifacts/experiment-003/cases/{case_id}/evaluator/test_behavior.py",
            "regression_tests": f"artifacts/experiment-003/cases/{case_id}/evaluator/test_regression.py",
            "reference_patch": f"artifacts/experiment-003/cases/{case_id}/reference.patch",
            "commands": public_metadata["commands"],
        })
    write_json(E003_PUBLIC / "case-descriptions.json", {case["case_id"]: case for case in cases})
    write_text = E003_PUBLIC / "README.md"
    write_text.write_text(
        "# Experiment 003 public artifacts\n\n"
        "E003 is the five-case paired pilot on newly constructed software defects. "
        "After all ten runs closed, the public package was expanded to include the "
        "buggy and fixed case trees, visible tests, held-out behavior tests, nearby "
        "regression tests, reference patches, prompts, patches, evaluator outcomes, "
        "sanitized timelines, and run metadata. Hidden reasoning, credentials, raw "
        "environment dumps, and private session exports remain excluded.\n\n"
        "Medium scored 5/5 and Max scored 5/5. See `../../reports/experiment-003-results.md`, "
        "`../../reports/devin-swe2-reasoning-effort-v2.md`, and `../../results/publication-summary-v2.json`.\n",
        encoding="utf-8",
    )
    return cases


def draw_chart(path: Path, title: str, labels: list[str], series: dict[str, list[float]], suffix: str = "") -> None:
    from PIL import Image, ImageDraw, ImageFont

    width, height = 1600, 900
    image = Image.new("RGB", (width, height), "#f7f9fb")
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 30)
        bold = ImageFont.truetype("/Library/Fonts/Arial Bold.ttf", 42)
        small = ImageFont.truetype("/Library/Fonts/Arial.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
        bold = font
        small = font
    draw.text((70, 45), title, fill="#1f2933", font=bold)
    colors = ["#2867d8", "#c56a2d", "#2f855a", "#805ad5"]
    plot = (130, 150, 1500, 760)
    max_value = max(max(values) for values in series.values()) or 1
    count = len(labels)
    groups = len(series)
    group_width = (plot[2] - plot[0]) / max(count, 1)
    bar_width = min(80, group_width / (groups + 1))
    for i, label in enumerate(labels):
        center = plot[0] + group_width * (i + 0.5)
        draw.text((center - 60, plot[3] + 20), label, fill="#52606d", font=small)
        for j, (name, values) in enumerate(series.items()):
            value = values[i]
            x0 = center + (j - (groups - 1) / 2) * bar_width
            y1 = plot[3]
            y0 = y1 - (value / max_value) * (plot[3] - plot[1])
            draw.rectangle((x0, y0, x0 + bar_width - 5, y1), fill=colors[j % len(colors)])
            draw.text((x0, max(y0 - 28, plot[1] - 5)), f"{value:g}{suffix}", fill="#1f2933", font=small)
    draw.line((plot[0], plot[3], plot[2], plot[3]), fill="#9aa6b2", width=2)
    legend_x = plot[0]
    for j, name in enumerate(series):
        draw.rectangle((legend_x, 105, legend_x + 20, 125), fill=colors[j % len(colors)])
        draw.text((legend_x + 30, 100), name, fill="#52606d", font=font)
        legend_x += 220
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def build_charts(records: list[dict[str, Any]]) -> list[str]:
    by_case: dict[str, dict[str, dict[str, Any]]] = {}
    for row in records:
        by_case.setdefault(row["case_id"], {})[row["condition"]] = row
    ordered = ["black-16", "fastapi-3", "scrapy-3", "tqdm-5", "tornado-13", "E003-N01", "E003-N02", "E003-N03", "E003-N04", "E003-N05"]
    labels = [case.replace("-", " ") for case in ordered]
    wall_m = [by_case[case]["M"]["wall_seconds"] for case in ordered]
    wall_x = [by_case[case]["X"]["wall_seconds"] for case in ordered]
    draw_chart(CHART_DIR / "v2-paired-wall-time.png", "Paired wall time: historical and novel cases", labels, {"Medium": wall_m, "Max": wall_x}, "s")
    success = {
        "E002 historical": [5, 4],
        "E003 novel": [5, 5],
    }
    draw_chart(CHART_DIR / "v2-success-by-dataset.png", "Success by dataset", ["Medium", "Max"], {key: value for key, value in success.items()})
    condition = {c: [row for row in records if row["condition"] == c] for c in ("M", "X")}
    draw_chart(CHART_DIR / "v2-resource-use.png", "Aggregate observable resource use", ["Wall (s)", "Tool calls", "Completion tokens / 100"], {
        "Medium": [sum(r["wall_seconds"] for r in condition["M"]), sum(r["tool_calls"] for r in condition["M"]), sum(r["completion_tokens"] for r in condition["M"]) / 100],
        "Max": [sum(r["wall_seconds"] for r in condition["X"]), sum(r["tool_calls"] for r in condition["X"]), sum(r["completion_tokens"] for r in condition["X"]) / 100],
    })
    tqdm = by_case["tqdm-5"]
    draw_chart(CHART_DIR / "v2-tqdm-heldout.png", "tqdm: visible versus held-out evaluation", ["Medium public", "Max public", "Medium held-out", "Max held-out"], {"Pass": [1, 1, 1, 0]})
    return [
        "assets/charts/v2-paired-wall-time.png",
        "assets/charts/v2-success-by-dataset.png",
        "assets/charts/v2-resource-use.png",
        "assets/charts/v2-tqdm-heldout.png",
    ]


def build_summary(records: list[dict[str, Any]], cases: list[dict[str, Any]], source_base_commit: str) -> dict[str, Any]:
    def condition_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "runs": len(rows),
            "solved": sum(row["success"] for row in rows),
            "wall_time_seconds": stats(rows, "wall_seconds"),
            "steps": stats(rows, "steps"),
            "tool_calls": stats(rows, "tool_calls"),
            "prompt_tokens": stats(rows, "prompt_tokens"),
            "completion_tokens": stats(rows, "completion_tokens"),
            "cached_tokens": stats(rows, "cached_tokens"),
            "source_patch_lines_added": stats(rows, "lines_added"),
            "source_patch_lines_deleted": stats(rows, "lines_deleted"),
            "generated_files_total": sum(row["generated_files"] for row in rows),
            "reported_cost": None,
            "reported_acus": None,
        }
    pairs = []
    for case_id in sorted({row["case_id"] for row in records}, key=lambda value: (value.startswith("E003"), value)):
        pair = {row["condition"]: row for row in records if row["case_id"] == case_id}
        medium, maximum = pair["M"], pair["X"]
        pairs.append({
            "case_id": case_id,
            "provenance": medium["provenance"],
            "medium_run": medium["run_id"],
            "max_run": maximum["run_id"],
            "medium_success": medium["success"],
            "max_success": maximum["success"],
            "outcome": "both succeeded" if medium["success"] and maximum["success"] else "Medium only" if medium["success"] else "Max only" if maximum["success"] else "both failed",
            "max_minus_medium": {
                "wall_seconds": maximum["wall_seconds"] - medium["wall_seconds"],
                "steps": maximum["steps"] - medium["steps"],
                "tool_calls": maximum["tool_calls"] - medium["tool_calls"],
                "prompt_tokens": maximum["prompt_tokens"] - medium["prompt_tokens"],
                "completion_tokens": maximum["completion_tokens"] - medium["completion_tokens"],
            },
        })
    grouped = {dataset: {condition: condition_summary([r for r in records if r["provenance"] == dataset and r["condition"] == condition]) for condition in ("M", "X")} for dataset in ("historical", "novel")}
    grouped["combined"] = {condition: condition_summary([r for r in records if r["condition"] == condition]) for condition in ("M", "X")}
    return {
        "schema_version": 2,
        "publication_version": "2.0.0",
        "source_evidence_base_commit": source_base_commit,
        "project": "Devin + SWE-2 Reasoning Effort Benchmark",
        "repository": "https://github.com/MAJORminorStudio/devin-agent-benchmark",
        "research_questions": [
            "Does the E002 Medium-versus-Max result replicate on five newly constructed cases withheld until the protocol was frozen?",
            "How do the conditions compare on behavioral success and observable resource use across the combined ten-case study?",
        ],
        "denominator": {"valid_capability_runs": 20, "unique_cases": 10, "e001_included": False, "e001_status": "operational provenance only"},
        "datasets": {"historical": {"experiment": "E002", "cases": 5}, "novel": {"experiment": "E003", "cases": 5}},
        "condition_summary": grouped,
        "paired_outcomes": {outcome: sum(pair["outcome"] == outcome for pair in pairs) for outcome in ("both succeeded", "Medium only", "Max only", "both failed")},
        "pairs": pairs,
        "runs": records,
        "cases": cases,
        "novelty_boundary": "E003 instances, defects, prompts, reference fixes, and held-out evaluations were newly constructed and withheld until the protocol was frozen and execution began; no training-data absence claim is made.",
        "limitations": ["Exploratory paired study with ten unique cases; no statistical-significance claim.", "One agent product and one model family under one frozen setup.", "Observable activity is not internal reasoning.", "Cost and ACUs were unavailable.", "E002 and E003 differ in case provenance and project scale."],
        "public_paths": {"report": "reports/devin-swe2-reasoning-effort-v2.md", "csv": "results/publication-paired-results-v2.csv", "artifacts": "artifacts/experiment-003/", "methodology": "docs/methodology.md"},
    }


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    fields = ["provenance", "experiment", "case_id", "label", "project", "bug_id", "run_id", "condition", "model", "success", "public", "heldout", "regression", "wall_seconds", "steps", "tool_calls", "prompt_tokens", "completion_tokens", "cached_tokens", "source_files_changed", "lines_added", "lines_deleted", "files_changed", "generated_files", "session_id"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in records)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-root", type=Path, required=True, help="closed E003 staging root; never publish this path in artifacts")
    args = parser.parse_args()
    private_root = args.private_root.resolve()
    if not private_root.is_dir():
        raise SystemExit(f"E003 private staging root missing: {private_root}")
    cases = build_case_evidence(private_root)
    records = e002_records() + e003_records()
    if len(records) != 20 or {row["provenance"] for row in records} != {"historical", "novel"}:
        raise SystemExit("expected exactly 20 E002/E003 records")
    charts = build_charts(records)
    artifact_manifest = read_json(E003_PUBLIC / "MANIFEST.json")
    artifact_manifest["publication_status"] = "expanded-after-all-ten-runs-closed"
    artifact_manifest["public_case_bundle"] = {
        "root": "artifacts/experiment-003/cases/",
        "contents": ["buggy source", "fixed source", "visible tests", "held-out behavior tests", "regression tests", "reference patches", "safe case manifests"],
        "cases": [case["case_id"] for case in cases],
        "raw_session_exports": "excluded",
        "hidden_reasoning": "excluded",
        "credentials_and_private_paths": "excluded",
    }
    write_json(E003_PUBLIC / "MANIFEST.json", artifact_manifest)
    source_base_commit = "342679f87b5411f4c6217b0af38d14985e6e74ea"
    summary = build_summary(records, cases, source_base_commit)
    write_json(ROOT / "results" / "publication-summary-v2.json", summary)
    write_csv(ROOT / "results" / "publication-paired-results-v2.csv", records)
    print(json.dumps({"runs": len(records), "charts": charts, "summary": str(ROOT / "results" / "publication-summary-v2.json")}, indent=2))


if __name__ == "__main__":
    main()
