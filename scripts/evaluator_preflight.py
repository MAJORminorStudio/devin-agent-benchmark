#!/usr/bin/env python3
"""Run public, held-out, and regression suites on every frozen baseline."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bugsinpy_harness as harness  # noqa: E402
import evaluator_environment as evaluator  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def validate_case(case: Dict[str, Any], phase1_root: Path, cases_dir: Path, env_root: Path, timeout: int) -> Dict[str, Any]:
    case_id = str(case["case_id"])
    spec = evaluator.case_spec(case_id)
    metadata = spec["metadata"]
    heldout_dir = (cases_dir / case_id).resolve()
    readiness = evaluator.readiness(env_root, case_id)
    result: Dict[str, Any] = {
        "case_id": case_id,
        "validated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "environment": readiness,
        "commands": {
            "public": case["test_command"],
            "heldout": metadata["heldout_commands"],
            "regression": metadata.get("regression_commands", []),
        },
        "sides": {},
    }
    if readiness["status"] != "pass":
        result["status"] = "EVALUATION_ERROR"
        result["error"] = "; ".join(readiness["problems"])
        return result
    for side in ("buggy", "fixed"):
        workspace = (phase1_root / case_id / "verification" / side).resolve()
        if not workspace.is_dir():
            result["status"] = "EVALUATION_ERROR"
            result["error"] = f"verification workspace missing: {workspace}"
            return result
        test_env = evaluator.process_environment(env_root, case_id, workspace=workspace)
        heldout_env = evaluator.process_environment(env_root, case_id, workspace=workspace)
        public = harness.execute_commands(case["test_command"], workspace, timeout, env=test_env)
        heldout = harness.execute_commands(metadata["heldout_commands"], heldout_dir, timeout, env=heldout_env)
        regression = harness.execute_commands(metadata.get("regression_commands", []), workspace, timeout, env=test_env)
        result["sides"][side] = {
            "workspace": str(workspace),
            "public": public,
            "heldout": heldout,
            "regression": regression,
        }
    result["buggy_public_fails"] = result["sides"]["buggy"]["public"]["overall"] == "fail"
    result["fixed_public_passes"] = result["sides"]["fixed"]["public"]["overall"] == "pass"
    result["buggy_heldout_fails"] = result["sides"]["buggy"]["heldout"]["overall"] == "fail"
    result["fixed_heldout_passes"] = result["sides"]["fixed"]["heldout"]["overall"] == "pass"
    result["buggy_regression_passes"] = result["sides"]["buggy"]["regression"]["overall"] == "pass"
    result["fixed_regression_passes"] = result["sides"]["fixed"]["regression"]["overall"] == "pass"
    result["status"] = "pass" if all(result[key] for key in (
        "buggy_public_fails", "fixed_public_passes", "buggy_heldout_fails",
        "fixed_heldout_passes", "buggy_regression_passes", "fixed_regression_passes",
    )) else "fail"
    return result


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "manifests/experiment-001.json")
    parser.add_argument("--cases-dir", type=Path, default=REPO_ROOT / "evaluation/experiment-001")
    parser.add_argument("--phase1-root", type=Path, default=REPO_ROOT / "results/runs/phase-1")
    parser.add_argument("--env-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "evaluation/experiment-001/preflight.json")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args(argv)
    manifest = harness.load_manifest(args.manifest)
    cases = [validate_case(case, args.phase1_root.resolve(), args.cases_dir.resolve(), args.env_root.resolve(), args.timeout) for case in manifest["cases"]]
    status = "pass" if all(item.get("status") == "pass" for item in cases) else "fail"
    output = {
        "status": status,
        "experiment_id": "experiment-001",
        "validated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "environment_root": str(args.env_root.expanduser().resolve()),
        "cases": cases,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
