#!/usr/bin/env python3
"""
Auto-Replenish Engine for WorldQuant BRAIN Alpha Portal
Generates 1,000+ new high-multiplier Alphas across diverse universes and regions.
"""

import os
import json
import time
import random

BATCH_JOBS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "batch_jobs.json")

REGIONS = [
    ("CHN", "TOP2000U", 1),
    ("USA", "TOP3000", 1),
    ("EUR", "TOP2500", 1),
    ("JPN", "TOP1000", 0),
    ("ASI", "TOP1000", 1),
    ("IND", "TOP500", 1)
]

OPERATORS = ["ts_rank", "ts_zscore", "rank", "zscore", "ts_delta", "group_rank", "group_zscore", "ts_std_dev", "ts_mean"]
FIELDS = [
    "close", "open", "high", "low", "volume", "vwap", "returns",
    "fundamental_ebitda", "fundamental_net_income", "fundamental_sales",
    "sentiment_score_news", "news_volume_historical", "options_volume_flow",
    "snt_social_value", "snt_social_volume", "implied_volatility_call_30"
]
NEUTRALIZATIONS = ["SUBINDUSTRY", "INDUSTRY", "SECTOR", "MARKET"]

def generate_expression():
    op1 = random.choice(OPERATORS)
    f1 = random.choice(FIELDS)
    d1 = random.choice([5, 10, 20, 60, 120])
    
    op2 = random.choice(OPERATORS)
    f2 = random.choice(FIELDS)
    d2 = random.choice([10, 20, 30, 60])
    
    templates = [
        f"{op1}({f1}, {d1}) - {op2}({f2}, {d2})",
        f"-1 * {op1}({f1} / ({f2} + 0.001), {d1})",
        f"group_rank({op1}({f1}, {d1}), {random.choice(NEUTRALIZATIONS)})",
        f"zscore({op1}({f1}, {d1})) * ts_rank({f2}, {d2})",
        f"ts_zscore({f1} - {f2}, {d1})"
    ]
    return random.choice(templates)

def create_batch(batch_count=500):
    region, universe, delay = random.choice(REGIONS)
    timestamp = int(time.time())
    rand_suffix = random.randint(1000, 9999)
    batch_id = f"BATCH_{timestamp}_{rand_suffix}"
    
    items = []
    seen = set()
    for _ in range(batch_count):
        for _ in range(50):
            expr = generate_expression()
            neutral = random.choice(NEUTRALIZATIONS)
            key = f"{expr}_{neutral}"
            if key not in seen:
                seen.add(key)
                items.append({
                    "expression": expr,
                    "settings": {
                        "instrumentType": "EQUITY",
                        "region": region,
                        "universe": universe,
                        "delay": delay,
                        "decay": random.choice([0, 4, 10]),
                        "neutralization": neutral,
                        "truncation": 0.08,
                        "pasteurization": "ON",
                        "unitHandling": "VERIFY",
                        "nanHandling": "FILL_ZERO"
                    },
                    "dry_run": False,
                    "auto_submit": True,
                    "status": "QUEUED",
                    "result": None
                })
                break

    batch_data = {
        "batch_id": batch_id,
        "name": f"{region} D{delay} {universe} Multiplier Auto-Batch",
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

def auto_replenish_queue(min_threshold=1000, add_batches=2):
    if not os.path.exists(BATCH_JOBS_FILE):
        jobs = {}
    else:
        try:
            with open(BATCH_JOBS_FILE, "r", encoding="utf-8") as f:
                jobs = json.load(f)
        except Exception:
            jobs = {}
            
    remaining_total = 0
    for b in jobs.values():
        if isinstance(b, dict) and b.get("status") in ["RUNNING", "PENDING"]:
            tot = b.get("total", 0)
            comp = b.get("completed", 0)
            remaining_total += max(0, tot - comp)
            
    print(f"[AUTO-REPLENISH] Current queue remaining Alphas: {remaining_total}")
    if remaining_total < min_threshold:
        print(f"[AUTO-REPLENISH] Threshold ({min_threshold}) reached! Creating {add_batches} new batches (1,000 Alphas)...")
        for _ in range(add_batches):
            b_id, b_data = create_batch(500)
            jobs[b_id] = b_data
            print(f"[AUTO-REPLENISH] Added batch {b_id}: {b_data['name']}")
        
        with open(BATCH_JOBS_FILE, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2)
        return True
    return False

if __name__ == "__main__":
    auto_replenish_queue(min_threshold=1000, add_batches=2)
