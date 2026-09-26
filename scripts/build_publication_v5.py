#!/usr/bin/env python3
"""Build a sanitized, versioned E007/E008 publication package from source ledgers."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E7 = ROOT / "artifacts/experiment-007"
E8 = ROOT / "artifacts/experiment-008"
OUT = ROOT / "artifacts/publication-v5.0.0"
FIG = OUT / "figures"
DATA = OUT / "data"


def read_json(path: Path):
    return json.loads(path.read_text())


def write_csv(path: Path, rows: list[dict], columns: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)
e7runs = [json.loads(line) for line in (E7 / "E007-RUNS.jsonl").read_text().splitlines() if line]
e8runs = [json.loads(line) for line in (E8 / "E008-RUNS.jsonl").read_text().splitlines() if line]
matrix = read_json(E8 / "E008-REPLICATION-MATRIX.json")
stability = read_json(E8 / "E008-STABILITY-ANALYSIS.json")
e7results = read_json(E7 / "E007-RESULTS.json")
recheck = read_json(E8 / "E008-E007-EVALUATOR-RECHECK.json")
recheck_rows = [json.loads(line) for line in (E8 / "E008-E007-EVALUATOR-RECHECK.jsonl").read_text().splitlines() if line]
diff_by_case = {c["case_id"]: c["difficulty"] for c in matrix["cases"]}

# Sanitized E007 run ledger: omit session names/IDs, raw command, paths, output,
# exports, prompt hashes, and all private planning/reasoning traces.
e7_public = []
for row in e7runs:
    e7_public.append({
        "case_id": row["case_id"], "difficulty": row["difficulty"],
        "effort": row["reasoning_effort"], "historical_evaluator_outcome": bool(row["success"]),
        "public_suite": row.get("public_result"), "heldout_suite": row.get("heldout_result"),
        "regression_suite": row.get("regression_result"), "agent_steps": row.get("agent_steps"),
        "wall_time_seconds": row.get("wall_clock_seconds"), "input_tokens": row.get("input_tokens"),
        "output_tokens": row.get("output_tokens"), "total_tokens": row.get("total_tokens"),
        "timing_available": row.get("wall_clock_seconds") is not None,
    })
write_csv(DATA / "e007_runs_sanitized.csv", e7_public, list(e7_public[0]))

# Replication table comes from the E008 machine-readable case matrix; historical
# E007 outcomes are independently joined from its preserved run ledger.
historical = {(r["case_id"], r["reasoning_effort"]): bool(r["success"]) for r in e7runs}
case_rows = []
for row in matrix["cases"]:
    out = {"case_id": row["case_id"], "difficulty": row["difficulty"]}
    for effort in ("medium", "max"):
        out[f"original_{effort}"] = bool(row[f"original_{effort}_outcome"])
        out[f"e007_historical_{effort}"] = historical[(row["case_id"], effort)]
        out[f"e007_clean_{effort}"] = bool(row[f"e007_{effort}_outcome"])
        out[f"clean_agreement_{effort}"] = bool(row[f"original_{effort}_outcome"]) == bool(row[f"e007_{effort}_outcome"])
    case_rows.append(out)
write_csv(DATA / "case_level_replication.csv", case_rows, list(case_rows[0]))

# Targeted E008 public ledger deliberately omits session IDs and all filesystem,
# command, export, trace, and credential-related fields.
e8_public = []
for row in e8runs:
    suites = row.get("final_suite_results") or {}
    e8_public.append({
        "run_slot": row["run_slot"], "case_id": row["case_id"], "difficulty": diff_by_case[row["case_id"]],
        "effort": row["effort"], "repetition": row["repetition"], "outcome": bool(row["final_task_success"]),
        "public_suite": suites.get("public"), "heldout_suite": suites.get("heldout"),
        "regression_suite": suites.get("regression"), "agent_steps": row.get("steps"),
        "wall_time_seconds": row.get("wall_time_seconds"), "input_tokens": row.get("input_tokens"),
        "output_tokens": row.get("output_tokens"), "total_tokens": row.get("total_tokens"),
        "initial_adapter_error": bool(row.get("evaluation_adapter_failure_preserved")),
        "human_interventions": row.get("intervention_count", 0), "actual_cost_status": "unknown",
    })
write_csv(DATA / "e008_targeted_runs_sanitized.csv", e8_public, list(e8_public[0]))

sequence_rows = []
for item in stability["conditions"]:
    sequence_rows.append({
        "case_id": item["case_id"], "difficulty": item["difficulty"], "effort": item["effort"],
        "original": bool(item["original_outcome"]), "e007_clean_recheck": bool(item["e007_clean_rechecked_outcome"]),
        "e008_r1": bool(item["e008_trials"][0]["outcome"]), "e008_r2": bool(item["e008_trials"][1]["outcome"]),
        "e008_r3": bool(item["e008_trials"][2]["outcome"]), "successes_out_of_five": item["solves_out_of_five"],
        "e008_repeats_successes_out_of_three": item["new_trial_solves"],
        "e008_repeat_consistency": item["new_trial_stability"],
    })
write_csv(DATA / "five_observation_sequences.csv", sequence_rows, list(sequence_rows[0]))

# Clean evaluator result by case and effort, retaining only binary outcomes.
clean_outcomes = dict(historical)
for row in recheck_rows:
    clean_outcomes[(row["case_id"], row["effort"])] = row["recheck_status"] == "valid" and all(
        result["status"] == "pass" for result in row["evaluator_results"].values() if isinstance(result, dict) and "status" in result
    )
clean_rows = []
for case_id, difficulty in diff_by_case.items():
    item = {"case_id": case_id, "difficulty": difficulty}
    for effort in ("medium", "high", "max"):
        item[effort] = clean_outcomes[(case_id, effort)]
    clean_rows.append(item)
write_csv(DATA / "e007_clean_rechecked_case_outcomes.csv", clean_rows, list(clean_rows[0]))

agreement = {}
for effort in ("medium", "max"):
    states = [(bool(r[f"original_{effort}"]), bool(r[f"e007_clean_{effort}"])) for r in case_rows]
    agreement[effort] = {
        "agreement": sum(a == b for a, b in states), "n": len(states),
        "stable_solves": sum(a and b for a, b in states),
        "stable_failures": sum(not a and not b for a, b in states),
        "original_only_solves": sum(a and not b for a, b in states),
        "clean_E007_only_solves": sum(not a and b for a, b in states),
    }
tiers = {}
for tier in ("moderate", "hard", "very-hard"):
    tiers[tier] = {effort: {"successes": sum(r[effort] for r in clean_rows if r["difficulty"] == tier), "n": 10}
                   for effort in ("medium", "high", "max")}

summary = {
    "agent_sessions": {"E007": len(e7runs), "E008": len(e8runs), "combined": len(e7runs) + len(e8runs)},
    "historical_E007_scores": {k: {"successes": v["successes"], "n": v["n"]} for k, v in e7results["scores"].items()},
    "E008_clean_recheck_of_E007": {k: {"successes": v["corrected_E007_total_successes"], "n": 30} for k, v in recheck.items()},
    "clean_E007_difficulty_tiers": tiers,
    "original_to_clean_E007_agreement": agreement,
    "E008_targeted_repeats": {
        "selected_cases": 9, "selected_case_effort_conditions": 11,
        "planned_and_completed": stability["attempted_run_slots"],
        "valid_final_evaluations": stability["valid_final_evaluations"],
        "passes": stability["new_trial_successes"], "new_trial_denominator": stability["new_trial_total"],
        "five_observation_passes": stability["five_observation_successes"],
        "five_observation_denominator": stability["five_observation_total"],
        "unanimous_conditions": sum(c["new_trial_stability"].startswith("unanimous") for c in stability["conditions"]),
        "mixed_conditions": sum(c["new_trial_stability"] == "mixed" for c in stability["conditions"]),
        "human_interventions": sum(r.get("intervention_count", 0) for r in e8runs),
        "initial_E002_adapter_errors": sum(bool(r.get("evaluation_adapter_failure_preserved")) for r in e8runs),
        "slot_10_serialization_recovered_without_rerun": True,
        "replacement_or_retry_sessions": 0,
        "actual_cost": "unknown",
    },
    "sources": {
        "historical_E007": "E007-RESULTS.json and E007-RUNS.jsonl",
        "clean_E007_recheck_and_case_matrix": "E008-E007-EVALUATOR-RECHECK.json and E008-REPLICATION-MATRIX.json",
        "targeted_repeats": "E008-RUNS.jsonl and E008-STABILITY-ANALYSIS.json",
    },
}
write_json(DATA / "publication_summary.json", summary)

# The manifest contains only public task design metadata; strips run IDs, host
# paths, private billing statement, and all workspace locations.
manifest = read_json(E7 / "E007-MANIFEST.json")
public_manifest = {
    "experiment_id": "E007", "case_count": 30,
    "difficulty_tier_counts": {"moderate": 10, "hard": 10, "very-hard": 10},
    "efforts": ["medium", "high", "max"], "runs_planned": 90,
    "case_effort_cells": [
        {"case_id": c["case_id"], "difficulty": c["difficulty"], "effort": effort}
        for c in manifest["cases"] for effort in ("medium", "high", "max")
    ],
    "note": "Sanitized manifest; private paths, session IDs, and command records are omitted.",
}
write_json(DATA / "e007_sanitized_manifest.json", public_manifest)

manifest8 = read_json(E8 / "E008-RERUN-MANIFEST-APPROVED-FROZEN.json")
write_json(DATA / "e008_sanitized_manifest.json", {
    "experiment_id": "E008", "selected_cases": len({c["case_id"] for c in manifest8["conditions"]}),
    "selected_conditions": len(manifest8["conditions"]), "trials_per_condition": 3,
    "planned_runs": sum(c["new_trials"] for c in manifest8["conditions"]),
    "actual_cost": "unknown", "conditions": [
        {"case_id": c["case_id"], "difficulty": c["difficulty"], "effort": c["effort"],
         "new_trials": c["new_trials"], "reason": c["why"]}
        for c in manifest8["conditions"]
    ],
})

# Keep the sequence and selected-repeat figure from the audited E008 source.
for source, target in [
    (E8 / "charts/07-five-outcome-sequences.png", FIG / "05-five-observation-sequences.png"),
    (E8 / "charts/08-three-repeat-frequencies.png", FIG / "06-targeted-repeat-consistency.png"),
]:
    shutil.copy2(source, target)

print(json.dumps({"output": str(OUT), "E007_runs": len(e7runs), "E008_runs": len(e8runs),
                  "sequences": len(sequence_rows), "summary": summary["E008_targeted_repeats"]}, indent=2))
