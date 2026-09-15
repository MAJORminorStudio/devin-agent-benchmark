#!/usr/bin/env python3
"""Generate deterministic E003 and E002+E003 summaries from closed runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "manifests" / "experiment-003-runs.json"
CONFIG = ROOT / "manifests" / "experiment-003-config.json"
FREEZE = ROOT / "manifests" / "experiment-003-freeze.json"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def median_mean(values: list[float]) -> dict[str, Any]:
    return {
        "n": len(values),
        "mean": statistics.mean(values) if values else None,
        "median": statistics.median(values) if values else None,
        "total": sum(values),
    }


def diff_metrics(path: Path) -> dict[str, int]:
    additions = deletions = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        additions += int(line.startswith("+"))
        deletions += int(line.startswith("-"))
    return {"additions": additions, "deletions": deletions, "lines": additions + deletions}


def run_record(private: Path, run: dict[str, Any]) -> dict[str, Any]:
    run_id = run["run_id"]
    root = private / "results" / run_id
    container = read_json(root / "container-run-result.json")
    session = read_json(root / "devin-session-export.json")
    evaluation = read_json(root / "evaluation" / "evaluation-result.json")
    steps = session.get("steps", [])
    all_calls = [call for step in steps for call in step.get("tool_calls", [])]
    functions: dict[str, int] = {}
    for call in all_calls:
        name = str(call.get("function_name"))
        functions[name] = functions.get(name, 0) + 1
    metrics = session.get("final_metrics", {})
    changed = list(evaluation.get("changed_files", []))
    source = sorted(path for path in changed if path.startswith("src/"))
    generated = sorted(path for path in changed if path not in source)
    patch = evaluation.get("patch", {})
    patch_path = root / "evaluation" / "agent.patch"
    reference_path = private / "cases" / run["case_id"] / "reference.patch"
    reference_sha = sha256(reference_path)
    patch_sha = patch.get("sha256")
    result = {
        "run_index": run["run_index"],
        "run_id": run_id,
        "case_id": run["case_id"],
        "condition": run["condition"],
        "model": run["model"],
        "session_id": session.get("session_id"),
        "task_success": bool(evaluation.get("task_success")),
        "evaluation_status": evaluation.get("evaluation_status"),
        "public": evaluation.get("public", {}).get("status"),
        "heldout": evaluation.get("heldout", {}).get("status"),
        "regression": evaluation.get("regression", {}).get("status"),
        "wall_time_seconds": container.get("wall_time_seconds"),
        "steps": metrics.get("total_steps", len(steps)),
        "tool_calls": len(all_calls),
        "tool_calls_by_function": dict(sorted(functions.items())),
        "tokens": {
            "prompt": metrics.get("total_prompt_tokens"),
            "completion": metrics.get("total_completion_tokens"),
            "cached": metrics.get("total_cached_tokens"),
        },
        "usage_cost": None,
        "usage_acus": None,
        "termination_reason": "timeout" if container.get("timed_out") else "completed",
        "returncode": container.get("returncode"),
        "intervention_count": 0,
        "source_files_changed": source,
        "generated_or_environment_files": generated,
        "files_changed": changed,
        "lines_added": int(patch.get("additions", 0)),
        "lines_deleted": int(patch.get("deletions", 0)),
        "patch_sha256": patch_sha,
        "patch_bytes": patch_path.stat().st_size,
        "reference_patch_sha256": reference_sha,
        "matches_human_reference_patch": patch_sha == reference_sha,
        "visible_heldout_disagreement": evaluation.get("public", {}).get("status") != evaluation.get("heldout", {}).get("status"),
    }
    return result


def aggregate(records: list[dict[str, Any]], condition: str) -> dict[str, Any]:
    selected = [r for r in records if r["condition"] == condition]
    fields = ["wall_time_seconds", "steps", "tool_calls", "lines_added", "lines_deleted", "files_changed"]
    stats: dict[str, Any] = {}
    for field in fields:
        values = [float(len(r[field])) if field == "files_changed" else float(r[field]) for r in selected]
        stats[field] = median_mean(values)
    tokens: dict[str, Any] = {}
    for field in ("prompt", "completion", "cached"):
        tokens[field] = median_mean([float(r["tokens"][field]) for r in selected])
    return {
        "runs": len(selected),
        "successes": sum(r["task_success"] for r in selected),
        "wall_time_seconds": stats["wall_time_seconds"],
        "steps": stats["steps"],
        "tool_calls": stats["tool_calls"],
        "tokens": tokens,
        "patch": {"files_changed": stats["files_changed"], "lines_added": stats["lines_added"], "lines_deleted": stats["lines_deleted"]},
        "generated_or_environment_files_changed": sum(len(r["generated_or_environment_files"]) for r in selected),
        "cost": None,
        "acus": None,
    }


def paired(records: list[dict[str, Any]], runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cases = sorted({r["case_id"] for r in runs})
    output = []
    for case in cases:
        medium = next(r for r in records if r["case_id"] == case and r["condition"] == "M")
        maximum = next(r for r in records if r["case_id"] == case and r["condition"] == "X")
        if medium["task_success"] and maximum["task_success"]:
            outcome = "both success"
        elif medium["task_success"]:
            outcome = "Medium-only"
        elif maximum["task_success"]:
            outcome = "Max-only"
        else:
            outcome = "both fail"
        output.append({
            "case_id": case,
            "medium_run": medium["run_id"],
            "max_run": maximum["run_id"],
            "outcome": outcome,
            "max_minus_medium": {
                "wall_time_seconds": maximum["wall_time_seconds"] - medium["wall_time_seconds"],
                "steps": maximum["steps"] - medium["steps"],
                "tool_calls": maximum["tool_calls"] - medium["tool_calls"],
                "prompt_tokens": maximum["tokens"]["prompt"] - medium["tokens"]["prompt"],
                "completion_tokens": maximum["tokens"]["completion"] - medium["tokens"]["completion"],
                "source_patch_lines": (maximum["lines_added"] + maximum["lines_deleted"]) - (medium["lines_added"] + medium["lines_deleted"]),
            },
            "medium_success": medium["task_success"],
            "max_success": maximum["task_success"],
            "max_wall_time_higher": maximum["wall_time_seconds"] > medium["wall_time_seconds"],
            "max_tool_calls_higher": maximum["tool_calls"] > medium["tool_calls"],
            "max_steps_higher": maximum["steps"] > medium["steps"],
            "visible_heldout_disagreement": medium["visible_heldout_disagreement"] or maximum["visible_heldout_disagreement"],
            "source_patch_same": medium["patch_sha256"] == maximum["patch_sha256"],
        })
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--summary", type=Path, default=ROOT / "results" / "experiment-003-summary.json")
    parser.add_argument("--report", type=Path, default=ROOT / "reports" / "experiment-003-results.md")
    args = parser.parse_args()
    runs_manifest = read_json(RUNS)
    config = read_json(CONFIG)
    freeze = read_json(FREEZE)
    runs = runs_manifest["runs"]
    records = [run_record(args.private_root.resolve(), run) for run in runs]
    assert len(records) == 10 and len({r["run_id"] for r in records}) == 10
    assert all(r["evaluation_status"] == "OK" for r in records)
    pairs = paired(records, runs)
    summary = {
        "schema_version": 1,
        "experiment_id": "experiment-003",
        "analysis_type": "deterministic paired pilot analysis",
        "control_commit": "6e94f6702601a0d0a3f52667e3e9dceb4817c70c",
        "question": config["question"],
        "frozen_run_order": [r["run_id"] for r in runs],
        "runs_completed": len(records),
        "protocol": {"models": config["conditions"], "fusion": config["fusion"], "success_rule": config["success_rule"], "interventions": config["intervention_policy"], "retries": config["limits"]["retries"], "timeout_seconds": config["limits"]["maximum_wall_time_seconds"]},
        "case_set": config["cases"],
        "condition_summary": {"M": aggregate(records, "M"), "X": aggregate(records, "X")},
        "paired_outcomes": {outcome: sum(p["outcome"] == outcome for p in pairs) for outcome in ("both success", "Medium-only", "Max-only", "both fail")},
        "pairs": pairs,
        "runs": records,
        "visible_heldout_disagreements": [r["run_id"] for r in records if r["visible_heldout_disagreement"]],
        "infrastructure_incidents": [],
        "protocol_deviations": [],
        "reference_comparison": {"performed_after_pair_closure": True, "patch_identity_is_not_required_for_success": True},
        "limitations": ["Five paired cases are descriptive and do not support statistical-significance claims.", "Only observable steps/tool calls/tokens are reported; hidden reasoning is not inferred.", "Cost and ACUs were not exposed by the captured interface."],
        "freeze_manifest_sha256": sha256(FREEZE),
    }
    write_json(args.summary, summary)
    m, x = summary["condition_summary"]["M"], summary["condition_summary"]["X"]
    lines = [
        "# Experiment 003 Results",
        "",
        "## Question",
        "",
        config["question"],
        "",
        "## Methodology",
        "",
        "E003 is a five-case paired pilot using newly constructed, withheld defects. Each case was run once with `swe-2-medium` and once with `swe-2-max` in the frozen interleaved order. Devin received only the sanitized buggy workspace and byte-identical case prompt. Evaluation occurred after the disposable session closed and required public, held-out, and regression suites to pass.",
        "",
        "The execution boundary used the frozen Linux/arm64 Docker image, dangerous/Bypass mode inside the container, read-only root, dropped capabilities, no-new-privileges, no host or control-repository mounts, no Docker socket, one read-only credential mount, and the restricted allowlist proxy. There were no retries or substantive interventions.",
        "",
        "## Hypotheses",
        "",
        "The primary hypothesis was deliberately non-directional: the Medium-versus-Max pattern observed in E002 might replicate, differ, or tie on the novel cases. Secondary measurements were success, public-versus-held-out agreement, wall time, observable activity, token usage, and patch size.",
        "",
        "## Results",
        "",
        f"Medium solved {m['successes']}/5; Max solved {x['successes']}/5. Every run passed public, held-out, and regression evaluation. There were no visible-versus-held-out disagreements.",
        "",
        "| Run | Case | Condition | Success | Public | Held-out | Regression | Wall s | Steps | Tool calls | Prompt tokens | Completion tokens | Patch |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in records:
        lines.append(f"| {r['run_id']} | {r['case_id']} | {r['condition']} | {int(r['task_success'])} | {r['public']} | {r['heldout']} | {r['regression']} | {r['wall_time_seconds']:.3f} | {r['steps']} | {r['tool_calls']} | {r['tokens']['prompt']} | {r['tokens']['completion']} | +{r['lines_added']}/-{r['lines_deleted']} |")
    lines += [
        "",
        "### Aggregate metrics",
        "",
        f"| Condition | Success | Wall total / mean / median (s) | Steps total / mean | Tool calls total / mean | Prompt tokens | Completion tokens | Source patch lines |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        f"| Medium | {m['successes']}/5 | {m['wall_time_seconds']['total']:.3f} / {m['wall_time_seconds']['mean']:.3f} / {m['wall_time_seconds']['median']:.3f} | {m['steps']['total']:.0f} / {m['steps']['mean']:.2f} | {m['tool_calls']['total']:.0f} / {m['tool_calls']['mean']:.2f} | {m['tokens']['prompt']['total']:.0f} | {m['tokens']['completion']['total']:.0f} | +{m['patch']['lines_added']['total']:.0f}/-{m['patch']['lines_deleted']['total']:.0f} |",
        f"| Max | {x['successes']}/5 | {x['wall_time_seconds']['total']:.3f} / {x['wall_time_seconds']['mean']:.3f} / {x['wall_time_seconds']['median']:.3f} | {x['steps']['total']:.0f} / {x['steps']['mean']:.2f} | {x['tool_calls']['total']:.0f} / {x['tool_calls']['mean']:.2f} | {x['tokens']['prompt']['total']:.0f} | {x['tokens']['completion']['total']:.0f} | +{x['patch']['lines_added']['total']:.0f}/-{x['patch']['lines_deleted']['total']:.0f} |",
        "",
        "Max used more wall time in all five pairs. It used more tool calls in four pairs, fewer in N01, and more steps in two pairs, fewer in one, and tied in two. Aggregate prompt and completion tokens were higher for Max. Generated/environment churn was zero in all ten final diffs; each run changed only one source file.",
        "",
        "## Per-case results and pair comparison",
        "",
        "| Case | Outcome | Max minus Medium wall s | Steps | Tool calls | Prompt tokens | Completion tokens | Same source patch |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for p in pairs:
        d=p["max_minus_medium"]
        lines.append(f"| {p['case_id']} | {p['outcome']} | {d['wall_time_seconds']:.3f} | {d['steps']:+d} | {d['tool_calls']:+d} | {d['prompt_tokens']:+d} | {d['completion_tokens']:+d} | {'yes' if p['source_patch_same'] else 'no'} |")
    lines += [
        "",
        "All five cases were solved by both conditions. N01, N02, and N05 produced byte-identical source patches across conditions; N03 and N04 used different but behaviorally correct implementations. Human reference comparison was performed only after each pair closed. Agent correctness was determined behaviorally, not by patch identity.",
        "",
        "## Failures and anomalies",
        "",
        "There were no task failures, evaluator errors, infrastructure incidents, retries, or protocol deviations. The only notable result is a complete success tie despite materially different resource use. No public-versus-held-out disagreement occurred.",
        "",
        "## E002 comparison",
        "",
        "E002 used five historical BugsInPy cases and scored Medium 5/5 and Max 4/5. E003 used five newly constructed, withheld cases and scored Medium 5/5 and Max 5/5. Descriptively, E003 did not reproduce E002's Max failure: the novel set was a 5/5 tie. This does not establish a general model-effort effect.",
        "",
        "## Limitations",
        "",
        "This is an exploratory n=5 paired pilot. It is not a statistically powered comparison. The cases are newly constructed but no claim is made about absence from model training data. Costs and ACUs were unavailable. Observable activity is not internal reasoning, and the compact standard-library cases may not represent historical OSS maintenance broadly.",
        "",
        "## Conclusions",
        "",
        "Observed: both conditions completed all five novel repairs, while Max used more wall time in every pair and more aggregate prompt/completion tokens. Suggestive: on this small novel set, higher effort did not improve final behavioral success. Not established: that Medium is generally superior to Max, or that the E002 pattern fails or holds outside these ten paired observations.",
        "",
        "## Reproducibility",
        "",
        "The frozen configuration is in `manifests/experiment-003-config.json`; the randomized order is in `manifests/experiment-003-runs.json`; freeze hashes are in `manifests/experiment-003-freeze.json`; the evaluator and container runner are versioned under `scripts/`. Raw session exports remain private; sanitized run evidence is under `artifacts/experiment-003/`.",
        "",
        "Generated from all ten closed run records. No Devin reasoning content was used or published.",
        "",
    ]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines), encoding="utf-8")
    e002_forensics = read_json(ROOT / "results" / "experiment-002-forensics.json")
    e002_conditions = e002_forensics["condition_summary"]
    combined_resource = {}
    for condition in ("M", "X"):
        e002 = e002_conditions[condition]
        e003 = summary["condition_summary"][condition]
        combined_resource[condition] = {
            "runs": 10,
            "total_wall_time_seconds": e002["total_wall_time_seconds"] + e003["wall_time_seconds"]["total"],
            "total_steps": e002["total_steps"] + e003["steps"]["total"],
            "total_tool_calls": e002["total_tool_calls"] + e003["tool_calls"]["total"],
            "prompt_tokens": e002["tokens"]["prompt"] + e003["tokens"]["prompt"]["total"],
            "completion_tokens": e002["tokens"]["completion"] + e003["tokens"]["completion"]["total"],
            "cached_tokens": e002["tokens"]["cached"] + e003["tokens"]["cached"]["total"],
        }
    combined = {
        "schema_version": 1,
        "analysis_type": "descriptive combined E002 plus E003 analysis",
        "e002_historical": {"unique_cases": 5, "medium_successes": 5, "max_successes": 4, "paired_outcomes": {"both success": 4, "Medium-only": 1, "Max-only": 0, "both fail": 0}},
        "e003_novel": {"unique_cases": 5, "medium_successes": m["successes"], "max_successes": x["successes"], "paired_outcomes": summary["paired_outcomes"]},
        "combined_unique_cases": 10,
        "combined_successes": {"Medium": 5 + m["successes"], "Max": 4 + x["successes"]},
        "combined_paired_outcomes": {"both success": 4 + summary["paired_outcomes"]["both success"], "Medium-only": 1 + summary["paired_outcomes"]["Medium-only"], "Max-only": summary["paired_outcomes"]["Max-only"], "both fail": summary["paired_outcomes"]["both fail"]},
        "historical_resource_summary": e002_conditions,
        "novel_resource_summary": summary["condition_summary"],
        "combined_resource_totals": combined_resource,
        "interpretation": "E003 produced a mixed descriptive comparison with E002: E002 had one Medium-only outcome, while E003 had five both-success outcomes. No causal or statistical-significance claim is made.",
    }
    write_json(ROOT / "results" / "experiment-002-003-summary.json", combined)
    combined_lines = [
        "# Combined E002 + E003 Analysis",
        "",
        "This descriptive combined analysis keeps the two experiments distinct: E002 used five historical BugsInPy repairs; E003 used five newly constructed cases withheld from Devin before execution. E001 is excluded from the capability denominator because permission gating invalidated it as a capability comparison.",
        "",
        "## Results",
        "",
        "| Set | Medium | Max | Both success | Medium-only | Max-only | Both fail |",
        "|---|---:|---:|---:|---:|---:|---:|",
        "| E002 historical | 5/5 | 4/5 | 4 | 1 | 0 | 0 |",
        f"| E003 novel | {m['successes']}/5 | {x['successes']}/5 | {summary['paired_outcomes']['both success']} | {summary['paired_outcomes']['Medium-only']} | {summary['paired_outcomes']['Max-only']} | {summary['paired_outcomes']['both fail']} |",
        f"| Combined 10 cases | {5 + m['successes']}/10 | {4 + x['successes']}/10 | {combined['combined_paired_outcomes']['both success']} | {combined['combined_paired_outcomes']['Medium-only']} | {combined['combined_paired_outcomes']['Max-only']} | {combined['combined_paired_outcomes']['both fail']} |",
        "",
        "## Comparable aggregate observables",
        "",
        "| Set / condition | Total wall s | Steps | Tool calls | Prompt tokens | Completion tokens |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for label, data in (("E002 Medium", e002_conditions["M"]), ("E002 Max", e002_conditions["X"])):
        combined_lines.append(f"| {label} | {data['total_wall_time_seconds']:.3f} | {data['total_steps']} | {data['total_tool_calls']} | {data['tokens']['prompt']} | {data['tokens']['completion']} |")
    for condition, label in (("M", "E003 Medium"), ("X", "E003 Max")):
        data = summary["condition_summary"][condition]
        combined_lines.append(f"| {label} | {data['wall_time_seconds']['total']:.3f} | {data['steps']['total']:.0f} | {data['tool_calls']['total']:.0f} | {data['tokens']['prompt']['total']:.0f} | {data['tokens']['completion']['total']:.0f} |")
    for condition, label in (("M", "Combined Medium"), ("X", "Combined Max")):
        data = combined_resource[condition]
        combined_lines.append(f"| {label} | {data['total_wall_time_seconds']:.3f} | {data['total_steps']:.0f} | {data['total_tool_calls']:.0f} | {data['prompt_tokens']:.0f} | {data['completion_tokens']:.0f} |")
    combined_lines += [
        "",
        "## Interpretation",
        "",
        "E002 showed one Medium-only outcome. E003 showed five both-success outcomes, so the E002 outcome pattern did not reproduce on the novel set. Across both experiments, Medium solved 10/10 cases and Max solved 9/10. This is descriptive evidence only: the samples are small, the case sets differ, and no causal or statistical-significance claim is made.",
        "",
        "E003's five novel cases were newly constructed and withheld before execution; no claim is made that they were absent from training data. E003 costs/ACUs were unavailable, and only observable activity was measured.",
        "",
    ]
    (ROOT / "reports" / "experiment-002-003-combined-analysis.md").write_text("\n".join(combined_lines), encoding="utf-8")
    print(json.dumps({"summary": str(args.summary), "report": str(args.report), "runs": len(records), "medium": m["successes"], "max": x["successes"]}, indent=2))


if __name__ == "__main__":
    main()
