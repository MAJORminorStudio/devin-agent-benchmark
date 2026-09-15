#!/usr/bin/env python3
"""Build the public publication data files and charts from committed results.

This script is intentionally read-only with respect to experiment evidence: it
reads the committed E001/E002 summaries and forensic analysis, then writes only
publication derivatives under results/, assets/charts/, and (optionally) a
caller-selected output root. It never reads ignored raw run directories.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import textwrap
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
CASE_ORDER = ["black-16", "fastapi-3", "scrapy-3", "tqdm-5", "tornado-13"]
CASE_LABELS = {
    "black-16": "Black 16",
    "fastapi-3": "FastAPI 3",
    "scrapy-3": "Scrapy 3",
    "tqdm-5": "tqdm 5",
    "tornado-13": "Tornado 13",
}
MEDIUM = "#2867d8"
MAX = "#c56a2d"
SOURCE = "#2f855a"
GENERATED = "#9aa6b2"
ADDED = "#2f855a"
DELETED = "#b45345"
PASS = "#2f855a"
FAIL = "#b45345"
TEXT = "#1f2933"
MUTED = "#52606d"
GRID = "#d9e2ec"
BACKGROUND = "#f7f9fb"


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def fmt_number(value: float) -> str:
    if float(value).is_integer():
        return f"{int(value):,}"
    return f"{value:,.1f}"


def fmt_seconds(value: float) -> str:
    return f"{value:.1f}s"


def token_label(value: float) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return fmt_number(value)


def build_records(summary: Mapping[str, Any], forensic: Mapping[str, Any], manifest: Mapping[str, Any]) -> List[Dict[str, Any]]:
    summary_runs = {item["run_id"]: item for item in summary["runs"]}
    forensic_runs = {item["run_id"]: item for item in forensic["runs"]}
    manifest_cases = {item["case_id"]: item for item in manifest["cases"]}
    records: List[Dict[str, Any]] = []
    for case_id in CASE_ORDER:
        case = manifest_cases[case_id]
        row: Dict[str, Any] = {
            "case": case_id,
            "label": CASE_LABELS[case_id],
            "project": case["project"],
            "bug_id": case["bug_id"],
            "difficulty": case["difficulty"],
            "repository": case["original_repository"],
            "buggy_commit": case["buggy_commit"],
            "fixed_commit": case["fixed_commit"],
            "public_prompt": f"prompts/experiment-001/{case_id}.md",
            "heldout_tests": case["heldout_test_files"],
            "evaluator_metadata": f"evaluation/experiment-001/{case_id}/metadata.json",
        }
        for condition in ("M", "X"):
            matched = [
                item for item in summary["runs"]
                if item["case_id"] == case_id and item["condition"] == condition
            ]
            if len(matched) != 1:
                raise ValueError(f"expected one summary run for {case_id}/{condition}")
            item = matched[0]
            forensic_item = forensic_runs[item["run_id"]]
            patch = forensic_item["patch"]
            category_counts = patch.get("changed_files_by_category", {})
            generated_files = sum(
                count for category, count in category_counts.items() if category != "source"
            )
            prefix = "medium" if condition == "M" else "max"
            row.update({
                f"{prefix}_run": item["run_id"],
                f"{prefix}_session": item.get("session_id"),
                f"{prefix}_model": item["model"],
                f"{prefix}_success": bool(item["task_success"]),
                f"{prefix}_public": item["public_tests"],
                f"{prefix}_heldout": item["heldout_tests"],
                f"{prefix}_regression": item["regression_status"],
                f"{prefix}_wall_seconds": item["wall_time_seconds"],
                f"{prefix}_steps": item.get("steps"),
                f"{prefix}_tool_calls": item.get("tool_calls"),
                f"{prefix}_prompt_tokens": item["tokens"]["prompt"],
                f"{prefix}_completion_tokens": item["tokens"]["completion"],
                f"{prefix}_cached_tokens": item["tokens"]["cached"],
                f"{prefix}_source_files_changed": patch["changed_files_by_category"].get("source", 0),
                f"{prefix}_source_added": patch["source_additions"],
                f"{prefix}_source_deleted": patch["source_deletions"],
                f"{prefix}_files_changed": patch["changed_file_count"],
                f"{prefix}_generated_files": generated_files,
                f"{prefix}_patch_sha256": item.get("patch_sha256"),
            })
        records.append(row)
    return records


def build_publication_summary(
    summary: Mapping[str, Any],
    e001: Mapping[str, Any],
    forensic: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    def condition_metrics(condition: str) -> Dict[str, Any]:
        source = forensic["condition_summary"][condition]
        runs = [row for row in records]
        prefix = "medium" if condition == "M" else "max"
        return {
            "model": summary["condition_summary"][condition]["model"],
            "n": source["runs"],
            "solved": source["solved"],
            "wall_time_seconds": {
                "total": source["total_wall_time_seconds"],
                "mean": source["mean_wall_time_seconds"],
                "median": source["median_wall_time_seconds"],
            },
            "steps": {
                "total": source["total_steps"],
                "mean": source["mean_steps"],
                "values_by_case": [row[f"{prefix}_steps"] for row in runs],
            },
            "tool_calls": {
                "total": source["total_tool_calls"],
                "values_by_case": [row[f"{prefix}_tool_calls"] for row in runs],
            },
            "tokens": source["tokens"],
            "source_diff": {
                "files_changed": source["runs"],
                "lines_added": source["total_source_additions"],
                "lines_deleted": source["total_source_deletions"],
            },
            "workspace_change_record": {
                "files_changed": source["total_changed_files"],
                "generated_or_environment_files": sum(row[f"{prefix}_generated_files"] for row in runs),
            },
            "reported_cost": None,
            "reported_acus": None,
        }

    pairs = []
    for row in records:
        medium_wall = row["medium_wall_seconds"]
        max_wall = row["max_wall_seconds"]
        pairs.append({
            "case": row["case"],
            "medium_run": row["medium_run"],
            "max_run": row["max_run"],
            "medium_success": row["medium_success"],
            "max_success": row["max_success"],
            "outcome": (
                "both succeeded" if row["medium_success"] and row["max_success"]
                else "Medium only" if row["medium_success"]
                else "Max only" if row["max_success"]
                else "both failed"
            ),
            "max_minus_medium_wall_seconds": round(max_wall - medium_wall, 3),
            "wall_ratio_max_over_medium": round(max_wall / medium_wall, 6),
            "medium_steps": row["medium_steps"],
            "max_steps": row["max_steps"],
            "medium_tool_calls": row["medium_tool_calls"],
            "max_tool_calls": row["max_tool_calls"],
            "medium_source_added": row["medium_source_added"],
            "medium_source_deleted": row["medium_source_deleted"],
            "max_source_added": row["max_source_added"],
            "max_source_deleted": row["max_source_deleted"],
            "medium_generated_files": row["medium_generated_files"],
            "max_generated_files": row["max_generated_files"],
        })

    return {
        "schema_version": 1,
        "project": {
            "name": "Devin + SWE-2 Reasoning Effort Benchmark",
            "repository": "https://github.com/MAJORminorStudio/devin-agent-benchmark",
            "publisher": "MAJORminor Studio",
            "publication_version": "1.0.0",
            "publication_date": "2026-09-15",
        },
        "provenance": {
            "publication_control_commit": "7e623d0bdb34baa3f6a44e5240028016e11bffe3",
            "experiment_001_results": "results/experiment-001-summary.json",
            "experiment_002_results": "results/experiment-002-summary.json",
            "experiment_002_forensics": "results/experiment-002-forensics.json",
            "bugsinpy_dataset": "sources/bugsinpy.json",
        },
        "research_questions": {
            "primary": "How did SWE-2 Medium and SWE-2 Max compare on five real OSS repair tasks?",
            "secondary": "How much can permission configuration affect observed autonomous-agent performance?",
        },
        "models": {
            "M": "swe-2-medium",
            "X": "swe-2-max",
        },
        "experiments": {
            "experiment-001": {
                "status": "invalid_capability_comparison",
                "validity": "operational_provenance_only",
                "cases": 5,
                "runs": 10,
                "medium_solved": e001["overall"]["Medium"]["solved"],
                "max_solved": e001["overall"]["Max"]["solved"],
                "reason": "Noninteractive accept-edits permission gating rejected required tool calls and produced empty patches in all ten runs.",
                "report": "reports/experiment-001-results.md",
                "artifacts": "artifacts/experiment-001/README.md",
            },
            "experiment-002": {
                "status": "completed_exploratory_pilot",
                "validity": "autonomous_capability_result_under_isolated_configuration",
                "control_commit": summary["control_commit"],
                "runs": summary["runs_completed"],
                "protocol": summary["protocol"],
                "condition_metrics": {
                    "Medium": condition_metrics("M"),
                    "Max": condition_metrics("X"),
                },
                "paired_outcomes": summary["paired_outcomes"],
                "report": "reports/experiment-002-results.md",
                "forensic_report": "reports/experiment-002-forensic-analysis.md",
                "artifacts": "artifacts/experiment-002/README.md",
            },
        },
        "cases": [
            {
                "case": row["case"],
                "project": row["project"],
                "bug_id": row["bug_id"],
                "difficulty": row["difficulty"],
                "repository": row["repository"],
                "buggy_commit": row["buggy_commit"],
                "fixed_commit": row["fixed_commit"],
                "prompt": row["public_prompt"],
                "heldout_tests": row["heldout_tests"],
                "evaluator_metadata": row["evaluator_metadata"],
                "medium_run": row["medium_run"],
                "max_run": row["max_run"],
            }
            for row in records
        ],
        "paired_results": pairs,
        "limitations": [
            "Five historical Python bugs and five paired cases only.",
            "One agent product and one model family under one frozen task setup.",
            "Exploratory pilot; no statistical superiority claim is made.",
            "Monetary cost and ACU data were unavailable.",
            "Public benchmark exposure and contamination cannot be ruled out absolutely.",
        ],
        "reports": [
            "README.md",
            "reports/swe-2-medium-vs-max-research-report.md",
            "reports/experiment-002-results.md",
            "reports/experiment-002-forensic-analysis.md",
            "reports/experiment-001-results.md",
        ],
        "artifact_roots": [
            "artifacts/experiment-001/",
            "artifacts/experiment-002/",
            "manifests/experiment-001.json",
            "manifests/experiment-002-config.json",
            "manifests/experiment-002-runs.json",
            "evaluation/experiment-001/",
        ],
    }


def write_paired_csv(path: Path, records: Sequence[Mapping[str, Any]]) -> None:
    fields = [
        "case", "medium_run", "max_run", "medium_success", "max_success",
        "medium_wall_seconds", "max_wall_seconds", "wall_ratio_max_over_medium",
        "medium_steps", "max_steps", "medium_tool_calls", "max_tool_calls",
        "medium_prompt_tokens", "max_prompt_tokens", "medium_completion_tokens",
        "max_completion_tokens", "medium_source_added", "medium_source_deleted",
        "max_source_added", "max_source_deleted",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in records:
            writer.writerow({
                "case": row["case"],
                "medium_run": row["medium_run"],
                "max_run": row["max_run"],
                "medium_success": int(row["medium_success"]),
                "max_success": int(row["max_success"]),
                "medium_wall_seconds": row["medium_wall_seconds"],
                "max_wall_seconds": row["max_wall_seconds"],
                "wall_ratio_max_over_medium": round(row["max_wall_seconds"] / row["medium_wall_seconds"], 6),
                "medium_steps": row["medium_steps"],
                "max_steps": row["max_steps"],
                "medium_tool_calls": row["medium_tool_calls"],
                "max_tool_calls": row["max_tool_calls"],
                "medium_prompt_tokens": row["medium_prompt_tokens"],
                "max_prompt_tokens": row["max_prompt_tokens"],
                "medium_completion_tokens": row["medium_completion_tokens"],
                "max_completion_tokens": row["max_completion_tokens"],
                "medium_source_added": row["medium_source_added"],
                "medium_source_deleted": row["medium_source_deleted"],
                "max_source_added": row["max_source_added"],
                "max_source_deleted": row["max_source_deleted"],
            })


def get_fonts():
    from PIL import ImageFont

    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/Library/Fonts/Arial.ttf",
    ]

    def make(size: int, bold: bool = False):
        suffix = "-Bold" if bold else ""
        for base in candidates:
            candidate = base.replace(".ttf", f"{suffix}.ttf") if bold else base
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                continue
        return ImageFont.load_default()

    return make


def make_image(title: str, subtitle: str, size: Tuple[int, int] = (1600, 900)):
    from PIL import Image, ImageDraw

    image = Image.new("RGB", size, BACKGROUND)
    draw = ImageDraw.Draw(image)
    font = get_fonts()
    draw.text((80, 48), title, fill=TEXT, font=font(38, True))
    draw.text((80, 100), subtitle, fill=MUTED, font=font(22))
    return image, draw, font


def legend(draw, font, x: int, y: int, entries: Sequence[Tuple[str, str]]) -> None:
    cursor = x
    for label, color in entries:
        draw.rectangle((cursor, y + 5, cursor + 22, y + 27), fill=color)
        draw.text((cursor + 32, y), label, fill=TEXT, font=font(20))
        cursor += 32 + draw.textlength(label, font=font(20)) + 42


def draw_bar_pair(
    records: Sequence[Mapping[str, Any]],
    key: str,
    title: str,
    subtitle: str,
    y_label: str,
    output: Path,
    formatter=fmt_number,
    y_max: float | None = None,
    medium_key: str | None = None,
    max_key: str | None = None,
) -> None:
    from PIL import ImageDraw

    image, draw, font = make_image(title, subtitle)
    medium_key = medium_key or f"medium_{key}"
    max_key = max_key or f"max_{key}"
    values_m = [float(row[medium_key]) for row in records]
    values_x = [float(row[max_key]) for row in records]
    y_max = y_max or max(values_m + values_x) * 1.22 or 1
    left, right, top, bottom = 170, 70, 180, 120
    x0, x1 = left, image.width - right
    y0, y1 = image.height - bottom, top
    draw.line((x0, y0, x1, y0), fill=TEXT, width=2)
    draw.line((x0, y0, x0, y1), fill=TEXT, width=2)
    for tick in range(0, 6):
        value = y_max * tick / 5
        y = y0 - (value / y_max) * (y0 - y1)
        draw.line((x0, y, x1, y), fill=GRID, width=1)
        label = formatter(value)
        bbox = draw.textbbox((0, 0), label, font=font(18))
        draw.text((x0 - (bbox[2] - bbox[0]) - 16, y - 12), label, fill=MUTED, font=font(18))
    slot = (x1 - x0) / len(records)
    bar_width = min(62, slot * 0.22)
    for idx, row in enumerate(records):
        center = x0 + slot * (idx + 0.5)
        for value, color, offset in ((values_m[idx], MEDIUM, -bar_width * 0.6), (values_x[idx], MAX, bar_width * 0.6)):
            x_left = center + offset - bar_width / 2
            x_right = center + offset + bar_width / 2
            y = y0 - (value / y_max) * (y0 - y1)
            draw.rectangle((x_left, y, x_right, y0), fill=color)
            label = formatter(value)
            bbox = draw.textbbox((0, 0), label, font=font(18))
            draw.text((center + offset - (bbox[2] - bbox[0]) / 2, max(y - 32, y1 - 2)), label, fill=TEXT, font=font(18))
        label = CASE_LABELS[row["case"]]
        bbox = draw.textbbox((0, 0), label, font=font(18))
        draw.text((center - (bbox[2] - bbox[0]) / 2, y0 + 20), label, fill=TEXT, font=font(18))
    draw.text((30, (y1 + y0) / 2), y_label, fill=MUTED, font=font(20), anchor="mm")
    legend(draw, font, left, 140, (("SWE-2 Medium", MEDIUM), ("SWE-2 Max", MAX)))
    draw.text((80, image.height - 54), "Source: committed Experiment 002 summary and forensic metrics; five paired cases.", fill=MUTED, font=font(16))
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=True)


def draw_success(records: Sequence[Mapping[str, Any]], output: Path) -> None:
    image, draw, font = make_image(
        "Task success by condition",
        "TASK_SUCCESS is behavioral: public tests + held-out tests + clean regression suite; n=5 per condition.",
    )
    values = [("SWE-2 Medium", sum(bool(r["medium_success"]) for r in records), MEDIUM), ("SWE-2 Max", sum(bool(r["max_success"]) for r in records), MAX)]
    left, right, top, bottom = 250, 100, 190, 130
    x0, x1 = left, image.width - right
    y0, y1 = image.height - bottom, top
    draw.line((x0, y0, x1, y0), fill=TEXT, width=2)
    draw.line((x0, y0, x0, y1), fill=TEXT, width=2)
    for tick in range(6):
        y = y0 - tick / 5 * (y0 - y1)
        draw.line((x0, y, x1, y), fill=GRID, width=1)
        label = str(tick)
        draw.text((x0 - 38, y - 12), label, fill=MUTED, font=font(20))
    slot = (x1 - x0) / 2
    bar_width = 180
    for idx, (label, value, color) in enumerate(values):
        center = x0 + slot * (idx + 0.5)
        y = y0 - value / 5 * (y0 - y1)
        draw.rectangle((center - bar_width / 2, y, center + bar_width / 2, y0), fill=color)
        value_label = f"{value}/5"
        bbox = draw.textbbox((0, 0), value_label, font=font(32, True))
        draw.text((center - (bbox[2] - bbox[0]) / 2, y - 48), value_label, fill=TEXT, font=font(32, True))
        bbox = draw.textbbox((0, 0), label, font=font(24))
        draw.text((center - (bbox[2] - bbox[0]) / 2, y0 + 28), label, fill=TEXT, font=font(24))
    draw.text((55, (y1 + y0) / 2), "Successful cases", fill=MUTED, font=font(22), anchor="mm")
    draw.text((80, image.height - 54), "Source: results/experiment-002-summary.json; exploratory five-case pilot.", fill=MUTED, font=font(16))
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=True)


def draw_token_use(records: Sequence[Mapping[str, Any]], output: Path) -> None:
    from PIL import ImageDraw

    image, draw, font = make_image(
        "Observed token use",
        "Prompt and completion tokens are shown in separate panels so completion activity remains visible; totals across five runs.",
        (1600, 1050),
    )
    panels = [("Prompt tokens", "_prompt_tokens", 260, 520), ("Completion tokens", "_completion_tokens", 650, 910)]
    for panel_title, suffix, top, bottom in panels:
        medium = sum(row["medium" + suffix] for row in records)
        maximum = sum(row["max" + suffix] for row in records)
        y_max = max(medium, maximum) * 1.24 or 1
        left, right = 250, 100
        x0, x1 = left, image.width - right
        y0, y1 = bottom, top
        draw.text((left, top - 48), panel_title, fill=TEXT, font=font(26, True))
        draw.line((x0, y0, x1, y0), fill=TEXT, width=2)
        draw.line((x0, y0, x0, y1), fill=TEXT, width=2)
        for tick in range(0, 5):
            value = y_max * tick / 4
            y = y0 - (value / y_max) * (y0 - y1)
            draw.line((x0, y, x1, y), fill=GRID, width=1)
            draw.text((x0 - 130, y - 12), token_label(value), fill=MUTED, font=font(18))
        slot = (x1 - x0) / 2
        bar_width = 180
        for idx, (label, value, color) in enumerate((("SWE-2 Medium", medium, MEDIUM), ("SWE-2 Max", maximum, MAX))):
            center = x0 + slot * (idx + 0.5)
            y = y0 - (value / y_max) * (y0 - y1)
            draw.rectangle((center - bar_width / 2, y, center + bar_width / 2, y0), fill=color)
            text = token_label(value)
            bbox = draw.textbbox((0, 0), text, font=font(28, True))
            draw.text((center - (bbox[2] - bbox[0]) / 2, y - 42), text, fill=TEXT, font=font(28, True))
            bbox = draw.textbbox((0, 0), label, font=font(22))
            draw.text((center - (bbox[2] - bbox[0]) / 2, y0 + 18), label, fill=TEXT, font=font(22))
    legend(draw, font, 250, 175, (("SWE-2 Medium", MEDIUM), ("SWE-2 Max", MAX)))
    draw.text((80, image.height - 52), "Source: results/experiment-002-summary.json; provider-reported cost/ACUs were unavailable.", fill=MUTED, font=font(16))
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=True)


def draw_source_vs_churn(records: Sequence[Mapping[str, Any]], output: Path) -> None:
    from PIL import ImageDraw

    image, draw, font = make_image(
        "Source changes versus workspace churn",
        "Source-only line changes are separate from generated/cache/virtualenv entries in the preserved all-file workspace record.",
        (1600, 1050),
    )
    # Upper panel: source line changes.
    left, right = 250, 100
    x0, x1 = left, image.width - right
    for title, values, colors, top, bottom, maximum in [
        (
            "Actual source diff lines",
            [("Added", sum(r["medium_source_added"] for r in records), sum(r["max_source_added"] for r in records)),
             ("Deleted", sum(r["medium_source_deleted"] for r in records), sum(r["max_source_deleted"] for r in records))],
            [ADDED, DELETED], 250, 500, 60,
        ),
        (
            "Generated/environment files in workspace record",
            [("Source files", sum(r["medium_source_files_changed"] for r in records), sum(r["max_source_files_changed"] for r in records)),
             ("Generated/cache", sum(r["medium_generated_files"] for r in records), sum(r["max_generated_files"] for r in records))],
            [SOURCE, GENERATED], 670, 940, 3500,
        ),
    ]:
        draw.text((left, top - 50), title, fill=TEXT, font=font(26, True))
        y0, y1 = bottom, top
        draw.line((x0, y0, x1, y0), fill=TEXT, width=2)
        draw.line((x0, y0, x0, y1), fill=TEXT, width=2)
        for tick in range(5):
            value = maximum * tick / 4
            y = y0 - (value / maximum) * (y0 - y1)
            draw.line((x0, y, x1, y), fill=GRID, width=1)
            draw.text((x0 - 125, y - 12), fmt_number(value), fill=MUTED, font=font(18))
        slot = (x1 - x0) / 2
        group_width = 260
        for idx, (condition, color) in enumerate((("Medium", MEDIUM), ("Max", MAX))):
            center = x0 + slot * (idx + 0.5)
            cursor = center - group_width / 2
            bottom_height = 0
            for (label, medium, maximum_value), segment_color in zip(values, colors):
                value = medium if condition == "Medium" else maximum_value
                height = value / maximum * (y0 - y1)
                y_top = y0 - bottom_height - height
                draw.rectangle((cursor, y_top, cursor + group_width, y0 - bottom_height), fill=segment_color)
                if value:
                    text = fmt_number(value)
                    bbox = draw.textbbox((0, 0), text, font=font(20, True))
                    draw.text((center - (bbox[2] - bbox[0]) / 2, y_top - 30 if bottom_height == 0 else y_top + 8), text, fill=TEXT, font=font(20, True))
                bottom_height += height
            draw.text((center - 44, y0 + 18), condition, fill=TEXT, font=font(22))
        if title.startswith("Actual"):
            legend(draw, font, 890, top - 48, (("Added", ADDED), ("Deleted", DELETED)))
        else:
            legend(draw, font, 820, top - 48, (("Source files", SOURCE), ("Generated/cache", GENERATED)))
    draw.text((80, image.height - 50), "The large Max record is overwhelmingly generated virtualenv/cache churn, not source modification.", fill=MUTED, font=font(16))
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=True)


def draw_tqdm_case(output: Path) -> None:
    from PIL import ImageDraw

    image, draw, font = make_image(
        "tqdm-5: visible-test agreement, held-out disagreement",
        "Both agents passed the visible public check; only Medium satisfied the held-out sized-iterable behavior.",
        (1600, 900),
    )
    draw.rounded_rectangle((100, 230, 1500, 380), radius=18, outline=GRID, width=3, fill="#ffffff")
    draw.text((800, 270), "disabled progress wrapper over a sized iterable", fill=TEXT, font=font(30, True), anchor="mm")
    draw.text((800, 325), "Expected externally observable behavior: infer the iterable length when total is omitted", fill=MUTED, font=font(22), anchor="mm")
    draw.line((800, 380, 800, 455), fill=TEXT, width=3)
    draw.polygon([(790, 445), (810, 445), (800, 465)], fill=TEXT)
    branches = [
        (150, 480, 730, "Medium", "inferred len(iterable)", "total = 3", "HELD-OUT PASS", PASS),
        (870, 480, 1450, "Max", "initialized total only", "total = None", "HELD-OUT FAIL", FAIL),
    ]
    for x_left, _, x_right, condition, detail, observed, result, color in branches:
        draw.rounded_rectangle((x_left, 480, x_right, 720), radius=18, outline=GRID, width=3, fill="#ffffff")
        draw.text(((x_left + x_right) / 2, 525), condition, fill=MEDIUM if condition == "Medium" else MAX, font=font(30, True), anchor="mm")
        draw.text(((x_left + x_right) / 2, 585), detail, fill=TEXT, font=font(25), anchor="mm")
        draw.text(((x_left + x_right) / 2, 640), observed, fill=TEXT, font=font(28, True), anchor="mm")
        draw.text(((x_left + x_right) / 2, 690), result, fill=color, font=font(24, True), anchor="mm")
    draw.text((80, image.height - 52), "Source: E002 forensic analysis and public tqdm patches; behavior, not patch identity, determines TASK_SUCCESS.", fill=MUTED, font=font(16))
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=True)


def build_charts(records: Sequence[Mapping[str, Any]], output_dir: Path) -> None:
    draw_bar_pair(
        records, "wall_seconds", "Paired wall-clock time", "Elapsed seconds per case; each case is a paired Medium/Max comparison.",
        "seconds", output_dir / "paired-wall-time.png", formatter=fmt_seconds,
    )
    draw_success(records, output_dir / "success-rate.png")
    draw_token_use(records, output_dir / "total-token-use.png")
    draw_bar_pair(
        records, "tool_calls", "Observable tool calls by case", "Counted from sanitized session timelines; rejected calls were absent in E002.",
        "tool calls", output_dir / "tool-calls-by-case.png",
    )
    draw_bar_pair(
        records, "steps", "Agent steps by case", "Observable session steps recorded in the public result summary.",
        "steps", output_dir / "steps-by-case.png",
    )
    draw_source_vs_churn(records, output_dir / "source-vs-workspace-churn.png")
    draw_tqdm_case(output_dir / "tqdm-case-study.png")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this repository)")
    args = parser.parse_args()
    root = args.root.resolve()
    summary = read_json(root / "results/experiment-002-summary.json")
    e001 = read_json(root / "results/experiment-001-summary.json")
    forensic = read_json(root / "results/experiment-002-forensics.json")
    manifest = read_json(root / "manifests/experiment-001.json")
    records = build_records(summary, forensic, manifest)
    publication = build_publication_summary(summary, e001, forensic, records)
    write_json(root / "results/publication-summary.json", publication)
    write_paired_csv(root / "results/publication-paired-results.csv", records)
    build_charts(records, root / "assets/charts")
    print(json.dumps({
        "status": "ok",
        "cases": len(records),
        "charts": 7,
        "summary": str(root / "results/publication-summary.json"),
        "csv": str(root / "results/publication-paired-results.csv"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
