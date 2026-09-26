#!/usr/bin/env python3
"""Validate publication claims and package hygiene against source records."""
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E7 = ROOT / "artifacts/experiment-007"
E8 = ROOT / "artifacts/experiment-008"
OUT = ROOT / "artifacts/publication-v5.0.0"

def j(path): return json.loads(path.read_text())
def rows(path): return [json.loads(s) for s in path.read_text().splitlines() if s]

e7=rows(E7/"E007-RUNS.jsonl"); e8=rows(E8/"E008-RUNS.jsonl")
assert len(e7)==90 and len({r["run_id"] for r in e7})==90 and len({r["session_export"] for r in e7})==90
assert len(e8)==33 and len({r["run_id"] for r in e8})==33 and len({r["session_id"] for r in e8})==33
assert len(e7)+len(e8)==123
hist={eff:sum(bool(r["success"]) for r in e7 if r["reasoning_effort"]==eff) for eff in ("medium","high","max")}
assert hist=={"medium":16,"high":18,"max":18},hist
summary=j(OUT/"data/publication_summary.json")
assert {k:v["successes"] for k,v in summary["E008_clean_recheck_of_E007"].items()}=={"medium":22,"high":24,"max":24}
assert {k:v["agreement"] for k,v in summary["original_to_clean_E007_agreement"].items()}=={"medium":24,"max":25}
assert summary["original_to_clean_E007_agreement"]["medium"]["stable_solves"]==20
assert summary["original_to_clean_E007_agreement"]["medium"]["stable_failures"]==4
assert summary["original_to_clean_E007_agreement"]["medium"]["original_only_solves"]==4
assert summary["original_to_clean_E007_agreement"]["medium"]["clean_E007_only_solves"]==2
assert summary["original_to_clean_E007_agreement"]["max"]["stable_solves"]==21
assert summary["original_to_clean_E007_agreement"]["max"]["stable_failures"]==4
assert summary["original_to_clean_E007_agreement"]["max"]["original_only_solves"]==2
assert summary["original_to_clean_E007_agreement"]["max"]["clean_E007_only_solves"]==3
rep=summary["E008_targeted_repeats"]
assert rep["selected_cases"]==9 and rep["selected_case_effort_conditions"]==11
assert rep["planned_and_completed"]==33 and rep["valid_final_evaluations"]==33
assert rep["passes"]==19 and rep["five_observation_passes"]==30 and rep["five_observation_denominator"]==55
assert rep["unanimous_conditions"]==6 and rep["mixed_conditions"]==5
assert rep["human_interventions"]==0 and rep["replacement_or_retry_sessions"]==0 and rep["actual_cost"]=="unknown"

clean=list(csv.DictReader((OUT/"data/e007_clean_rechecked_case_outcomes.csv").open()))
assert len(clean)==30
assert {e:sum(r[e]=="True" for r in clean) for e in ("medium","high","max")}=={"medium":22,"high":24,"max":24}
five=list(csv.DictReader((OUT/"data/five_observation_sequences.csv").open()))
assert len(five)==11
assert sum(sum(r[k]=="True" for k in ("original","e007_clean_recheck","e008_r1","e008_r2","e008_r3")) for r in five)==30
targeted=list(csv.DictReader((OUT/"data/e008_targeted_runs_sanitized.csv").open()))
assert len(targeted)==33 and sum(r["outcome"]=="True" for r in targeted)==19
assert all(r["actual_cost_status"]=="unknown" for r in targeted)

# Guard that release tables do not expose host paths, session names/IDs, raw
# traces, credentials, or a misleading overall 30/55 benchmark rate.
for name in ["e007_runs_sanitized.csv","e008_targeted_runs_sanitized.csv","case_level_replication.csv","five_observation_sequences.csv"]:
    data=(OUT/"data"/name).read_text()
    for forbidden in ("/Users/", "/Volumes/", "session_id", "session_export", "sk-"):
        assert forbidden not in data, (name,forbidden)
all_text="\n".join(p.read_text(errors="ignore") for p in OUT.rglob("*") if p.is_file() and p.suffix in {".md",".csv",".json"})
assert "30/55 benchmark score" not in all_text.lower()
assert "54.5% overall score" not in all_text.lower()
assert "actual cost is **unknown**" in all_text.lower() or '"actual_cost": "unknown"' in all_text.lower()
assert len(list((OUT/"figures").glob("*.png")))==7

# Verify source checksums and final release package checksums.
for directory in (E7,E8):
    checksum=directory/"checksums/SHA256SUMS.txt"
    if checksum.exists():
        subprocess.run(["shasum","-a","256","-c",str(checksum)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
checks=OUT/"checksums/SHA256SUMS.txt"
if checks.exists():
    subprocess.run(["shasum","-a","256","-c",str(checks)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
print(json.dumps({"status":"PASS","E007_sessions":len(e7),"E008_sessions":len(e8),"combined_sessions":123,
                  "historical_scores":hist,"clean_recheck":{k:v["successes"] for k,v in summary["E008_clean_recheck_of_E007"].items()},
                  "agreement":{k:v["agreement"] for k,v in summary["original_to_clean_E007_agreement"].items()},
                  "targeted_passes":f'{rep["passes"]}/33',"five_observation_passes":f'{rep["five_observation_passes"]}/55',
                  "figures":7,"actual_cost":"unknown"},indent=2))
