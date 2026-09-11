#!/usr/bin/env python3
"""
WorldQuant BRAIN Advanced Alpha Generator (Elite TOP3000 Model)
Autonomously generates, simulates, logs, and submits mathematical trading signals
using strictly 100% coverage price/volume data and advanced volume-weighted momentum structures.
"""

import os
import re
import csv
import sys
import json
import time
import random
import argparse
import requests

# PLACEHOLDER FOR USER COOKIE
COOKIE = "_fbp=fb.1.1778595947954.838983336151760867; _ga=GA1.1.687920460.1778595944; _ga_9RN6WVT1K1=GS2.1.s1781431572$o106$g1$t1781431659$j43$l0$h0; _rdt_uuid=1778595944372.55b2243d-1bc9-440f-a27d-c17c7e25a64c; t=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI3b3l1Q1VZVVZ2UzJ6amlEbklXZTFXVlpEeWduVDhIWCIsImV4cCI6MTc4MTQ0NjA0MiwiYW1yIjpbInB3ZCIsImZhY2UiLCJjYXB0Y2hhIl19.QWgc5U5GNrtlSOhochnFbvUx5ZISINW4tjWwp8wPamA; _gcl_au=1.1.326319197.1778595941.355378989.1781431599.1781431598; _ga_FXKNEPLB1N=GS2.1.s1779733566$o7$g0$t1779733566$j60$l0$h0; __zlcmid=1XcoWMCkz0Gybrj; cookieyes-consent=consentid:V3N1Q1lGeXMxZWJjQU5ienR2TEtiUnlGMTdIN3k3cFA,consent:yes,action:yes,necessary:yes,functional:yes,analytics:yes,performance:yes,advertisement:yes,other:yes"

# 1. The High-Octane Alternative Data Pool (100% Coverage Target)
# Removing basic price data to focus on Options Skew, Sentiment, and Analyst Derivatives
DATA_POOL = [
    "implied_volatility_mean_skew_10", 
    "put_call_ratio_options", 
    "call_breakeven_10",
    "snt_social_volume_fast_d1", 
    "nws18_qep_fast_d1", 
    "nws18_bee_fast_d1",
    "analyst_revision_rank_derivative",
    "earnings_certainty_rank_derivative",
    "parkinson_volatility_10",
    "returns"
]

def generate_alpha():
    """
    Randomly selects ONE of three structures and applies the absolute assembly line:
    Template 1 (Trend & Volume Acceleration):
      core = f"(rank(ts_delta(rank({ds_all}), {w1})) * rank(ts_delta(rank(volume), {w2})))"
    Template 2 (Volatility Adjusted Momentum):
      core = f"(rank(ts_delta(rank({ds_all}), {w1})) * rank(parkinson_volatility_10))"
    Template 3 (Liquidity Rank Convergence):
      core = f"(rank(rank({ds_all}) - rank(adv20)))"
    """
    template_type = random.choice(["1", "2", "3"])
    w1 = random.choice([2, 3, 5, 10])
    w2 = random.choice([2, 3, 5, 10])
    decay = random.choice([2, 3, 5])
    sign = random.choice(["1", "-1"])
    
    ds_all = random.choice(DATA_POOL)
    
    if template_type == "1":
        core = f"(rank(ts_delta(rank({ds_all}), {w1})) * rank(ts_delta(rank(volume), {w2})))"
    elif template_type == "2":
        core = f"(rank(ts_delta(rank({ds_all}), {w1})) * rank(parkinson_volatility_10))"
    else: # Template 3
        core = f"(rank(rank({ds_all}) - rank(adv20)))"
        
    alpha = f"normalize(ts_decay_linear(zscore(group_neutralize(({core} * rank(adv20) * {sign}), market)), {decay}))"
    return alpha

def mutate_alpha(code):
    """
    Parses the core, sign, and decay from:
    normalize(ts_decay_linear(zscore(group_neutralize(({core} * rank(adv20) * {sign}), market)), decay))
    Then mutates target parameters (ds_all, w1/w2, or sign) strictly under mutator lockdown.
    """
    decay = random.choice([2, 3, 5])
    core = None
    sign = random.choice(["1", "-1"])
    
    wrapper_match = re.match(
        r'^normalize\(ts_decay_linear\(zscore\(group_neutralize\(\((.*) \* rank\(adv20\) \* (-?1)\),\s*market\)\),\s*(\d+)\)\)$',
        code
    )
    
    if wrapper_match:
        core = wrapper_match.group(1)
        sign = wrapper_match.group(2)
        decay = int(wrapper_match.group(3))
    else:
        return generate_alpha()
        
    template_type = None
    ds_all = None
    w1 = None
    w2 = None
    
    # Check template structures inside core:
    if "ts_delta(rank(volume)" in core or "delta(rank(volume)" in core:
        template_type = "1"
        match_1 = re.search(
            r'rank\((?:ts_)?delta\(rank\((\w+)\),\s*(\d+)\)\)\s*\*\s*rank\((?:ts_)?delta\(rank\(volume\),\s*(\d+)\)\)',
            core
        )
        if match_1:
            ds_all = match_1.group(1)
            w1 = int(match_1.group(2))
            w2 = int(match_1.group(3))
        else:
            ds_all = random.choice(DATA_POOL)
            w1 = random.choice([2, 3, 5, 10])
            w2 = random.choice([2, 3, 5, 10])
            
    elif "parkinson_volatility_10" in core:
        template_type = "2"
        match_2 = re.search(
            r'rank\((?:ts_)?delta\(rank\((\w+)\),\s*(\d+)\)\)\s*\*\s*rank\(parkinson_volatility_10\)',
            core
        )
        if match_2:
            ds_all = match_2.group(1)
            w1 = int(match_2.group(2))
        else:
            ds_all = random.choice(DATA_POOL)
            w1 = random.choice([2, 3, 5, 10])
        w2 = None
        
    elif "rank(adv20)" in core or "-" in core:
        template_type = "3"
        match_3 = re.search(r'rank\(rank\((\w+)\)\s*-\s*rank\(adv20\)\)', core)
        if match_3:
            ds_all = match_3.group(1)
        else:
            ds_all = random.choice(DATA_POOL)
        w1, w2 = None, None
        
    else:
        return generate_alpha()
        
    if ds_all not in DATA_POOL:
        ds_all = random.choice(DATA_POOL)
        
    if w1 and w1 not in [2, 3, 5, 10]:
        w1 = random.choice([2, 3, 5, 10])
    if w2 and w2 not in [2, 3, 5, 10]:
        w2 = random.choice([2, 3, 5, 10])
        
    mutatable = ["sign"]
    if template_type == "1":
        mutatable.extend(["ds_all", "w1", "w2"])
    elif template_type == "2":
        mutatable.extend(["ds_all", "w1"])
    elif template_type == "3":
        mutatable.extend(["ds_all"])
        
    target = random.choice(mutatable)
    
    if target == "sign":
        sign = "-1" if sign == "1" else "1"
    elif target == "ds_all":
        choices = [d for d in DATA_POOL if d != ds_all]
        ds_all = random.choice(choices) if choices else ds_all
    elif target == "w1":
        choices = [w for w in [2, 3, 5, 10] if w != w1]
        w1 = random.choice(choices) if choices else w1
    elif target == "w2":
        choices = [w for w in [2, 3, 5, 10] if w != w2]
        w2 = random.choice(choices) if choices else w2
        
    if template_type == "1":
        new_core = f"(rank(ts_delta(rank({ds_all}), {w1})) * rank(ts_delta(rank(volume), {w2})))"
    elif template_type == "2":
        new_core = f"(rank(ts_delta(rank({ds_all}), {w1})) * rank(parkinson_volatility_10))"
    else:
        new_core = f"(rank(rank({ds_all}) - rank(adv20)))"
        
    new_alpha = f"normalize(ts_decay_linear(zscore(group_neutralize(({new_core} * rank(adv20) * {sign}), market)), {decay}))"
    return new_alpha

# Historical Alphas CSV Helpers
def migrate_csv_file():
    csv_file = "simulation_results.csv"
    if not os.path.exists(csv_file):
        return
    try:
        with open(csv_file, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if not rows:
            return
        header = rows[0]
        if "FailedChecks" not in header:
            print("Migrating simulation_results.csv to add FailedChecks column...")
            header.append("FailedChecks")
            header.append("Code")
            for i in range(1, len(rows)):
                while len(rows[i]) < len(header):
                    rows[i].append("")
            with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(rows)
    except Exception as e:
        print(f"Failed to migrate CSV: {e}")

def get_historical_alphas():
    csv_file = "simulation_results.csv"
    alphas = []
    if not os.path.exists(csv_file):
        return alphas
    try:
        with open(csv_file, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                if row[0] == "Status" or (row[0] == "SUCCESS" and "fcf_yield_times_forward_roe" in "".join(row)):
                    if "Sharpe" in row or "Code" in row:
                        continue
                status = row[0].strip()
                if status not in ["SUCCESS", "FAILED", "ERROR"]:
                    continue
                code = ""
                for cell in reversed(row):
                    if any(op in cell for op in ["normalize", "decay", "ts_", "correlation", "delta", "rank", "log"]):
                        code = cell.strip()
                        break
                if not code:
                    continue
                def to_fraction(pct_str):
                    try:
                        return float(pct_str) / 100.0 if pct_str else 0.0
                    except ValueError:
                        return 0.0
                def to_float(val_str):
                    try:
                        return float(val_str) if val_str else 0.0
                    except ValueError:
                        return 0.0
                sharpe = to_float(row[1]) if len(row) > 1 else 0.0
                fitness = to_float(row[2]) if len(row) > 2 else 0.0
                returns = to_fraction(row[3]) if len(row) > 3 else 0.0
                drawdown = to_fraction(row[4]) if len(row) > 4 else 0.0
                margin = (to_float(row[5]) / 10000.0) if len(row) > 5 else 0.0
                turnover = to_fraction(row[6]) if len(row) > 6 else 0.0
                failed_checks = []
                if len(row) >= 12:
                    try:
                        code_idx = row.index(code)
                        if code_idx > 0:
                            failed_checks_str = row[code_idx - 1]
                            if any(check in failed_checks_str for check in ["LOW_SHARPE", "LOW_FITNESS", "SELF_CORRELATION", "CONCENTRATED_WEIGHT", "INCOMPATIBLE_UNIT", "LOW_SUB_UNIVERSE_SHARPE"]):
                                failed_checks = [c.strip() for c in failed_checks_str.split(";")]
                    except ValueError:
                        pass
                metrics = {
                    "sharpe": sharpe,
                    "fitness": fitness,
                    "returns": returns,
                    "drawdown": drawdown,
                    "margin": margin,
                    "turnover": turnover
                }
                alphas.append({
                    "code": code,
                    "status": status,
                    "metrics": metrics
                })
    except Exception as e:
        print(f"Error reading CSV logs: {e}")
    return alphas

def get_recent_successful_alphas(alphas):
    successful_alphas = []
    for a in reversed(alphas):
        if a.get("status") == "SUCCESS":
            metrics = a.get("metrics", {})
            sharpe = metrics.get("sharpe", 0.0)
            fitness = metrics.get("fitness", 0.0)
            if sharpe > 1.0 and fitness > 1.0:
                code = a.get("code", "")
                if code and code not in successful_alphas:
                    successful_alphas.append(code)
                if len(successful_alphas) >= 15:
                    break
    return successful_alphas

# WorldQuant BRAIN API & Simulation Logic
def extract_metrics(data, session, headers):
    if "is" in data and isinstance(data["is"], dict):
        is_dict = data["is"]
        if "sharpe" in is_dict:
            return is_dict
    if "results" in data:
        results = data["results"]
        if isinstance(results, dict):
            if "sharpe" in results:
                return results
            if "is" in results and isinstance(results["is"], dict):
                return results["is"]
        elif isinstance(results, list) and len(results) > 0:
            if isinstance(results[0], dict):
                if "sharpe" in results[0]:
                    return results[0]
                if "is" in results[0] and isinstance(results[0]["is"], dict):
                    return results[0]["is"]
    if "alpha" in data and isinstance(data["alpha"], dict):
        alpha_dict = data["alpha"]
        if "is" in alpha_dict and isinstance(alpha_dict["is"], dict):
            return alpha_dict["is"]
    alpha_id = data.get("alpha")
    if alpha_id and isinstance(alpha_id, str):
        alpha_url = f"https://api.worldquantbrain.com/alphas/{alpha_id}"
        for attempt in range(3):
            try:
                resp = session.get(alpha_url, headers=headers)
                if resp.status_code == 200:
                    alpha_data = resp.json()
                    if "is" in alpha_data and isinstance(alpha_data["is"], dict):
                        return alpha_data["is"]
                elif resp.status_code == 429:
                    time.sleep(5)
            except Exception as e:
                time.sleep(2)
    return None

def simulate_alpha(expression, session, headers, settings, dry_run=False):
    universe = "TOP3000"
    decay = settings.get("decay", 2)
    if decay == -1:
        decay = random.choice([2, 3, 5])
    if dry_run:
        print(f"[DRY-RUN] Simulating code on universe={universe}, decay={decay}")
        time.sleep(1)
        mock_success = random.random() < 0.7
        if mock_success:
            metrics = {
                "sharpe": random.uniform(0.1, 2.2),
                "fitness": random.uniform(0.5, 2.2),
                "returns": random.uniform(-0.10, 0.35),
                "drawdown": random.uniform(-0.30, -0.01),
                "margin": random.uniform(0.00005, 0.00035),
                "turnover": random.uniform(0.05, 0.85)
            }
            return {
                "status": "SUCCESS",
                "metrics": metrics,
                "failed_checks": [],
                "universe": universe,
                "decay": decay,
                "alpha_id": "mock_alpha_id"
            }
        else:
            return {
                "status": "FAILED",
                "error": "Mock simulation failure",
                "universe": universe,
                "decay": decay
            }
            
    payload = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": settings.get("instrumentType", "EQUITY"),
            "region": settings.get("region", "USA"),
            "universe": universe,
            "delay": settings.get("delay", 1),
            "decay": decay,
            "neutralization": "INDUSTRY",
            "truncation": settings.get("truncation", 0.08),
            "pasteurization": "ON",
            "nanHandling": "ON",
            "language": settings.get("language", "FASTEXPR"),
            "unitHandling": settings.get("unitHandling", "VERIFY"),
            "visualization": False
        },
        "regular": expression
    }
    
    backoff = 60
    while True:
        try:
            print("Submitting simulation POST request...")
            response = session.post(
                "https://api.worldquantbrain.com/simulations",
                json=payload,
                headers=headers
            )
            if response.status_code == 429:
                print(f"Rate limited (429) on POST. Backing off for {backoff}s...")
                time.sleep(backoff)
                backoff = min(backoff * 2, 900)
                continue
            if response.status_code in [201, 202]:
                break
            else:
                print(f"Simulation startup failed with HTTP {response.status_code}: {response.text}")
                return {
                    "status": f"HTTP_{response.status_code}",
                    "error": response.text,
                    "universe": universe,
                    "decay": decay
                }
        except Exception as e:
            print(f"Connection error on simulation POST: {e}. Retrying in 10s...")
            time.sleep(10)
            
    status_url = response.headers.get("Location")
    if not status_url:
        return {
            "status": "NO_LOCATION_HEADER",
            "error": "Location header missing",
            "universe": universe,
            "decay": decay
        }
    if not status_url.startswith("http"):
        status_url = "https://api.worldquantbrain.com" + status_url
        
    print(f"Polling simulation status from: {status_url}")
    poll_count = 0
    none_status_count = 0
    current_phase = 1
    poll_interval = 2
    while poll_count < 300:
        if poll_count < 10:
            phase = 1
            new_interval = 2
        elif poll_count < 60:
            phase = 2
            new_interval = 10
        else:
            phase = 3
            new_interval = 30
        if phase != current_phase:
            print(f"[INFO] Escalating polling delay to {new_interval}s due to queue length")
            current_phase = phase
        poll_interval = new_interval
        try:
            poll_resp = session.get(status_url, headers=headers)
            if poll_resp.status_code == 429:
                time.sleep(60)
                continue
            try:
                data = poll_resp.json()
            except json.JSONDecodeError:
                time.sleep(3)
                poll_count += 1
                continue
            status = data.get("status")
            if status is None:
                none_status_count += 1
                if none_status_count > 25:
                    time.sleep(30)
                    none_status_count = 0
            else:
                none_status_count = 0
                print(f"Poll {poll_count + 1}/300 - Status: {status}")
            if status in ["COMPLETE", "COMPLETED"]:
                alpha_id = data.get("alpha")
                failed_checks = []
                metrics = None
                if alpha_id and isinstance(alpha_id, str):
                    alpha_url = f"https://api.worldquantbrain.com/alphas/{alpha_id}"
                    for attempt in range(3):
                        try:
                            resp = session.get(alpha_url, headers=headers)
                            if resp.status_code == 200:
                                alpha_data = resp.json()
                                metrics = alpha_data.get("is")
                                checks = alpha_data.get("is", {}).get("checks", [])
                                failed_checks = [c["name"] for c in checks if c.get("result") == "FAIL"]
                                break
                            elif resp.status_code == 429:
                                time.sleep(5)
                        except Exception as e:
                            time.sleep(2)
                if not metrics:
                    metrics = extract_metrics(data, session, headers)
                if metrics:
                    return {
                        "status": "SUCCESS",
                        "metrics": metrics,
                        "failed_checks": failed_checks,
                        "universe": universe,
                        "decay": decay,
                        "alpha_id": alpha_id
                    }
                else:
                    return {
                        "status": "METRICS_EXTRACTION_FAILED",
                        "error": "Could not find metrics in response",
                        "universe": universe,
                        "decay": decay
                    }
            elif status in ["FAILED", "ERROR"]:
                error_msg = data.get("message") or data.get("error") or "Unknown simulation error"
                failed_checks = []
                if "unit" in error_msg.lower() or "incompatible" in error_msg.lower():
                    failed_checks.append("INCOMPATIBLE_UNIT")
                if "self" in error_msg.lower() and "corr" in error_msg.lower():
                    failed_checks.append("SELF_CORRELATION")
                return {
                    "status": status,
                    "error": error_msg,
                    "failed_checks": failed_checks,
                    "universe": universe,
                    "decay": decay
                }
            time.sleep(poll_interval)
            poll_count += 1
        except Exception as e:
            time.sleep(3)
            poll_count += 1
            
    return {
        "status": "TIMEOUT",
        "error": "Exceeded maximum polling steps (300)",
        "universe": universe,
        "decay": decay
    }

def submit_alpha(alpha_id, session, headers, dry_run=False):
    """
    Submits an alpha to WorldQuant BRAIN submissions endpoint.
    POST https://api.worldquantbrain.com/submissions
    Payload: {"alpha": alpha_id}
    """
    if dry_run:
        print(f"[DRY-RUN] Submitting alpha {alpha_id} to WorldQuant BRAIN")
        return True

    payload = {"alpha": alpha_id}
    try:
        print(f"Submitting alpha {alpha_id} to WorldQuant BRAIN submissions endpoint...")
        response = session.post(
            "https://api.worldquantbrain.com/submissions",
            json=payload,
            headers=headers
        )
        if response.status_code in [200, 201, 202]:
            print(f"✅ Alpha {alpha_id} submitted successfully! Status code: {response.status_code}")
            return True
        else:
            print(f"❌ Failed to submit alpha {alpha_id}: HTTP {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception occurred during submission of alpha {alpha_id}: {e}")
        return False

def log_elite_alpha(code, metrics, universe, decay):
    elite_file = "elite_alphas.txt"
    try:
        s_val = float(metrics.get("sharpe", 0.0))
        f_val = float(metrics.get("fitness", 0.0))
        m_val = float(metrics.get("margin", 0.0))
        
        # Elite Hunting Mode threshold check: Sharpe > 1.0 AND Fitness > 1.0 AND Margin > 0.00015
        if not (s_val > 1.0 and f_val > 1.0 and m_val > 0.00015):
            return
            
        r_val = float(metrics.get("returns", 0.0))
        t_val = float(metrics.get("turnover", 0.0))
        
        returns_pct = f"{r_val * 100.0:.4f}%"
        margin_bps = f"{m_val * 10000.0:.4f}"
        turnover_pct = f"{t_val * 100.0:.4f}%"
        
        with open(elite_file, mode="a", encoding="utf-8") as f:
            f.write(f"Code: {code}\n")
            f.write(f"Sharpe: {s_val:.4f}, Fitness: {f_val:.4f}, Returns: {returns_pct}, Margin(bps): {margin_bps}, Turnover: {turnover_pct}, Universe: {universe}, Decay: {decay}\n")
            f.write("-" * 50 + "\n")
        print(f"🔥 Elite Alpha Saved to {elite_file}! Sharpe: {s_val:.4f}, Fitness: {f_val:.4f}, Margin: {margin_bps} bps")
    except Exception as e:
        print(f"Error logging elite alpha: {e}")

def log_attempt(status, metrics, failed_checks, universe, decay, code, settings=None):
    csv_file = "simulation_results.csv"
    file_exists = os.path.exists(csv_file)
    sharpe = ""
    fitness = ""
    returns_pct = ""
    drawdown_pct = ""
    margin_bps = ""
    turnover_pct = ""
    if metrics:
        s_val = metrics.get("sharpe")
        f_val = metrics.get("fitness")
        r_val = metrics.get("returns")
        d_val = metrics.get("drawdown")
        m_val = metrics.get("margin")
        t_val = metrics.get("turnover")
        sharpe = f"{float(s_val):.4f}" if s_val is not None else ""
        fitness = f"{float(f_val):.4f}" if f_val is not None else ""
        if r_val is not None:
            r_float = float(r_val)
            returns_pct = f"{r_float * 100.0:.4f}" if abs(r_float) <= 1.0 else f"{r_float:.4f}"
        if d_val is not None:
            d_float = float(d_val)
            drawdown_pct = f"{d_float * 100.0:.4f}" if abs(d_float) <= 1.0 else f"{d_float:.4f}"
        if m_val is not None:
            margin_bps = f"{float(m_val) * 10000.0:.4f}"
        if t_val is not None:
            t_float = float(t_val)
            turnover_pct = f"{t_float * 100.0:.4f}" if abs(t_float) <= 1.0 else f"{t_float:.4f}"
    try:
        with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "Status", "Sharpe", "Fitness", "Returns(%)", "Drawdown(%)",
                    "Margin(bps)", "Turnover(%)", "Universe", "Delay", "Decay", "Neutralization", "FailedChecks", "Code"
                ])
            checks_str = ";".join(failed_checks) if failed_checks else ""
            delay_val = settings.get("delay", 1) if settings else 1
            neutral_val = settings.get("neutralization", "INDUSTRY") if settings else "INDUSTRY"
            writer.writerow([
                status, sharpe, fitness, returns_pct, drawdown_pct,
                margin_bps, turnover_pct, universe, delay_val, decay, neutral_val, checks_str, code
            ])
        print(f"Logged to CSV: Status={status}, Sharpe={sharpe}, Fitness={fitness}, Turnover(%)={turnover_pct}, FailedChecks={checks_str}")
        
        # Elite checks logic: strictly log only when Sharpe > 1.0 AND Fitness > 1.0 AND Margin > 0.00015
        if status == "SUCCESS" and metrics:
            s_val = metrics.get("sharpe")
            f_val = metrics.get("fitness")
            m_val = metrics.get("margin")
            if s_val is not None and f_val is not None and m_val is not None:
                s_float = float(s_val)
                f_float = float(f_val)
                m_float = float(m_val)
                if s_float > 1.0 and f_float > 1.0 and m_float > 0.00015:
                    log_elite_alpha(code, metrics, universe, decay)
    except Exception as e:
        print(f"Failed to log to CSV: {e}")

# Main execution loop
def main():
    parser = argparse.ArgumentParser(description="WorldQuant BRAIN Advanced Alpha Generator (Elite TOP3000 Model)")
    parser.add_argument("--cookie", type=str, help="Override auth cookie string")
    parser.add_argument("--dry-run", action="store_true", help="Run offline dry-run mode with simulated metrics")
    parser.add_argument("--iterations", type=int, default=0, help="Limit number of loops to run (0 for infinite)")
    parser.add_argument("--universe", type=str, default="TOP3000", help="Universe")
    parser.add_argument("--delay", type=int, default=1, help="Simulation Delay")
    parser.add_argument("--decay", type=int, default=-1, help="Decay factor")
    parser.add_argument("--neutralization", type=str, default="INDUSTRY", help="Neutralization level")
    parser.add_argument("--truncation", type=float, default=0.08, help="Truncation limit")
    parser.add_argument("--pasteurization", type=str, choices=["ON", "OFF"], default="ON", help="Pasteurization status")
    parser.add_argument("--nan-handling", type=str, choices=["ON", "OFF"], default="ON", dest="nan_handling", help="NaN handling status")
    parser.add_argument("--unit-handling", type=str, choices=["VERIFY", "COMPLY"], default="VERIFY", dest="unit_handling", help="Unit handling status")
    parser.add_argument("--region", type=str, default="USA", help="Region")
    parser.add_argument("--instrument-type", type=str, default="EQUITY", dest="instrument_type", help="Instrument type")
    parser.add_argument("--engine", type=str, default="advanced", help="Engine type")
    args = parser.parse_args()
    
    print("=" * 60)
    print(" WORLDQUANT BRAIN ALPHA FACTORY - ELITE TOP3000 MODEL")
    print("=" * 60)
    
    session = requests.Session()
    cookie_str = args.cookie
    if not cookie_str or cookie_str == "PASTE_YOUR_COOKIE_HERE":
        cookie_str = COOKIE if COOKIE and COOKIE != "PASTE_YOUR_COOKIE_HERE" else ""
        
    headers = {
        "Cookie": cookie_str,
        "Content-Type": "application/json"
    }
    token = None
    for part in cookie_str.split(";"):
        part = part.strip()
        if part.startswith("t="):
            token = part[2:]
            break
    if token:
        headers["Authorization"] = f"Bearer {token}"
        print(f"Extracted JWT session token: {token[:30]}...")
        
    if not args.dry_run:
        print("Testing authentication with WorldQuant BRAIN API...")
        try:
            resp = session.get("https://api.worldquantbrain.com/users/self", headers=headers)
            if resp.status_code == 200:
                user_info = resp.json()
                username = user_info.get("email") or user_info.get("username") or "User"
                print(f"✅ Connection successful! Authenticated as: {username}")
            else:
                print(f"⚠️ Authentication warning: API returned status code {resp.status_code}.")
        except Exception as e:
            print(f"⚠️ Connection error during authentication test: {e}")
    else:
        print("⚠️ RUNNING IN OFFLINE DRY-RUN MODE (MOCK API SIMULATIONS)")
        
    migrate_csv_file()
    
    sim_settings = {
        "universe": "TOP3000",
        "delay": args.delay,
        "decay": args.decay,
        "neutralization": "INDUSTRY",
        "truncation": args.truncation,
        "pasteurization": "ON",
        "nanHandling": "ON",
        "unitHandling": args.unit_handling,
        "region": args.region,
        "instrumentType": args.instrument_type,
        "language": "FASTEXPR"
    }
    
    loop_count = 0
    while True:
        loop_count += 1
        if args.iterations > 0 and loop_count > args.iterations:
            print(f"Reached requested limit of {args.iterations} iterations. Exiting.")
            break
            
        print(f"\n--- Alpha Factory Cycle #{loop_count} ---")
        
        alphas = get_historical_alphas()
        # Filter winners that fit our DATA_POOL and meet minimum thresholds
        winners = [a for a in alphas if a["status"] == "SUCCESS" and a["metrics"]["sharpe"] > 1.0 and a["metrics"]["fitness"] > 1.0]
        winners = [w for w in winners if any(fd in w["code"] for fd in DATA_POOL)]
        
        print(f"Parsed {len(alphas)} historical alphas, found {len(winners)} eligible winners.")
        
        history_buffer = get_recent_successful_alphas(alphas)
        print(f"📋 HISTORY_BUFFER (last 15 successful expressions): {history_buffer}")
        
        is_mutation = False
        parent_code = None
        
        if winners and random.random() < 0.30:
            parent_alpha = random.choice(winners)
            parent_code = parent_alpha["code"]
            is_mutation = True
            
        attempts = 0
        code = None
        while attempts < 15:
            if is_mutation:
                candidate = mutate_alpha(parent_code)
            else:
                candidate = generate_alpha()
                
            if candidate not in history_buffer:
                code = candidate
                break
            attempts += 1
            
        if not code:
            code = generate_alpha()
            
        if is_mutation:
            print(f"🧬 [MUTATION] Mutating parent:\nCode: {parent_code}\nChild: {code}")
        else:
            print(f"✨ [GENERATION] New random alpha expression:\nCode: {code}")
            
        # Simulate
        result = simulate_alpha(code, session, headers, sim_settings, dry_run=args.dry_run)
        
        status = result["status"]
        metrics = result.get("metrics")
        failed_checks = result.get("failed_checks", [])
        universe = result.get("universe")
        decay = result.get("decay")
        alpha_id = result.get("alpha_id")
        
        # Discard logic: Sharpe < 0.5 is not submitted but is still logged to the CSV file.
        is_submittable = True
        if status == "SUCCESS":
            sharpe_val = float(metrics.get("sharpe", 0.0)) if metrics else 0.0
            if sharpe_val < 0.5:
                print(f"⚠️ DISCARDED FROM SUBMISSION: Sharpe is {sharpe_val:.4f} (< 0.5 threshold). Skipping submission but keeping CSV log.")
                is_submittable = False
                
        # Simple cross-correlation checks
        is_correlated = False
        sim_score = 0.0
        correlated_code = None
        for past_code in history_buffer:
            past_tokens = set(re.findall(r'\b[a-zA-Z0-9_]+\b', past_code))
            cand_tokens = set(re.findall(r'\b[a-zA-Z0-9_]+\b', code))
            if past_tokens and cand_tokens:
                overlap = len(past_tokens.intersection(cand_tokens)) / max(len(past_tokens), len(cand_tokens))
                if overlap > 0.85:
                    is_correlated = True
                    sim_score = overlap
                    correlated_code = past_code
                    break
                    
        if status == "SUCCESS" and is_correlated:
            print(f"⚠️ REJECTED: Candidate shares {sim_score:.2%} components with existing alpha in history: {correlated_code}")
            status = "FAILED"
            if "SELF_CORRELATION" not in failed_checks:
                failed_checks.append("SELF_CORRELATION")
                
        # Submission logic: If status is SUCCESS and Sharpe is >= 0.5, submit alpha.
        if status == "SUCCESS" and is_submittable:
            if alpha_id:
                submit_alpha(alpha_id, session, headers, dry_run=args.dry_run)
            else:
                print("⚠️ Warning: Cannot submit alpha because alpha_id is missing.")
                
        log_attempt(status, metrics, failed_checks, universe, decay, code, settings=sim_settings)

if __name__ == "__main__":
    main()