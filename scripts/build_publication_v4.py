#!/usr/bin/env python3
"""Build the final V4 publication package from canonical experiment records."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "publication-v4"
CHARTS = OUT / "charts"
SOURCE_COMMIT = "82915fc31c63cd8fb6a01a4e527be95e0d7de698"
TIER_ORDER = {"moderate": 0, "hard": 1, "very-hard": 2}
TIER_LABEL = {"moderate": "Moderate", "hard": "Hard", "very-hard": "Very-hard"}
CONDITION_LABEL = {"M": "Medium", "X": "Max"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def status(value: Any) -> str:
    value = str(value).lower()
    return "pass" if value in {"pass", "clean", "true"} else "fail"


def norm_e002(raw: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for r in raw["runs"]:
        out.append(
            {
                "experiment": "E002",
                "tier": "moderate",
                "provenance": "historical-public",
                "case": r["case_id"],
                "case_key": f"E002:{r['case_id']}",
                "project": r.get("project"),
                "experiment_case_id": r["experiment_case_id"],
                "run_id": r["run_id"],
                "condition": r["condition"],
                "model": r["model"],
                "session_id": r.get("session_id"),
                "success": bool(r["task_success"]),
                "public": status(r["public_tests"]),
                "held_out": status(r["heldout_tests"]),
                "regression": status(r["regression_status"]),
                "evaluation_status": r["evaluation_status"],
                "wall_time_seconds": float(r["wall_time_seconds"]),
                "steps": int(r["steps"]),
                "tool_calls": int(r["tool_calls"]),
                "prompt_tokens": int(r["tokens"]["prompt"]),
                "completion_tokens": int(r["tokens"]["completion"]),
                "cached_tokens": int(r["tokens"]["cached"]),
                "source_files_changed": int(r["source_files_changed"]),
                "workspace_churn_files": int(r["files_changed"]),
                "generated_or_environment_files": max(0, int(r["files_changed"]) - int(r["source_files_changed"])),
                "lines_added": int(r["lines_added"]),
                "lines_deleted": int(r["lines_deleted"]),
                "patch_sha256": r.get("patch_sha256"),
                "prompt_sha256": None,
                "visible_heldout_disagreement": r["public_tests"] == "pass" and r["heldout_tests"] != "pass",
                "failure_classification": r.get("failure_classification"),
            }
        )
    return out


def norm_e004(raw: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for r in raw["runs"]:
        patch = r["patch"]
        out.append(
            {
                "experiment": "E004",
                "tier": "moderate",
                "provenance": "newly-constructed-withheld",
                "case": r["case_id"],
                "case_key": f"E004:{r['case_id']}",
                "project": None,
                "experiment_case_id": r["case_id"],
                "run_id": r["run_id"],
                "condition": r["condition"],
                "model": r["model"],
                "session_id": r.get("session_id"),
                "success": bool(r["task_success"]),
                "public": status(r["public"]),
                "held_out": status(r["heldout"]),
                "regression": status(r["regression"]),
                "evaluation_status": r["evaluation_status"],
                "wall_time_seconds": float(r["wall_time_seconds"]),
                "steps": int(r["steps"]),
                "tool_calls": int(r["tool_calls"]),
                "prompt_tokens": int(r["tokens"]["prompt"]),
                "completion_tokens": int(r["tokens"]["completion"]),
                "cached_tokens": int(r["tokens"]["cached"]),
                "source_files_changed": int(patch["files_changed"]),
                "workspace_churn_files": int(patch["files_changed"] + len(patch["generated_or_environment_files"])),
                "generated_or_environment_files": len(patch["generated_or_environment_files"]),
                "lines_added": int(patch["lines_added"]),
                "lines_deleted": int(patch["lines_deleted"]),
                "patch_sha256": patch.get("sha256"),
                "prompt_sha256": None,
                "visible_heldout_disagreement": bool(r.get("visible_heldout_disagreement")),
                "failure_classification": None,
            }
        )
    return out


def norm_e005(raw: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for r in raw["records"]:
        ev = r["evaluation"]
        patch = r["patch"]
        out.append(
            {
                "experiment": "E005",
                "tier": "hard",
                "provenance": r["provenance"],
                "case": r["case_id"],
                "case_key": f"E005:{r['case_id']}",
                "project": None,
                "experiment_case_id": r["case_id"],
                "run_id": r["run_id"],
                "condition": r["condition"],
                "model": r["model"],
                "session_id": r.get("session_id"),
                "success": bool(ev["task_success"]),
                "public": status(ev["public"]),
                "held_out": status(ev["heldout"]),
                "regression": status(ev["regression"]),
                "evaluation_status": ev["status"],
                "wall_time_seconds": float(r["wall_time_seconds"]),
                "steps": int(r["steps"]),
                "tool_calls": int(r["tool_calls"]),
                "prompt_tokens": int(r["tokens"]["prompt"]),
                "completion_tokens": int(r["tokens"]["completion"]),
                "cached_tokens": int(r["tokens"]["cached"]),
                "source_files_changed": len(patch["source_files_changed"]),
                "workspace_churn_files": int(patch["workspace_churn_files"]),
                "generated_or_environment_files": len(patch["generated_or_environment_files_changed"]),
                "lines_added": int(patch["line_counts"]["additions"]),
                "lines_deleted": int(patch["line_counts"]["deletions"]),
                "patch_sha256": patch.get("sha256"),
                "prompt_sha256": r.get("prompt_sha256"),
                "visible_heldout_disagreement": ev["public"] == "pass" and ev["heldout"] != "pass",
                "failure_classification": None,
            }
        )
    return out


def norm_e006(raw: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for r in raw["records"]:
        out.append(
            {
                "experiment": "E006",
                "tier": "very-hard",
                "provenance": r["provenance"],
                "case": r["case_id"],
                "case_key": f"E006:{r['case_id']}",
                "project": r.get("project"),
                "experiment_case_id": r["experiment_case_id"],
                "run_id": r["run_id"],
                "condition": r["condition"],
                "model": r["model"],
                "session_id": r.get("session_id"),
                "success": bool(r["task_success"]),
                "public": status(r["public"]),
                "held_out": status(r["heldout"]),
                "regression": status(r["regression"]),
                "evaluation_status": r["evaluation_status"],
                "wall_time_seconds": float(r["wall_time_seconds"]),
                "steps": int(r["steps"]),
                "tool_calls": int(r["tool_calls"]),
                "prompt_tokens": int(r["tokens"]["prompt"]),
                "completion_tokens": int(r["tokens"]["completion"]),
                "cached_tokens": int(r["tokens"]["cached"]),
                "source_files_changed": len(r["source_files_changed"]),
                "workspace_churn_files": int(r["workspace_churn_files"]),
                "generated_or_environment_files": len(r["generated_or_environment_files"]),
                "lines_added": int(r["lines_added"]),
                "lines_deleted": int(r["lines_deleted"]),
                "patch_sha256": r.get("patch_sha256"),
                "prompt_sha256": r.get("prompt_sha256"),
                "visible_heldout_disagreement": bool(r["visible_heldout_disagreement"]),
                "failure_classification": r.get("failure_classification"),
            }
        )
    return out


def load_records() -> list[dict[str, Any]]:
    e002 = json.loads((ROOT / "results/experiment-002-summary.json").read_text())
    e004 = json.loads((ROOT / "results/experiment-004-summary.json").read_text())
    e005 = json.loads((ROOT / "results/experiment-005-ledger.json").read_text())
    e006 = json.loads((ROOT / "results/experiment-006-ledger.json").read_text())
    records = norm_e002(e002) + norm_e004(e004) + norm_e005(e005) + norm_e006(e006)
    for r in records:
        r["tier_index"] = TIER_ORDER[r["tier"]]
    return records


def pairs(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for r in records:
        grouped[r["case_key"]][r["condition"]] = r
    output = []
    for case_key, sides in grouped.items():
        if set(sides) != {"M", "X"}:
            raise ValueError(f"unpaired case: {case_key}")
        m, x = sides["M"], sides["X"]
        if m["tier"] != x["tier"] or m["provenance"] != x["provenance"]:
            raise ValueError(f"pair metadata mismatch: {case_key}")
        if m["success"] and x["success"]:
            outcome = "both success"
        elif m["success"]:
            outcome = "Medium-only"
        elif x["success"]:
            outcome = "Max-only"
        else:
            outcome = "both fail"
        output.append(
            {
                "experiment": m["experiment"],
                "tier": m["tier"],
                "provenance": m["provenance"],
                "case": m["case"],
                "case_key": case_key,
                "medium_run": m["run_id"],
                "max_run": x["run_id"],
                "medium_success": m["success"],
                "max_success": x["success"],
                "outcome": outcome,
                "wall_time_delta_max_minus_medium": x["wall_time_seconds"] - m["wall_time_seconds"],
                "steps_delta_max_minus_medium": x["steps"] - m["steps"],
                "tool_calls_delta_max_minus_medium": x["tool_calls"] - m["tool_calls"],
                "prompt_tokens_delta_max_minus_medium": x["prompt_tokens"] - m["prompt_tokens"],
                "completion_tokens_delta_max_minus_medium": x["completion_tokens"] - m["completion_tokens"],
                "cached_tokens_delta_max_minus_medium": x["cached_tokens"] - m["cached_tokens"],
                "source_files_delta_max_minus_medium": x["source_files_changed"] - m["source_files_changed"],
                "workspace_churn_delta_max_minus_medium": x["workspace_churn_files"] - m["workspace_churn_files"],
                "visible_heldout_disagreement": m["visible_heldout_disagreement"] or x["visible_heldout_disagreement"],
            }
        )
    return sorted(output, key=lambda p: (TIER_ORDER[p["tier"]], p["case_key"]))


def metric_summary(records: list[dict[str, Any]], field: str) -> dict[str, Any]:
    values = [r[field] for r in records]
    return {
        "total": sum(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "n": len(values),
    }


def subset_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "runs": len(records),
        "successes": sum(r["success"] for r in records),
        "success_rate": sum(r["success"] for r in records) / len(records),
        "public_passes": sum(r["public"] == "pass" for r in records),
        "held_out_passes": sum(r["held_out"] == "pass" for r in records),
        "regression_passes": sum(r["regression"] == "pass" for r in records),
        "wall_time_seconds": metric_summary(records, "wall_time_seconds"),
        "steps": metric_summary(records, "steps"),
        "tool_calls": metric_summary(records, "tool_calls"),
        "prompt_tokens": metric_summary(records, "prompt_tokens"),
        "completion_tokens": metric_summary(records, "completion_tokens"),
        "cached_tokens": metric_summary(records, "cached_tokens"),
        "source_files_changed": metric_summary(records, "source_files_changed"),
        "workspace_churn_files": metric_summary(records, "workspace_churn_files"),
        "generated_or_environment_files": metric_summary(records, "generated_or_environment_files"),
        "lines_added": metric_summary(records, "lines_added"),
        "lines_deleted": metric_summary(records, "lines_deleted"),
    }


def wilson(successes: int, n: int, z: float = 1.959963984540054) -> list[float]:
    p = successes / n
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    radius = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denominator
    return [max(0.0, center - radius), min(1.0, center + radius)]


def exact_mcnemar(medium_only: int, max_only: int) -> float:
    n = medium_only + max_only
    if n == 0:
        return 1.0
    probs = [math.comb(n, k) * (0.5 ** n) for k in range(n + 1)]
    observed = min(medium_only, max_only)
    return min(1.0, 2 * sum(probs[: observed + 1]))


def failure_mode(records: list[dict[str, Any]]) -> str:
    if any(r["evaluation_status"] != "OK" for r in records):
        return "infrastructure/evaluator incident"
    if any(r["wall_time_seconds"] >= 7200 for r in records):
        return "timeout"
    if any(r["public"] == "fail" for r in records):
        return "visible/public failure"
    if any(r["held_out"] == "fail" for r in records) and all(r["regression"] == "pass" for r in records):
        return "held-out-only behavioral failure"
    if any(r["regression"] == "fail" for r in records):
        return "regression failure"
    return "successful repair"


def build_summary(records: list[dict[str, Any]], ps: list[dict[str, Any]]) -> dict[str, Any]:
    tier_data: dict[str, Any] = {}
    for tier in ("moderate", "hard", "very-hard"):
        tier_records = [r for r in records if r["tier"] == tier]
        cases = {r["case_key"] for r in tier_records}
        provenance = {
            p: len({r["case_key"] for r in tier_records if r["provenance"] == p})
            for p in ("historical-public", "newly-constructed-withheld")
        }
        tier_data[tier] = {
            "unique_cases": len(cases),
            "runs": len(tier_records),
            "provenance_cases": provenance,
            "conditions": {
                CONDITION_LABEL[c]: subset_summary([r for r in tier_records if r["condition"] == c])
                for c in ("M", "X")
            },
            "paired_outcomes": dict(Counter(p["outcome"] for p in ps if p["tier"] == tier)),
        }
    cumulative = {
        c: subset_summary([r for r in records if r["condition"] == c])
        for c in ("M", "X")
    }
    cumulative_pairs = dict(Counter(p["outcome"] for p in ps))
    failure_counts = Counter()
    failure_by_experiment: dict[str, Counter[str]] = defaultdict(Counter)
    for r in records:
        if not r["success"]:
            category = failure_mode([r])
            failure_counts[category] += 1
            failure_by_experiment[r["experiment"]][category] += 1
    stats = {}
    for label, selected in [
        ("moderate", [p for p in ps if p["tier"] == "moderate"]),
        ("hard", [p for p in ps if p["tier"] == "hard"]),
        ("very-hard", [p for p in ps if p["tier"] == "very-hard"]),
        ("cumulative-primary", ps),
    ]:
        m_only = sum(p["outcome"] == "Medium-only" for p in selected)
        x_only = sum(p["outcome"] == "Max-only" for p in selected)
        stats[label] = {
            "pairs": len(selected),
            "medium_only": m_only,
            "max_only": x_only,
            "discordant_pairs": m_only + x_only,
            "exact_mcnemar_two_sided_p": exact_mcnemar(m_only, x_only),
            "confidence_intervals_95_wilson": {
                c: {
                    "successes": len([r for r in records if r["condition"] == c and (label == "cumulative-primary" or r["tier"] == label) and r["success"]]),
                    "runs": len([r for r in records if r["condition"] == c and (label == "cumulative-primary" or r["tier"] == label)]),
                    "interval": wilson(
                        sum(r["condition"] == c and r["success"] and (label == "cumulative-primary" or r["tier"] == label) for r in records),
                        sum(r["condition"] == c and (label == "cumulative-primary" or r["tier"] == label) for r in records),
                    ),
                }
                for c in ("M", "X")
            },
        }
    return {
        "schema_version": 1,
        "publication_version": "4.0.0",
        "title": "Reasoning Effort Across the Software-Repair Difficulty Curve",
        "subtitle": "A 30-case paired evaluation of SWE-2 Medium and Max in Devin",
        "experiment": "publication-v4",
        "source_commit": SOURCE_COMMIT,
        "canonical_evidence": {
            "E002_summary": sha256(ROOT / "results/experiment-002-summary.json"),
            "E004_summary": sha256(ROOT / "results/experiment-004-summary.json"),
            "E005_ledger": sha256(ROOT / "results/experiment-005-ledger.json"),
            "E006_ledger": sha256(ROOT / "results/experiment-006-ledger.json"),
        },
        "primary": {
            "unique_bugs": len({r["case_key"] for r in records}),
            "valid_runs": len(records),
            "tiers": 3,
            "historical_cases": len({r["case_key"] for r in records if r["provenance"] == "historical-public"}),
            "withheld_cases": len({r["case_key"] for r in records if r["provenance"] == "newly-constructed-withheld"}),
            "conditions": {
                CONDITION_LABEL[c]: cumulative[c] for c in ("M", "X")
            },
            "paired_outcomes": cumulative_pairs,
        },
        "tiers": tier_data,
        "exploratory_statistics": {
            "method": "Exact two-sided conditional McNemar/binomial test on discordant paired outcomes; 95% Wilson intervals for proportions.",
            "caveat": "Small paired samples; intervals and p-values are exploratory and do not establish general model superiority or causality.",
            "by_tier": stats,
        },
        "failure_modes": {
            "run_level_mutually_exclusive_counts": dict(failure_counts),
            "by_experiment": {e: dict(v) for e, v in failure_by_experiment.items()},
            "public_pass_held_out_fail_runs": sum(r["public"] == "pass" and r["held_out"] == "fail" for r in records),
            "public_pass_held_out_fail_by_experiment": {
                e: sum(r["experiment"] == e and r["public"] == "pass" and r["held_out"] == "fail" for r in records)
                for e in ("E002", "E004", "E005", "E006")
            },
            "timeouts": sum(r["wall_time_seconds"] >= 7200 for r in records),
            "in_protocol_evaluator_incidents": sum(r["evaluation_status"] != "OK" for r in records),
        },
        "resource_ratios_E006_max_minus_medium": {
            field: metric_summary([r for r in records if r["tier"] == "very-hard" and r["condition"] == "X"], field)["mean"]
            / metric_summary([r for r in records if r["tier"] == "very-hard" and r["condition"] == "M"], field)["mean"]
            for field in ("wall_time_seconds", "steps", "tool_calls", "prompt_tokens", "completion_tokens", "cached_tokens")
        },
        "interpretation": {
            "observed": [
                "Moderate: Medium 10/10, Max 8/10.",
                "Hard: Medium 7/10, Max 6/10.",
                "Very-hard: Medium 7/10, Max 9/10.",
                "Primary cumulative: Medium 24/30, Max 23/30.",
                "Max produced two Max-only repairs and zero Medium-only repairs at the very-hard tier.",
            ],
            "supported": [
                "Additional reasoning effort changed observable repair trajectories.",
                "Additional effort did not provide a uniform correctness benefit across tiers.",
                "The value of increased effort may be conditional on task difficulty in this benchmark.",
            ],
            "not_established": [
                "General superiority of Max or Medium.",
                "A universal difficulty crossover point.",
                "A causal effect of hidden reasoning on repair quality.",
                "Training exposure or absence from training data.",
                "Generalization beyond this agent, model family, task sample, and protocol.",
            ],
        },
        "exclusions": {
            "E003": "Supplemental easier withheld replication; excluded from the 30-case primary denominator.",
            "E001": "Methodological permission-gating failure; excluded from capability evidence.",
        },
        "publication_outputs": {
            "report": "reports/devin-swe2-reasoning-effort-v4-final.md",
            "summary": "results/publication-v4-summary.json",
            "paired_csv": "results/publication-v4-paired-results.csv",
            "runs_csv": "results/publication-v4-runs.csv",
            "tier_summary_csv": "results/publication-v4-tier-summary.csv",
            "charts": "artifacts/publication-v4/charts/",
        },
    }


RUN_FIELDS = [
    "experiment", "tier", "provenance", "case", "case_key", "project", "experiment_case_id",
    "run_id", "condition", "model", "session_id", "success", "public", "held_out", "regression",
    "evaluation_status", "wall_time_seconds", "steps", "tool_calls", "prompt_tokens",
    "completion_tokens", "cached_tokens", "source_files_changed", "workspace_churn_files",
    "generated_or_environment_files", "lines_added", "lines_deleted", "patch_sha256",
    "prompt_sha256", "visible_heldout_disagreement", "failure_classification",
]
PAIR_FIELDS = [
    "experiment", "tier", "provenance", "case", "case_key", "medium_run", "max_run",
    "medium_success", "max_success", "outcome", "wall_time_delta_max_minus_medium",
    "steps_delta_max_minus_medium", "tool_calls_delta_max_minus_medium",
    "prompt_tokens_delta_max_minus_medium", "completion_tokens_delta_max_minus_medium",
    "cached_tokens_delta_max_minus_medium", "source_files_delta_max_minus_medium",
    "workspace_churn_delta_max_minus_medium", "visible_heldout_disagreement",
]


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field) for field in fields} for row in rows)


def font(path: str, size: int):
    return ImageFont.truetype(path, size)


MONO = "/System/Library/Fonts/SFNSMono.ttf"
DISPLAY = "/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf"
BG = "#0a0a08"
INK = "#e7dfcc"
MUTED = "#a59d8b"
GRID = "#3b3831"
MEDIUM = "#d6814e"
MAX = "#94b0c4"
BOTH = "#e7dfcc"
MED_ONLY = "#d6814e"
MAX_ONLY = "#94b0c4"
BOTH_FAIL = "#5c574d"


def canvas(title: str, subtitle: str, width: int = 1600, height: int = 900):
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    draw.text((80, 58), title.upper(), font=font(DISPLAY, 48), fill=INK)
    draw.text((82, 118), subtitle, font=font(MONO, 22), fill=MUTED)
    draw.line((80, 166, width - 80, 166), fill=INK, width=2)
    return image, draw


def label(draw, xy, text, size=20, fill=INK, anchor=None):
    draw.text(xy, str(text), font=font(MONO, size), fill=fill, anchor=anchor)


def legend(draw, items, x=90, y=825, gap=245):
    for index, (name, color) in enumerate(items):
        x0 = x + index * gap
        draw.rectangle((x0, y - 13, x0 + 22, y + 9), fill=color)
        label(draw, (x0 + 34, y), name, 18, MUTED, "lm")


def plot_area(draw, left=130, top=220, right=1510, bottom=750, y_max=10, y_ticks=None):
    y_ticks = y_ticks or [0, 2, 4, 6, 8, 10]
    for tick in y_ticks:
        y = bottom - (tick / y_max) * (bottom - top)
        draw.line((left, y, right, y), fill=GRID, width=1)
        label(draw, (left - 18, y), tick, 17, MUTED, "rm")
    draw.line((left, top, left, bottom), fill=INK, width=2)
    draw.line((left, bottom, right, bottom), fill=INK, width=2)
    return left, top, right, bottom


def save_chart(image: Image.Image, name: str):
    CHARTS.mkdir(parents=True, exist_ok=True)
    image.save(CHARTS / name, format="PNG", optimize=True)


def chart_success(summary: dict[str, Any]):
    image, draw = canvas("Success by difficulty tier", "Complete repairs; denominator = 10 unique cases per tier")
    left, top, right, bottom = plot_area(draw)
    tiers = ["moderate", "hard", "very-hard"]
    centers = [390, 820, 1250]
    for center, tier in zip(centers, tiers):
        for offset, cond, color in [(-62, "Medium", MEDIUM), (62, "Max", MAX)]:
            val = summary["tiers"][tier]["conditions"][cond]["successes"]
            x0, x1 = center + offset - 38, center + offset + 38
            y = bottom - val / 10 * (bottom - top)
            draw.rectangle((x0, y, x1, bottom), fill=color)
            label(draw, (center + offset, y - 18), f"{val}/10", 20, INK, "mb")
        label(draw, (center, bottom + 38), TIER_LABEL[tier], 20, INK, "ma")
    legend(draw, [("SWE-2 Medium", MEDIUM), ("SWE-2 Max", MAX)])
    save_chart(image, "success-by-difficulty-tier.png")


def chart_paired(summary: dict[str, Any]):
    image, draw = canvas("Paired outcome composition", "Each bar partitions the 10 paired cases in one tier")
    left, top, right, bottom = plot_area(draw, y_max=10)
    colors = [BOTH, MED_ONLY, MAX_ONLY, BOTH_FAIL]
    names = ["Both success", "Medium-only", "Max-only", "Both fail"]
    tiers = ["moderate", "hard", "very-hard"]
    centers = [390, 820, 1250]
    for center, tier in zip(centers, tiers):
        counts = summary["tiers"][tier]["paired_outcomes"]
        current = bottom
        for name, color in zip(names, colors):
            val = counts.get(name, 0)
            height = val / 10 * (bottom - top)
            draw.rectangle((center - 78, current - height, center + 78, current), fill=color)
            if val:
                label(draw, (center, current - height / 2), val, 20, BG if color == BOTH else INK, "mm")
            current -= height
        label(draw, (center, bottom + 38), TIER_LABEL[tier], 20, INK, "ma")
    legend(draw, list(zip(names, colors)), gap=290)
    save_chart(image, "paired-outcome-composition.png")


def chart_provenance(summary: dict[str, Any]):
    image, draw = canvas("Historical vs withheld success", "Complete repairs; each provenance subgroup has n = 5 cases")
    left, top, right, bottom = plot_area(draw, y_max=5, y_ticks=[0, 1, 2, 3, 4, 5])
    tiers = ["moderate", "hard", "very-hard"]
    centers = [390, 820, 1250]
    colors = [MEDIUM, MAX]
    labels = [("Hist M", "historical-public", "Medium"), ("Hist X", "historical-public", "Max"), ("Withheld M", "newly-constructed-withheld", "Medium"), ("Withheld X", "newly-constructed-withheld", "Max")]
    for center, tier in zip(centers, tiers):
        for i, (name, provenance, cond) in enumerate(labels):
            val = summary["tiers"][tier]["conditions"][cond]["successes"] if i < 2 else summary["tiers"][tier]["conditions"][cond]["successes"]
            subset = [r for r in ALL_RECORDS if r["tier"] == tier and r["provenance"] == provenance and r["condition"] == ("M" if cond == "Medium" else "X")]
            val = sum(r["success"] for r in subset)
            x = center - 135 + i * 90
            y = bottom - val / 5 * (bottom - top)
            draw.rectangle((x - 28, y, x + 28, bottom), fill=colors[i % 2])
            label(draw, (x, y - 15), f"{val}/5", 16, INK, "mb")
            label(draw, (x, bottom + 30), name, 14, MUTED, "ma")
        label(draw, (center, bottom + 75), TIER_LABEL[tier], 20, INK, "ma")
    legend(draw, [("Medium", MEDIUM), ("Max", MAX)])
    save_chart(image, "historical-vs-withheld-success.png")


def chart_wall(summary: dict[str, Any]):
    image, draw = canvas("Mean wall time by tier", "Seconds per run; means are computed from all valid primary records")
    left, top, right, bottom = plot_area(draw, y_max=800, y_ticks=[0, 200, 400, 600, 800])
    centers = [390, 820, 1250]
    for center, tier in zip(centers, ("moderate", "hard", "very-hard")):
        for offset, cond, color in [(-62, "Medium", MEDIUM), (62, "Max", MAX)]:
            val = summary["tiers"][tier]["conditions"][cond]["wall_time_seconds"]["mean"]
            x = center + offset
            y = bottom - val / 800 * (bottom - top)
            draw.rectangle((x - 38, y, x + 38, bottom), fill=color)
            label(draw, (x, y - 15), f"{val:.0f}", 18, INK, "mb")
        label(draw, (center, bottom + 38), TIER_LABEL[tier], 20, INK, "ma")
    legend(draw, [("SWE-2 Medium", MEDIUM), ("SWE-2 Max", MAX)])
    save_chart(image, "mean-wall-time-by-tier.png")


def chart_tokens(summary: dict[str, Any]):
    image, draw = canvas("Observable token use", "Mean tokens per run; prompt and completion are separate panels")
    panels = [(130, 220, 760, 750, "Prompt tokens", "prompt_tokens", 1_500_000), (840, 220, 1510, 750, "Completion tokens", "completion_tokens", 30_000)]
    for left, top, right, bottom, title, field, maximum in panels:
        draw.text((left, top - 38), title, font=font(DISPLAY, 30), fill=INK)
        for tick in [0, maximum / 2, maximum]:
            y = bottom - tick / maximum * (bottom - top)
            draw.line((left, y, right, y), fill=GRID, width=1)
            label(draw, (left - 15, y), f"{tick/1e6:.1f}M" if maximum > 100000 else f"{tick/1000:.0f}K", 15, MUTED, "rm")
        draw.line((left, top, left, bottom), fill=INK, width=2)
        draw.line((left, bottom, right, bottom), fill=INK, width=2)
        centers = (285, 540, 700) if left < 500 else (995, 1250, 1410)
        for center, tier in zip(centers, ("moderate", "hard", "very-hard")):
            for offset, cond, color in [(-24, "Medium", MEDIUM), (24, "Max", MAX)]:
                val = summary["tiers"][tier]["conditions"][cond][field]["mean"]
                y = bottom - val / maximum * (bottom - top)
                draw.rectangle((center + offset - 14, y, center + offset + 14, bottom), fill=color)
            label(draw, (center, bottom + 25), TIER_LABEL[tier], 15, INK, "ma")
    legend(draw, [("Medium", MEDIUM), ("Max", MAX)], x=900, y=820)
    save_chart(image, "token-use-by-tier.png")


def chart_unique(summary: dict[str, Any]):
    image, draw = canvas("Unique repairs by tier", "Paired disagreements only; a unique repair is successful under one condition")
    left, top, right, bottom = plot_area(draw, y_max=3, y_ticks=[0, 1, 2, 3])
    for center, tier in zip((390, 820, 1250), ("moderate", "hard", "very-hard")):
        m = summary["tiers"][tier]["paired_outcomes"].get("Medium-only", 0)
        x = summary["tiers"][tier]["paired_outcomes"].get("Max-only", 0)
        draw.rectangle((center - 75, bottom - m / 3 * (bottom - top), center + 75, bottom), fill=MED_ONLY)
        draw.rectangle((center - 75, bottom - (m + x) / 3 * (bottom - top), center + 75, bottom - m / 3 * (bottom - top)), fill=MAX_ONLY)
        if m: label(draw, (center, bottom - m / 6 * (bottom - top)), m, 20, INK, "mm")
        if x: label(draw, (center, bottom - (m + x / 2) / 3 * (bottom - top)), x, 20, INK, "mm")
        label(draw, (center, bottom + 38), TIER_LABEL[tier], 20, INK, "ma")
    legend(draw, [("Medium-only", MED_ONLY), ("Max-only", MAX_ONLY)])
    save_chart(image, "unique-repairs-by-tier.png")


def chart_case_wall(ps: list[dict[str, Any]]):
    image, draw = canvas("Paired wall time across primary cases", "Log-scaled seconds; line connects Medium and Max within each case", height=1600)
    left, top, right, bottom = 360, 220, 1510, 1370
    draw.line((left, top, left, bottom), fill=INK, width=2)
    draw.line((left, bottom, right, bottom), fill=INK, width=2)
    values = []
    by_key = {r["run_id"]: r["wall_time_seconds"] for r in ALL_RECORDS}
    ordered = [p for p in ps]
    lo, hi = 80, max(by_key.values()) * 1.1
    def xpos(value):
        return left + (math.log(value) - math.log(lo)) / (math.log(hi) - math.log(lo)) * (right - left)
    for tick in [100, 300, 1000, 3000]:
        if tick <= hi:
            x = xpos(tick)
            draw.line((x, top, x, bottom), fill=GRID, width=1)
            label(draw, (x, bottom + 20), f"{tick}s", 16, MUTED, "ma")
    row_h = (bottom - top) / len(ordered)
    current_tier = None
    for i, p in enumerate(ordered):
        y = top + row_h * (i + 0.5)
        if p["tier"] != current_tier:
            current_tier = p["tier"]
            draw.line((80, y - row_h / 2, right, y - row_h / 2), fill=INK, width=2)
            label(draw, (90, y - row_h / 2 + 8), TIER_LABEL[current_tier].upper(), 16, INK, "lm")
        xm, xx = xpos(by_key[p["medium_run"]]), xpos(by_key[p["max_run"]])
        color = MAX_ONLY if p["outcome"] == "Max-only" else MED_ONLY if p["outcome"] == "Medium-only" else BOTH_FAIL if p["outcome"] == "both fail" else GRID
        draw.line((xm, y, xx, y), fill=color, width=3)
        draw.ellipse((xm - 7, y - 7, xm + 7, y + 7), fill=MEDIUM)
        draw.ellipse((xx - 7, y - 7, xx + 7, y + 7), fill=MAX)
        label(draw, (left - 20, y), p["case"], 15, MUTED, "rm")
    legend(draw, [("Medium", MEDIUM), ("Max", MAX), ("Max-only pair", MAX_ONLY), ("Medium-only pair", MED_ONLY), ("Both fail", BOTH_FAIL)], x=400, y=1500, gap=220)
    save_chart(image, "paired-wall-time-all-cases.png")


def chart_cumulative(summary: dict[str, Any]):
    image, draw = canvas("Cumulative primary outcome", "30 unique bugs; 60 valid paired runs")
    left, top, right, bottom = plot_area(draw, y_max=30, y_ticks=[0, 10, 20, 30])
    for x, cond, val, color in [(650, "Medium", 24, MEDIUM), (950, "Max", 23, MAX)]:
        y = bottom - val / 30 * (bottom - top)
        draw.rectangle((x - 70, y, x + 70, bottom), fill=color)
        label(draw, (x, y - 20), f"{val}/30", 24, INK, "mb")
        label(draw, (x, bottom + 38), cond, 22, INK, "ma")
    legend(draw, [("Complete repairs", INK)])
    save_chart(image, "cumulative-primary-result.png")


def chart_failures(summary: dict[str, Any]):
    image, draw = canvas("Failure-mode composition", "Mutually exclusive run-level categories across the four primary experiments")
    counts = summary["failure_modes"]["run_level_mutually_exclusive_counts"]
    names = ["held-out-only behavioral failure", "visible/public failure", "regression failure", "timeout", "infrastructure/evaluator incident"]
    colors = [MAX_ONLY, MED_ONLY, BOTH_FAIL, "#817a67", "#b34d42"]
    total = sum(counts.get(n, 0) for n in names)
    left, top, right, bottom = plot_area(draw, y_max=max(1, total), y_ticks=list(range(0, total + 1, 2)))
    current = bottom
    for name, color in zip(names, colors):
        val = counts.get(name, 0)
        h = val / max(1, total) * (bottom - top)
        draw.rectangle((500, current - h, 1100, current), fill=color)
        if val: label(draw, (800, current - h / 2), f"{val}  {name}", 19, INK, "mm")
        current -= h
    legend(draw, [("Failure category", MAX_ONLY)])
    save_chart(image, "failure-mode-composition.png")


def main():
    global ALL_RECORDS
    ALL_RECORDS = load_records()
    if len(ALL_RECORDS) != 60:
        raise SystemExit(f"expected 60 primary runs, got {len(ALL_RECORDS)}")
    if len({r["case_key"] for r in ALL_RECORDS}) != 30:
        raise SystemExit("primary case count is not exactly 30")
    if {r["tier"] for r in ALL_RECORDS} != {"moderate", "hard", "very-hard"}:
        raise SystemExit("primary tier set is incorrect")
    ps = pairs(ALL_RECORDS)
    if len(ps) != 30:
        raise SystemExit(f"expected 30 primary pairs, got {len(ps)}")
    OUT.mkdir(parents=True, exist_ok=True)
    CHARTS.mkdir(parents=True, exist_ok=True)
    summary = build_summary(ALL_RECORDS, ps)
    (ROOT / "results/publication-v4-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(ROOT / "results/publication-v4-runs.csv", RUN_FIELDS, sorted(ALL_RECORDS, key=lambda r: (r["tier_index"], r["experiment"], r["case_key"], r["condition"])))
    write_csv(ROOT / "results/publication-v4-paired-results.csv", PAIR_FIELDS, ps)
    tier_rows = []
    for tier in ("moderate", "hard", "very-hard"):
        for cond in ("M", "X"):
            d = summary["tiers"][tier]["conditions"][CONDITION_LABEL[cond]]
            tier_rows.append(
                {
                    "tier": tier,
                    "condition": CONDITION_LABEL[cond],
                    "runs": d["runs"],
                    "successes": d["successes"],
                    "success_rate": d["success_rate"],
                    "wall_total_seconds": d["wall_time_seconds"]["total"],
                    "wall_mean_seconds": d["wall_time_seconds"]["mean"],
                    "wall_median_seconds": d["wall_time_seconds"]["median"],
                    "steps_total": d["steps"]["total"],
                    "steps_mean": d["steps"]["mean"],
                    "steps_median": d["steps"]["median"],
                    "tool_calls_total": d["tool_calls"]["total"],
                    "tool_calls_mean": d["tool_calls"]["mean"],
                    "tool_calls_median": d["tool_calls"]["median"],
                    "prompt_tokens_total": d["prompt_tokens"]["total"],
                    "prompt_tokens_mean": d["prompt_tokens"]["mean"],
                    "completion_tokens_total": d["completion_tokens"]["total"],
                    "completion_tokens_mean": d["completion_tokens"]["mean"],
                    "cached_tokens_total": d["cached_tokens"]["total"],
                    "cached_tokens_mean": d["cached_tokens"]["mean"],
                    "source_files_total": d["source_files_changed"]["total"],
                    "source_files_mean": d["source_files_changed"]["mean"],
                    "workspace_churn_total": d["workspace_churn_files"]["total"],
                    "workspace_churn_mean": d["workspace_churn_files"]["mean"],
                    "lines_added_total": d["lines_added"]["total"],
                    "lines_deleted_total": d["lines_deleted"]["total"],
                }
            )
    write_csv(ROOT / "results/publication-v4-tier-summary.csv", list(tier_rows[0]), tier_rows)
    chart_success(summary)
    chart_paired(summary)
    chart_provenance(summary)
    chart_wall(summary)
    chart_tokens(summary)
    chart_unique(summary)
    chart_case_wall(ps)
    chart_cumulative(summary)
    chart_failures(summary)
    chart_manifest = {
        "schema_version": 1,
        "publication_version": "4.0.0",
        "source_commit": SOURCE_COMMIT,
        "charts": {
            path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in sorted(CHARTS.glob("*.png"))
        },
    }
    (OUT / "MANIFEST.json").write_text(json.dumps(chart_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "primary_runs": len(ALL_RECORDS),
        "primary_cases": len({r["case_key"] for r in ALL_RECORDS}),
        "pairs": len(ps),
        "medium": summary["primary"]["conditions"]["Medium"]["successes"],
        "max": summary["primary"]["conditions"]["Max"]["successes"],
        "charts": len(list(CHARTS.glob("*.png"))),
        "failure_modes": summary["failure_modes"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
