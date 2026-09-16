#!/usr/bin/env python3
"""Validate Experiment 001 held-out suites against Phase 1 trees.

This command is evaluator-side only. It never copies a held-out file into an
agent workspace; it executes the test from its control-repository directory
with the selected buggy or fixed source tree on ``PYTHONPATH``.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bugsinpy_harness as harness  # noqa: E402
import evaluator_environment as evaluator_env  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit("expected JSON object: %s" % path)
    return value


def validate_case(
    case: Dict[str, Any],
    cases_dir: Path,
    phase1_root: Path,
    env_root: Path,
    timeout: int,
) -> Dict[str, Any]:
    case_id = str(case["case_id"])
    metadata_path = cases_dir / case_id / "metadata.json"
    metadata = read_json(metadata_path)
    if metadata.get("case_id") != case_id:
        raise SystemExit("metadata case mismatch: %s" % metadata_path)
    heldout_dir = metadata_path.parent.resolve()
    readiness = evaluator_env.readiness(env_root, case_id)
    if readiness["status"] != "pass":
        raise SystemExit("validation environment is not ready: " + "; ".join(readiness["problems"]))
    records: Dict[str, Any] = {
        "case_id": case_id,
        "validated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "environment": metadata.get("environment", {}),
        "heldout_command": metadata["heldout_commands"],
        "regression_commands": metadata.get("regression_commands", []),
        "sides": {},
    }
    for side in ("buggy", "fixed"):
        workspace = (phase1_root / case_id / "verification" / side).resolve()
        if not workspace.is_dir():
            raise SystemExit("verification workspace is missing: %s" % workspace)
        environment = evaluator_env.process_environment(env_root, case_id, workspace=workspace)
        heldout = harness.execute_commands(
            metadata["heldout_commands"], heldout_dir, timeout, env=environment
        )
        regression = harness.execute_commands(
            metadata.get("regression_commands", []), workspace, timeout, env=environment
        )
        records["sides"][side] = {
            "workspace": str(workspace),
            "heldout": heldout,
            "regression": regression,
        }
    records["buggy_heldout_fails"] = records["sides"]["buggy"]["heldout"]["overall"] == "fail"
    records["fixed_heldout_passes"] = records["sides"]["fixed"]["heldout"]["overall"] == "pass"
    records["buggy_regression_passes"] = records["sides"]["buggy"]["regression"]["overall"] == "pass"
    records["fixed_regression_passes"] = records["sides"]["fixed"]["regression"]["overall"] == "pass"
    records["reproducible"] = all(
        records[key]
        for key in (
            "buggy_heldout_fails",
            "fixed_heldout_passes",
            "buggy_regression_passes",
            "fixed_regression_passes",
        )
    )
    output_path = cases_dir / case_id / "validation.json"
    output_path.write_text(json.dumps(records, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return records


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "manifests/experiment-001.json")
    parser.add_argument("--cases-dir", type=Path, default=REPO_ROOT / "evaluation/experiment-001")
    parser.add_argument("--phase1-root", type=Path, default=REPO_ROOT / "results/runs/phase-1")
    parser.add_argument("--env-root", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args(argv)
    manifest = harness.load_manifest(args.manifest)
    records = [
        validate_case(case, args.cases_dir.resolve(), args.phase1_root.resolve(), args.env_root.resolve(), args.timeout)
        for case in manifest["cases"]
    ]
    result = {"status": "pass" if all(item["reproducible"] for item in records) else "fail", "cases": records}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
