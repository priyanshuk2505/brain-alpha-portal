#!/usr/bin/env python3
"""
Dedicated Region-Agnostic (GLB TOP3000) Simulation Processor
Extracts Super-Elite Alphas matching strict criteria:
  - Original Sharpe > 3.0  => Keep formula as is
  - Original Sharpe < -3.0 => Multiply by -1 * (expression)
Assigns to Dedicated Slot 8 and logs results to region_agnostic_alpha_results.csv.
"""

import os
import re
import csv
import json
import time

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
BATCH_JOBS_FILE = os.path.join(WORKSPACE_DIR, "batch_jobs.json")
REGION_AGNOSTIC_CSV = os.path.join(WORKSPACE_DIR, "region_agnostic_alpha_results.csv")

def extract_strict_super_elite_alphas():
    alphas = []
    seen = set()

    # 1. Parse elite_alphas.txt
    elite_path = os.path.join(WORKSPACE_DIR, "elite_alphas.txt")
    if os.path.exists(elite_path):
        with open(elite_path, "r", encoding="utf-8") as f:
            content = f.read()
        blocks = content.split("------------------------------------------------------------")
        for b in blocks:
            code_m = re.search(r"Code:\s*(.+)", b)
            sharpe_m = re.search(r"Sharpe:\s*([-\d.]+)", b)
            if code_m and sharpe_m:
                expr = code_m.group(1).strip()
                try:
                    s_val = float(sharpe_m.group(1))
                    # Strict Filter: Sharpe > 3.0 OR Sharpe < -3.0
                    if s_val > 3.0 or s_val < -3.0:
                        final_expr = f"-1 * ({expr})" if s_val < -3.0 else expr
                        key = final_expr.replace(" ", "")
                        if key not in seen:
                            seen.add(key)
                            alphas.append({"orig_sharpe": s_val, "orig_expr": expr, "final_expr": final_expr})
                except Exception:
                    pass

    # 2. Parse simulation_results.csv
    csv_path = os.path.join(WORKSPACE_DIR, "simulation_results.csv")
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if len(row) >= 11:
                    expr = row[10].strip()
                    try:
                        s_val = float(row[2])
                        # Strict Filter: Sharpe > 3.0 OR Sharpe < -3.0
                        if s_val > 3.0 or s_val < -3.0:
                            final_expr = f"-1 * ({expr})" if s_val < -3.0 else expr
                            key = final_expr.replace(" ", "")
                            if key not in seen:
                                seen.add(key)
                                alphas.append({"orig_sharpe": s_val, "orig_expr": expr, "final_expr": final_expr})
                    except Exception:
                        pass

    # Sort descending by absolute original Sharpe
    alphas.sort(key=lambda x: abs(x["orig_sharpe"]), reverse=True)
    return alphas

def create_region_agnostic_batch():
    super_elites = extract_strict_super_elite_alphas()
    print(f"[REGION-AGNOSTIC] Found {len(super_elites)} Super-Elite Alphas with strict |Sharpe| > 3.0 (Sharpe > 3.0 or Sharpe < -3.0)")

    items = []
    for idx, item in enumerate(super_elites):
        expr = item["final_expr"]
        items.append({
            "expression": expr,
            "orig_sharpe": item["orig_sharpe"],
            "settings": {
                "instrumentType": "EQUITY",
                "region": "GLB",
                "universe": "TOP3000",
                "delay": 1,
                "decay": 0,
                "neutralization": "SUBINDUSTRY",
                "truncation": 0.08,
                "pasteurization": "ON",
                "unitHandling": "VERIFY",
                "nanHandling": "OFF",
                "language": "FASTEXPR",
                "visualization": False
            },
            "dry_run": False,
            "auto_submit": True,
            "status": "QUEUED",
            "result": None,
            "dedicated_slot": 8
        })

    batch_id = "BATCH_REGION_AGNOSTIC_GLB"
    batch_data = {
        "batch_id": batch_id,
        "name": "Region Agnostic GLB TOP3000 Super-Elite Batch (Slot 8)",
        "region": "GLB",
        "universe": "TOP3000",
        "delay": 1,
        "status": "RUNNING",
        "total": len(items),
        "completed": 0,
        "progress": 0.0,
        "start_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dedicated_slot": 8,
        "items": items
    }

    # Save into batch_jobs.json
    jobs = {}
    if os.path.exists(BATCH_JOBS_FILE):
        try:
            with open(BATCH_JOBS_FILE, "r", encoding="utf-8") as f:
                jobs = json.load(f)
        except Exception:
            jobs = {}

    jobs[batch_id] = batch_data
    with open(BATCH_JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2)

    # Initialize CSV header if not exists
    if not os.path.exists(REGION_AGNOSTIC_CSV):
        with open(REGION_AGNOSTIC_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Index", "OriginalSharpe", "GLB_Sharpe", "GLB_Fitness", "GLB_Returns(%)", "GLB_Margin(bps)", "GLB_Turnover(%)", "FailedChecks", "PassFail", "AlphaID", "Expression"])

    print(f"[REGION-AGNOSTIC] Created batch '{batch_id}' with {len(items)} Super-Elite items assigned to Slot 8.")
    return batch_id

if __name__ == "__main__":
    create_region_agnostic_batch()
