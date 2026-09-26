#!/usr/bin/env python3
"""Render publication figures from sanitized machine-readable v5 tables."""
import csv
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/publication-v5.0.0"
DATA = OUT / "data"
FIG = OUT / "figures"
FIG.mkdir(exist_ok=True)
try:
    regular = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)
    bold = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 30)
    medium = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 22)
    small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 15)
except OSError:
    regular = ImageFont.load_default()
    bold = medium = regular
    small = regular

NAVY = "#17212b"; MUTED = "#586879"; GRID = "#dce3e9"
BLUE = "#377eb8"; GOLD = "#e69f00"; PURPLE = "#8064a2"
GREEN = "#4c9f70"; RED = "#d95f59"; GREY = "#a9b4bf"
COLORS = {"Medium": BLUE, "High": GOLD, "Max": PURPLE, "Historical": GREY, "Clean recheck": GREEN}


def canvas(title, subtitle, height=800):
    img = Image.new("RGB", (1500, height), "white"); d = ImageDraw.Draw(img)
    d.text((55, 35), title, font=bold, fill=NAVY)
    d.text((57, 82), subtitle, font=regular, fill=MUTED)
    return img, d


def save(img, name): img.save(FIG / name)


def bars(data, effort_names, title, subtitle, filename, maxv=30, valuefmt=None):
    img, d = canvas(title, subtitle)
    left, right, top, bottom = 190, 1390, 175, 660
    for tick in range(0, maxv + 1, max(1, maxv // 5)):
        y = bottom - (bottom-top) * tick / maxv
        d.line((left, y, right, y), fill=GRID, width=1)
        d.text((75, y-11), str(tick), font=regular, fill=MUTED)
    n_groups = len(data); groupw = (right-left)/n_groups
    width = min(92, groupw/(len(effort_names)+2))
    for gi, (label, values) in enumerate(data):
        gx = left + groupw*(gi+.5)
        for ei, effort in enumerate(effort_names):
            value, denom = values[effort]
            x = gx + (ei-(len(effort_names)-1)/2)*(width+12)
            h = (bottom-top)*value/maxv
            d.rectangle((x-width/2,bottom-h,x+width/2,bottom),fill=COLORS[effort])
            label_text = valuefmt(value,denom) if valuefmt else f"{value}/{denom}"
            box=d.textbbox((0,0),label_text,font=regular)
            d.text((x-(box[2]-box[0])/2,bottom-h-30),label_text,font=regular,fill=NAVY)
            d.text((x-width/2,bottom+15),effort,font=small,fill=NAVY)
        b=d.textbbox((0,0),label,font=medium); d.text((gx-(b[2]-b[0])/2,bottom+48),label,font=medium,fill=NAVY)
    save(img, filename)


summary=json.loads((DATA/"publication_summary.json").read_text())
e7clean=json.loads((ROOT/"artifacts/experiment-008/E008-E007-EVALUATOR-RECHECK.json").read_text())
bars([("All 30 cases", {"Medium":(22,30),"High":(24,30),"Max":(24,30)})],
     ["Medium","High","Max"], "E007 outcomes after clean evaluator recheck",
     "Passes / 30 fixed cases; re-evaluations of preserved E007 workspaces, not new sessions.",
     "01-clean-e007-score-by-effort.png",30)

matrix=json.loads((ROOT/"artifacts/experiment-008/E008-REPLICATION-MATRIX.json").read_text())
# Use E007 difficulty summaries, with corrected very-hard rows from the recheck ledger.
historical_runs=[json.loads(x) for x in (ROOT/"artifacts/experiment-007/E007-RUNS.jsonl").read_text().splitlines() if x]
recheck_rows=[json.loads(x) for x in (ROOT/"artifacts/experiment-008/E008-E007-EVALUATOR-RECHECK.jsonl").read_text().splitlines() if x]
clean={(r["case_id"],r["effort"]): all(v["status"]=="pass" for v in r["evaluator_results"].values() if isinstance(v,dict) and "status" in v) for r in recheck_rows}
for r in historical_runs:
    clean.setdefault((r["case_id"],r["reasoning_effort"]), bool(r["success"]))
tiers=[]
for tier in ["moderate","hard","very-hard"]:
    values={}
    for effort in ["medium","high","max"]:
        count=sum(1 for case in matrix["cases"] if case["difficulty"]==tier and clean[(case["case_id"],effort)])
        values[effort.title()]=(count,10)
    tiers.append((tier.replace("-"," ").title(),values))
bars(tiers,["Medium","High","Max"],"Clean E007 passes by difficulty and effort",
     "Ten cases per difficulty tier; bars show passes / 10 after the clean evaluator recheck.",
     "02-clean-e007-by-difficulty-effort.png",10)

bars([("Medium",{"Historical":(16,30),"Clean recheck":(22,30)}),
      ("High",{"Historical":(18,30),"Clean recheck":(24,30)}),
      ("Max",{"Historical":(18,30),"Clean recheck":(24,30)})],
     ["Historical","Clean recheck"],"Historical E007 totals and E008 clean recheck",
     "Passes / 30 each; clean recheck evaluates the same saved agent workspaces.",
     "03-e007-historical-vs-clean-recheck.png",30)

case_rows=list(csv.DictReader((DATA/"case_level_replication.csv").open()))
img,d=canvas("Original benchmark vs clean E007: case-level agreement",
             "Each bar totals 30 paired cases; same aggregate count does not imply same cases solved.")
left,right,top,bottom=250,1310,180,615
cats=[("Stable solve",GREEN), ("Stable fail",GREY), ("Original only",RED), ("Clean E007 only",BLUE)]
for gi,effort in enumerate(["medium","max"]):
    counts=[0,0,0,0]
    for r in case_rows:
        o=r[f"original_{effort}"]=="True"; c=r[f"e007_clean_{effort}"]=="True"
        idx=0 if o and c else 1 if not o and not c else 2 if o else 3
        counts[idx]+=1
    x=430+gi*620; y=bottom
    for (label,color),count in zip(cats,counts):
        h=(bottom-top)*count/30
        d.rectangle((x-105,y-h,x+105,y),fill=color)
        if count: d.text((x-15,y-h/2-11),str(count),font=medium,fill="white" if color!=GREY else NAVY)
        y-=h
    d.text((x-45,bottom+20),effort.title(),font=medium,fill=NAVY)
d.text((180,680),"Stable solve: both pass  ·  Stable fail: both fail  ·  Directional changes: outcome differs",font=regular,fill=MUTED)
for i,(label,color) in enumerate(cats):
    x=250+(i%2)*560; y=730+(i//2)*30
    d.rectangle((x,y,x+18,y+18),fill=color); d.text((x+28,y-2),label,font=small,fill=NAVY)
save(img,"04-original-clean-case-agreement.png")

# Effort telemetry panels show observed E007 means and explicit denominators.
e7=json.loads((ROOT/"artifacts/experiment-007/E007-RESULTS.json").read_text())
metrics=[("Mean agent steps", "agent_steps_all", "steps"),
         ("Mean wall time", "wall_clock_seconds_all", "seconds"),
         ("Mean total token counters", "total_tokens_all", "tokens")]
img,d=canvas("E007 effort and execution telemetry",
             "All 90 sessions; denominators appear beside each value. High wall time n=29 because one wrapper duration is missing; no time imputed.",950)
for pi,(title,key,unit) in enumerate(metrics):
    y0=155+pi*245; d.text((70,y0),title,font=medium,fill=NAVY)
    maxval=max(e7["efficiency"][e][key]["mean"] for e in ["medium","high","max"])
    x0,x1=430,1390
    for j,effort in enumerate(["medium","high","max"]):
        y=y0+50+j*52; rec=e7["efficiency"][effort][key]; v=rec["mean"]; n=rec["n_available"]
        d.text((100,y-4),effort.title(),font=regular,fill=NAVY)
        d.rectangle((x0,y,x0+(x1-x0)*v/maxval,y+28),fill=COLORS[effort.title()])
        text=f"{v:.1f} {unit}  (n={n})"
        d.text((min(x1-190,x0+(x1-x0)*v/maxval+12),y+3),text,font=small,fill=NAVY)
save(img,"07-steps-tokens-timing-by-effort.png")

print("Rendered 5 source-derived figures; figures 05–06 were copied from audited E008 charts.")
