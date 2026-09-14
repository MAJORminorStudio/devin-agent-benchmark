#!/usr/bin/env python3
"""Validate the frozen Experiment 001 protocol without invoking Devin."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bugsinpy_harness as harness  # noqa: E402
import devin_runner  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_ID_RE = re.compile(r"^E001-C0[1-5]-[MX]$")


def die(message: str) -> None:
    raise SystemExit(f"error: {message}")


def read_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        die(f"could not read {path}: {exc}")
    if not isinstance(value, dict):
        die(f"expected an object in {path}")
    return value


def validate(
    manifest_path: Path,
    runs_path: Path,
    config_path: Path,
    *,
    export_root: Optional[Path] = None,
    results_root: Optional[Path] = None,
) -> Dict[str, Any]:
    manifest = harness.load_manifest(manifest_path)
    runs_manifest = read_json(runs_path)
    config = read_json(config_path)
    cases = {case["experiment_case_id"]: case for case in manifest["cases"]}
    if set(cases) != {f"E001-C0{i}" for i in range(1, 6)}:
        die("case manifest must contain exactly E001-C01 through E001-C05")
    order = runs_manifest.get("run_order")
    runs = runs_manifest.get("runs")
    if not isinstance(order, list) or not isinstance(runs, list):
        die("run manifest must contain run_order and runs arrays")
    if len(order) != 10 or len(runs) != 10 or len(set(order)) != 10:
        die("run manifest must contain ten unique ordered runs")
    run_by_id = {item.get("run_id"): item for item in runs}
    if set(order) != set(run_by_id):
        die("run_order and runs do not contain the same IDs")
    if order != manifest.get("run_order"):
        die("primary manifest and run manifest have different frozen orders")
    condition_models = {key: value["model"] for key, value in config.get("conditions", {}).items()}
    if condition_models != {"M": "swe-2-medium", "X": "swe-2-max"}:
        die("frozen conditions must be swe-2-medium and swe-2-max")

    errors: List[str] = []
    counts = {"M": 0, "X": 0}
    prompt_bytes: Dict[str, bytes] = {}
    export_digests: Dict[str, str] = {}
    for run_id in order:
        run = run_by_id[run_id]
        if not isinstance(run_id, str) or not RUN_ID_RE.fullmatch(run_id):
            errors.append(f"invalid run ID: {run_id}")
            continue
        condition = run.get("condition")
        case_id = run.get("experiment_case_id")
        if condition not in condition_models:
            errors.append(f"invalid condition in {run_id}: {condition}")
        if case_id not in cases:
            errors.append(f"unknown case mapping in {run_id}: {case_id}")
            continue
        if run.get("model") != condition_models.get(condition):
            errors.append(f"model mismatch in {run_id}")
        if run.get("effort_level") != config["conditions"][condition]["effort_level"]:
            errors.append(f"effort mismatch in {run_id}")
        if run.get("status") != "frozen-pending":
            errors.append(f"run is not frozen-pending in {run_id}")
        counts[condition] += 1
        if export_root:
            workspace = export_root / run_id
            case_file = workspace / "CASE.json"
            audit_file = export_root / f"{run_id}.leak-audit.json"
            if not workspace.is_dir() or not case_file.is_file() or not audit_file.is_file():
                errors.append(f"missing fresh export/audit for {run_id}")
                continue
            safe_case = read_json(case_file)
            audit = read_json(audit_file)
            if safe_case.get("experiment_case_id") != case_id or safe_case.get("case_id") != cases[case_id]["case_id"]:
                errors.append(f"CASE.json mapping mismatch in {run_id}")
            if audit.get("status") != "pass" or audit.get("destination") != str(workspace.resolve()):
                errors.append(f"leak audit did not pass in {run_id}")
            prompt_bytes.setdefault(cases[case_id]["case_id"], (workspace / "TASK.md").read_bytes())
            if prompt_bytes[cases[case_id]["case_id"]] != (workspace / "TASK.md").read_bytes():
                errors.append(f"prompt is not stable for {run_id}")
            export_digests[run_id] = str(audit.get("export_sha256"))

    if counts != {"M": 5, "X": 5}:
        errors.append(f"condition counts are not balanced: {counts}")
    for case_id in cases.values():
        case_key = case_id["case_id"]
        pair = [item for item in runs if item.get("case_id") == case_key]
        if {item.get("condition") for item in pair} != {"M", "X"}:
            errors.append(f"case pair is incomplete: {case_key}")
        if export_root and len(pair) == 2:
            left = export_digests.get(pair[0]["run_id"])
            right = export_digests.get(pair[1]["run_id"])
            if left != right:
                errors.append(f"fresh exports differ within case pair: {case_key}")

    if results_root:
        results_root = results_root.expanduser().resolve()
        if results_root.exists() and any(results_root.iterdir()):
            errors.append(f"results root is not empty/fresh: {results_root}")

    if errors:
        die("; ".join(errors))
    return {
        "status": "pass",
        "experiment_id": manifest["experiment_id"],
        "run_count": len(runs),
        "condition_counts": counts,
        "run_order": order,
        "export_count": len(export_digests) if export_root else None,
        "results_root_checked": str(results_root) if results_root else None,
        "fusion": "excluded by exact frozen model IDs",
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "manifests/experiment-001.json")
    parser.add_argument("--runs-manifest", type=Path, default=REPO_ROOT / "manifests/experiment-001-runs.json")
    parser.add_argument("--config", type=Path, default=REPO_ROOT / "manifests/experiment-001-config.json")
    parser.add_argument("--export-root", type=Path)
    parser.add_argument("--results-root", type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(validate(args.manifest, args.runs_manifest, args.config, export_root=args.export_root, results_root=args.results_root), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
