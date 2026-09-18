#!/usr/bin/env python3
"""
Generator script for IND D1 and ASI D1 Alphas using Templates 1, 2, and 3.
Creates BATCH_IND_D1_TEMPLATES and BATCH_ASI_D1_TEMPLATES and updates batch_jobs.json.
"""

import os
import json
import random
import time

BATCH_JOBS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "batch_jobs.json")
FIELDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extracted_fields.json")

# Load extracted fields if available
if os.path.exists(FIELDS_FILE):
    with open(FIELDS_FILE, "r", encoding="utf-8") as f:
        fields_data = json.load(f)
    IND_FIELDS = fields_data.get("ind_fields", [])
    ASI_FIELDS = fields_data.get("asi_fields", [])
else:
    IND_FIELDS = []
    ASI_FIELDS = []

# Fallback basic fields if needed
GENERIC_FIELDS = [
    "close", "open", "high", "low", "volume", "vwap", "returns",
    "fundamental_ebitda", "fundamental_net_income", "fundamental_sales",
    "capex", "roe", "equity"
]

if not IND_FIELDS:
    IND_FIELDS = GENERIC_FIELDS
if not ASI_FIELDS:
    ASI_FIELDS = GENERIC_FIELDS

GROUPS = ["subindustry", "subindustry", "industry"]
BUCKET_SIGNALS = ["cap", "returns", "volume", "vwap", "roe"]
RISK_FACTORS = ["volume", "cap", "returns", "vwap", "high", "low"]

def generate_template1_expr(field):
    d1 = random.choice([60, 65, 70, 75, 80])
    d2 = random.choice([40, 45, 50, 55, 60])
    d3 = random.choice([90, 120, 150, 180])
    s = 3
    h = random.choice([0.0002, 0.0003, 0.0004, 0.0005])
    group = random.choice(GROUPS)
    
    # Optionally wrap field with a ts_transform or rank
    transform_type = random.choice(["raw", "ts_rank", "rank", "ts_zscore", "ts_delta"])
    if transform_type == "ts_rank":
        x_expr = f"ts_rank({field}, {random.choice([10, 20, 30])})"
    elif transform_type == "rank":
        x_expr = f"rank({field})"
    elif transform_type == "ts_zscore":
        x_expr = f"ts_zscore({field}, {random.choice([20, 40, 60])})"
    elif transform_type == "ts_delta":
        x_expr = f"ts_delta({field}, {random.choice([5, 10, 20])})"
    else:
        x_expr = field

    expr = (
        f"data = winsorize(ts_backfill({x_expr}, {d1}), std={s}); "
        f"clean_signal = ts_regression(data, log(ts_mean(cap, {d2})), {d3}, rettype=0); "
        f"hump(group_neutralize(clean_signal, {group}), hump={h})"
    )
    return expr

def generate_template2_expr(field):
    bucket_sig = random.choice(BUCKET_SIGNALS)
    risk_fac = random.choice(RISK_FACTORS)
    d = random.choice([250, 252])
    h = 0.0002
    
    transform_type = random.choice(["raw", "rank", "ts_rank"])
    if transform_type == "rank":
        x_expr = f"rank({field})"
    elif transform_type == "ts_rank":
        x_expr = f"ts_rank({field}, {random.choice([10, 20, 60])})"
    else:
        x_expr = field

    expr = (
        f'grp = bucket(rank({bucket_sig}), range="0,1,0.2"); '
        f"alpha = scale(group_neutralize({x_expr}, grp)); "
        f"factor1 = scale({risk_fac}); "
        f"hump(ts_vector_neut(alpha, factor1, {d}), hump={h})"
    )
    return expr

def generate_template3_expr(field):
    d1 = random.choice([20, 30, 40, 50, 60])
    d2 = random.choice([120, 180, 250, 252])
    group1 = random.choice(GROUPS)
    expr = f"group_rank(ts_av_diff(ts_backfill({field}, {d1}), {d2}), {group1})"
    return expr

def build_batch(region, universe, delay, fields, count=500, prefix=""):
    timestamp = int(time.time())
    batch_id = f"BATCH_{prefix}_{region}_D{delay}_{timestamp}"
    
    settings = {
        "instrumentType": "EQUITY",
        "region": region,
        "universe": universe,
        "delay": delay,
        "decay": 5,
        "neutralization": "INDUSTRY",
        "truncation": 0.08,
        "pasteurization": "ON",
        "unitHandling": "VERIFY",
        "nanHandling": "FILL_ZERO",
        "language": "FASTEXPR"
    }
    
    items = []
    seen = set()
    
    # We distribute across Template 1 (50%), Template 2 (25%), Template 3 (25%)
    while len(items) < count:
        field = random.choice(fields)
        tmpl_choice = random.choices([1, 2, 3], weights=[50, 25, 25])[0]
        
        if tmpl_choice == 1:
            expr = generate_template1_expr(field)
        elif tmpl_choice == 2:
            expr = generate_template2_expr(field)
        else:
            expr = generate_template3_expr(field)
            
        if expr not in seen:
            seen.add(expr)
            items.append({
                "id": f"{batch_id}_{len(items)}",
                "expression": expr,
                "settings": settings.copy(),
                "status": "QUEUED",
                "dry_run": False,
                "auto_submit": True,
                "result": None
            })
            
    batch_data = {
        "batch_id": batch_id,
        "name": f"{region} D{delay} ({universe}) Template 1/2/3 Alpha Batch ({len(items)} Alphas)",
        "region": region,
        "universe": universe,
        "delay": delay,
        "status": "RUNNING",
        "total": len(items),
        "completed": 0,
        "progress": 0.0,
        "start_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "items": items
    }
    return batch_id, batch_data

def main():
    print(f"Loading {len(IND_FIELDS)} IND fields and {len(ASI_FIELDS)} ASI fields...")
    
    # Generate IND D1 Batch
    ind_batch_id, ind_batch_data = build_batch("IND", "TOP500", 1, IND_FIELDS, count=500, prefix="TEMPLATE")
    print(f"Generated IND Batch: {ind_batch_id} with {len(ind_batch_data['items'])} Alphas.")
    
    # Generate ASI D1 Batch
    asi_batch_id, asi_batch_data = build_batch("ASI", "TOP500", 1, ASI_FIELDS, count=500, prefix="TEMPLATE")
    print(f"Generated ASI Batch: {asi_batch_id} with {len(asi_batch_data['items'])} Alphas.")
    
    # Load batch_jobs.json
    jobs = {}
    if os.path.exists(BATCH_JOBS_FILE):
        try:
            with open(BATCH_JOBS_FILE, "r", encoding="utf-8") as f:
                jobs = json.load(f)
        except Exception as e:
            print(f"Error loading {BATCH_JOBS_FILE}: {e}")
            
    jobs[ind_batch_id] = ind_batch_data
    jobs[asi_batch_id] = asi_batch_data
    
    with open(BATCH_JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2)
        
    print(f"Successfully added {ind_batch_id} and {asi_batch_id} to {BATCH_JOBS_FILE}!")

if __name__ == "__main__":
    main()
