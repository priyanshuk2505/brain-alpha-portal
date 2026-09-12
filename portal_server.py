#!/usr/bin/env python3
"""
WorldQuant BRAIN Full-Stack Batch Alpha Portal Server
Flask REST API & Background Job Worker Engine with SHA256 Deduplication Cache,
Rate Limit Backoff, PnL Recordset Fetching, and Real-Time Batch Progress Monitoring.
"""

import os
import re
import csv
import sys
import json
import time
import hashlib
import random
import threading
from queue import Queue
from datetime import datetime, timezone
import requests
from flask import Flask, jsonify, request, render_template, send_from_directory, Response

# Setup App
app = Flask(__name__, template_folder="templates", static_folder="static")

# Directories & Files
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(WORKSPACE_DIR, "simulation_cache.json")
RESULTS_CSV = os.path.join(WORKSPACE_DIR, "simulation_results.csv")
ELITE_FILE = os.path.join(WORKSPACE_DIR, "elite_alphas.txt")

# Default User Cookie from alpha_factory
DEFAULT_COOKIE = "_fbp=fb.1.1778595947954.838983336151760867; _ga=GA1.1.687920460.1778595944; _ga_9RN6WVT1K1=GS2.1.s1781261144$o102$g1$t1781261272$j59$l0$h0; _rdt_uuid=1778595944372.55b2243d-1bc9-440f-a27d-c17c7e25a64c; t=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJnazFBcmtJOTJuN3RDUFQ2Vk9NU0FwMDgwTkxGYXNERiIsImV4cCI6MTc4MTI3NTY1MiwiYW1yIjpbInB3ZCIsImZhY2UiLCJjYXB0Y2hhIl19.BnWNMKcA2HPmJvAizMg9APzXLFHJAMfbkhiwDtmevGg; _gcl_au=1.1.326319197.1778595941.1284668449.1781175694.1781175694; _ga_FXKNEPLB1N=GS2.1.s1779733566$o7$g0$t1779733566$j60$l0$h0; __zlcmid=1XcoWMCkz0Gybrj; cookieyes-consent=consentid:V3N1Q1lGeXMxZWJjQU5ienR2TEtiUnlGMTdIN3k3cFA,consent:yes,action:yes,necessary:yes,functional:yes,analytics:yes,performance:yes,advertisement:yes,other:yes"

# Global Auth State
auth_state = {
    "cookie": DEFAULT_COOKIE,
    "user_email": "priyanshubhadani25@gmail.com",
    "authenticated": True,
    "last_checked": None
}

# In-Memory Cache and Batch Jobs Storage
cache_lock = threading.Lock()
jobs_lock = threading.Lock()

batch_jobs = {}  # batch_id -> dict
job_queue = Queue()

# -----------------------------------------------------------------------------
# SHA256 Simulation Cache Engine
# -----------------------------------------------------------------------------
def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache_data):
    with cache_lock:
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")

def get_alpha_hash(expression, settings):
    config = {"expression": expression.strip(), "settings": settings}
    config_str = json.dumps(config, sort_keys=True)
    return hashlib.sha256(config_str.encode("utf-8")).hexdigest()

# -----------------------------------------------------------------------------
# BRAIN Session & Auth Helpers
# -----------------------------------------------------------------------------
def get_brain_session():
    session = requests.Session()
    cookie_str = auth_state["cookie"].strip()
    
    # Auto-format raw JWT token if pasted without 't=' prefix
    if (cookie_str.startswith("eyJ") or cookie_str.startswith("teyJ")) and ";" not in cookie_str:
        if cookie_str.startswith("teyJ"):
            cookie_str = cookie_str[1:] # strip accidental leading t
        cookie_str = f"t={cookie_str}"
        auth_state["cookie"] = cookie_str

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
            
    if not token and (cookie_str.startswith("eyJ") or cookie_str.startswith("t=")):
        token = cookie_str[2:] if cookie_str.startswith("t=") else cookie_str

    if token:
        headers["Authorization"] = f"Bearer {token}"
    return session, headers

def authenticate_brain_user(email, password):
    try:
        session = requests.Session()
        resp = session.post("https://api.worldquantbrain.com/authentication", auth=(email, password), timeout=10)
        if resp.status_code in [200, 201]:
            cookie_parts = []
            for k, v in resp.cookies.items():
                cookie_parts.append(f"{k}={v}")
            
            if cookie_parts:
                auth_state["cookie"] = "; ".join(cookie_parts)
            elif resp.headers.get("Set-Cookie"):
                auth_state["cookie"] = resp.headers.get("Set-Cookie")
                
            auth_state["user_email"] = email
            auth_state["authenticated"] = True
            auth_state["last_checked"] = datetime.now(timezone.utc).isoformat()
            return True, "Authenticated successfully with WorldQuant BRAIN"
        else:
            auth_state["authenticated"] = False
            return False, f"HTTP {resp.status_code}: {resp.text}"
    except Exception as e:
        auth_state["authenticated"] = False
        return False, str(e)

def check_auth_status():
    session, headers = get_brain_session()
    try:
        resp = session.get("https://api.worldquantbrain.com/users/self", headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            auth_state["authenticated"] = True
            auth_state["user_email"] = data.get("email") or data.get("username") or auth_state["user_email"]
            auth_state["last_checked"] = datetime.now(timezone.utc).isoformat()
            return True, auth_state["user_email"]
        else:
            auth_state["authenticated"] = False
            return False, f"HTTP {resp.status_code}"
    except Exception as e:
        auth_state["authenticated"] = False
        return False, str(e)

# -----------------------------------------------------------------------------
# Core Simulation & API Functionality
# -----------------------------------------------------------------------------
def extract_metrics(data, session, headers):
    if "is" in data and isinstance(data["is"], dict):
        if "sharpe" in data["is"]:
            return data["is"]
    if "results" in data:
        res = data["results"]
        if isinstance(res, dict):
            if "sharpe" in res:
                return res
            if "is" in res and isinstance(res["is"], dict):
                return res["is"]
        elif isinstance(res, list) and len(res) > 0 and isinstance(res[0], dict):
            if "sharpe" in res[0]:
                return res[0]
            if "is" in res[0] and isinstance(res[0]["is"], dict):
                return res[0]["is"]
    alpha_id = data.get("alpha")
    if alpha_id and isinstance(alpha_id, str):
        alpha_url = f"https://api.worldquantbrain.com/alphas/{alpha_id}"
        for _ in range(3):
            try:
                resp = session.get(alpha_url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    a_data = resp.json()
                    if "is" in a_data and isinstance(a_data["is"], dict):
                        return a_data["is"]
                elif resp.status_code == 429:
                    time.sleep(3)
            except Exception:
                time.sleep(1)
    return None

def run_single_simulation(expression, settings, dry_run=False):
    alpha_hash = get_alpha_hash(expression, settings)
    cache = load_cache()
    
    # 1. Deduplication Cache Lookup
    if alpha_hash in cache:
        cached_entry = cache[alpha_hash]
        return {
            "status": "CACHED_DUPLICATE",
            "alpha_id": cached_entry.get("alpha_id"),
            "metrics": cached_entry.get("metrics"),
            "failed_checks": cached_entry.get("failed_checks", []),
            "cached": True,
            "hash": alpha_hash
        }
        
    session, headers = get_brain_session()
    universe = settings.get("universe", "TOP3000")
    decay = settings.get("decay", 2)
    
    # 2. Dry Run Simulation (Mocking)
    if dry_run:
        time.sleep(random.uniform(0.5, 1.2))
        mock_success = random.random() < 0.8
        if mock_success:
            metrics = {
                "sharpe": round(random.uniform(0.2, 2.4), 4),
                "fitness": round(random.uniform(0.4, 2.2), 4),
                "returns": round(random.uniform(-0.05, 0.35), 4),
                "drawdown": round(random.uniform(-0.25, -0.01), 4),
                "margin": round(random.uniform(0.00005, 0.00035), 6),
                "turnover": round(random.uniform(0.05, 0.85), 4)
            }
            alpha_id = f"MOCK_{alpha_hash[:8].upper()}"
            result = {
                "status": "SUCCESS",
                "alpha_id": alpha_id,
                "metrics": metrics,
                "failed_checks": [],
                "universe": universe,
                "decay": decay,
                "cached": False,
                "hash": alpha_hash
            }
            cache[alpha_hash] = result
            save_cache(cache)
            return result
        else:
            return {
                "status": "FAILED",
                "error": "Mock API simulation check failed",
                "universe": universe,
                "decay": decay,
                "cached": False,
                "hash": alpha_hash
            }
            
    # 3. Live BRAIN Remote Simulation API
    payload = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": settings.get("instrumentType", "EQUITY"),
            "region": settings.get("region", "USA"),
            "universe": universe,
            "delay": settings.get("delay", 1),
            "decay": decay,
            "neutralization": settings.get("neutralization", "INDUSTRY"),
            "truncation": settings.get("truncation", 0.08),
            "pasteurization": settings.get("pasteurization", "ON"),
            "nanHandling": settings.get("nanHandling", "ON"),
            "language": settings.get("language", "FASTEXPR"),
            "unitHandling": settings.get("unitHandling", "VERIFY"),
            "visualization": False
        },
        "regular": expression
    }
    
    backoff = 30
    resp = None
    for _ in range(5):
        try:
            resp = session.post("https://api.worldquantbrain.com/simulations", json=payload, headers=headers, timeout=15)
            if resp.status_code == 429:
                retry_sec = int(resp.headers.get("Retry-After", backoff))
                time.sleep(retry_sec)
                backoff = min(backoff * 2, 300)
                continue
            if resp.status_code in [201, 202]:
                break
            else:
                return {"status": f"HTTP_{resp.status_code}", "error": resp.text, "hash": alpha_hash}
        except Exception as e:
            time.sleep(5)
            
    if not resp or resp.status_code not in [201, 202]:
        return {"status": "REQUEST_FAILED", "error": "Could not connect to BRAIN API", "hash": alpha_hash}

    status_url = resp.headers.get("Location")
    if not status_url:
        return {"status": "NO_LOCATION_HEADER", "error": "Location header missing", "hash": alpha_hash}
    if not status_url.startswith("http"):
        status_url = "https://api.worldquantbrain.com" + status_url
        
    poll_count = 0
    while poll_count < 250:
        try:
            poll_resp = session.get(status_url, headers=headers, timeout=10)
            if poll_resp.status_code == 429:
                time.sleep(10)
                continue
            data = poll_resp.json()
            status = data.get("status")
            if status in ["COMPLETE", "COMPLETED"]:
                alpha_id = data.get("alpha")
                failed_checks = []
                metrics = None
                if alpha_id and isinstance(alpha_id, str):
                    a_resp = session.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}", headers=headers, timeout=10)
                    if a_resp.status_code == 200:
                        a_data = a_resp.json()
                        metrics = a_data.get("is")
                        checks = a_data.get("is", {}).get("checks", [])
                        failed_checks = [c["name"] for c in checks if c.get("result") == "FAIL"]
                if not metrics:
                    metrics = extract_metrics(data, session, headers)
                if metrics:
                    res = {
                        "status": "SUCCESS",
                        "alpha_id": alpha_id,
                        "metrics": metrics,
                        "failed_checks": failed_checks,
                        "universe": universe,
                        "decay": decay,
                        "cached": False,
                        "hash": alpha_hash
                    }
                    cache[alpha_hash] = res
                    save_cache(cache)
                    return res
                else:
                    return {"status": "METRICS_EXTRACTION_FAILED", "error": "Metrics unavailable", "hash": alpha_hash}
            elif status in ["FAILED", "ERROR"]:
                err = data.get("message") or data.get("error") or "Simulation error"
                return {"status": status, "error": err, "failed_checks": [], "hash": alpha_hash}
            
            retry_wait = int(poll_resp.headers.get("Retry-After", 3))
            time.sleep(max(retry_wait, 2))
            poll_count += 1
        except Exception as e:
            time.sleep(3)
            poll_count += 1
            
    return {"status": "TIMEOUT", "error": "Exceeded maximum polling limit", "hash": alpha_hash}

def submit_alpha_to_brain(alpha_id, dry_run=False):
    if dry_run or alpha_id.startswith("MOCK_"):
        return True, "Mock Alpha Submitted Successfully"
    session, headers = get_brain_session()
    try:
        resp = session.post("https://api.worldquantbrain.com/submissions", json={"alpha": alpha_id}, headers=headers, timeout=10)
        if resp.status_code in [200, 201, 202]:
            return True, f"Submitted successfully (HTTP {resp.status_code})"
        else:
            return False, f"HTTP {resp.status_code}: {resp.text}"
    except Exception as e:
        return False, str(e)

# -----------------------------------------------------------------------------
# Results Logger Helper
# -----------------------------------------------------------------------------
def log_result_to_csv(result, expression, settings):
    try:
        file_exists = os.path.exists(RESULTS_CSV)
        status = result.get("status", "UNKNOWN")
        metrics = result.get("metrics") or {}
        failed_checks = result.get("failed_checks", [])
        
        sharpe = f"{metrics.get('sharpe', ''):.4f}" if metrics.get('sharpe') is not None else ""
        fitness = f"{metrics.get('fitness', ''):.4f}" if metrics.get('fitness') is not None else ""
        returns = f"{metrics.get('returns', '') * 100:.4f}" if metrics.get('returns') is not None else ""
        drawdown = f"{metrics.get('drawdown', '') * 100:.4f}" if metrics.get('drawdown') is not None else ""
        margin = f"{metrics.get('margin', '') * 10000:.4f}" if metrics.get('margin') is not None else ""
        turnover = f"{metrics.get('turnover', '') * 100:.4f}" if metrics.get('turnover') is not None else ""
        
        checks_str = ";".join(failed_checks)
        universe = settings.get("universe", "TOP3000")
        delay = settings.get("delay", 1)
        decay = settings.get("decay", 2)
        neutralization = settings.get("neutralization", "INDUSTRY")
        region = settings.get("region", "USA")
        truncation = settings.get("truncation", 0.08)
        pasteurization = settings.get("pasteurization", "ON")
        nan_handling = settings.get("nanHandling", "ON")
        unit_handling = settings.get("unitHandling", "VERIFY")
        language = settings.get("language", "FASTEXPR")
        
        with open(RESULTS_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "Status", "Sharpe", "Fitness", "Returns(%)", "Drawdown(%)",
                    "Margin(bps)", "Turnover(%)", "Universe", "Delay", "Decay",
                    "Neutralization", "Region", "Truncation", "Pasteurization",
                    "NanHandling", "UnitHandling", "Language", "FailedChecks", "Code"
                ])
            writer.writerow([
                status, sharpe, fitness, returns, drawdown, margin, turnover,
                universe, delay, decay, neutralization, region, truncation,
                pasteurization, nan_handling, unit_handling, language, checks_str, expression
            ])
            
        # Check for Elite logging condition
        if status in ["SUCCESS", "CACHED_DUPLICATE"] and metrics:
            s_val = float(metrics.get("sharpe", 0))
            f_val = float(metrics.get("fitness", 0))
            m_val = float(metrics.get("margin", 0))
            if s_val >= 1.0 and f_val >= 1.0 and m_val >= 0.0001:
                with open(ELITE_FILE, "a", encoding="utf-8") as f_elite:
                    f_elite.write(f"Code: {expression}\n")
                    f_elite.write(f"Sharpe: {s_val:.4f}, Fitness: {f_val:.4f}, Returns: {returns}%, Margin(bps): {margin}, Turnover: {turnover}%, Universe: {universe}, Delay: {delay}, Neutralization: {neutralization}\n")
                    f_elite.write("-" * 60 + "\n")
    except Exception as e:
        print(f"Error logging to CSV: {e}")


# -----------------------------------------------------------------------------
# Background Queue Worker Thread
# -----------------------------------------------------------------------------
def background_worker():
    while True:
        job_item = job_queue.get()
        if job_item is None:
            break
            
        batch_id, item_index, item = job_item
        expression = item["expression"]
        settings = item["settings"]
        dry_run = item["dry_run"]
        auto_submit = item.get("auto_submit", False)
        
        with jobs_lock:
            if batch_id in batch_jobs:
                batch_jobs[batch_id]["items"][item_index]["status"] = "SIMULATING"
                batch_jobs[batch_id]["items"][item_index]["start_time"] = datetime.now(timezone.utc).isoformat()
                
        res = run_single_simulation(expression, settings, dry_run=dry_run)
        
        # Auto-submit check if Sharpe >= 0.5
        metrics = res.get("metrics") or {}
        sharpe = float(metrics.get("sharpe", 0.0))
        if auto_submit and res.get("status") in ["SUCCESS", "CACHED_DUPLICATE"] and sharpe >= 0.5:
            alpha_id = res.get("alpha_id")
            if alpha_id:
                sub_ok, sub_msg = submit_alpha_to_brain(alpha_id, dry_run=dry_run)
                res["submitted"] = sub_ok
                res["submit_msg"] = sub_msg
                
        # Log to CSV
        log_result_to_csv(res, expression, settings)
        
        with jobs_lock:
            if batch_id in batch_jobs:
                batch_jobs[batch_id]["items"][item_index]["status"] = res.get("status")
                batch_jobs[batch_id]["items"][item_index]["result"] = res
                batch_jobs[batch_id]["completed"] += 1
                total = batch_jobs[batch_id]["total"]
                completed = batch_jobs[batch_id]["completed"]
                batch_jobs[batch_id]["progress"] = round((completed / total) * 100, 1)
                if completed == total:
                    batch_jobs[batch_id]["status"] = "COMPLETED"
                    batch_jobs[batch_id]["end_time"] = datetime.now(timezone.utc).isoformat()
                    
        job_queue.task_done()

worker_thread = threading.Thread(target=background_worker, daemon=True)
worker_thread.start()

# -----------------------------------------------------------------------------
# REST API Endpoints
# -----------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/auth/status", methods=["GET"])
def get_auth_status():
    ok, details = check_auth_status()
    return jsonify({
        "authenticated": ok,
        "user_email": auth_state["user_email"],
        "details": details,
        "last_checked": auth_state["last_checked"]
    })

@app.route("/api/auth/update", methods=["POST"])
def update_auth():
    data = request.get_json() or {}
    new_cookie = data.get("cookie")
    if new_cookie:
        auth_state["cookie"] = new_cookie.strip()
        ok, details = check_auth_status()
        return jsonify({"success": ok, "details": details, "user_email": auth_state["user_email"]})
    return jsonify({"success": False, "error": "No cookie string provided"}), 400

@app.route("/api/auth/login", methods=["POST"])
def login_auth():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400
    ok, details = authenticate_brain_user(email, password)
    return jsonify({"success": ok, "message": details, "user_email": auth_state["user_email"]})

@app.route("/api/simulations/batch", methods=["POST"])
def enqueue_batch():
    data = request.get_json() or {}
    raw_expressions = data.get("expressions", [])
    settings = data.get("settings", {})
    dry_run = data.get("dry_run", False) or settings.get("dry_run", False)
    auto_submit = data.get("auto_submit", False) or settings.get("auto_submit", False)
    
    if isinstance(raw_expressions, str):
        # Line-separated expressions
        expressions = [line.strip() for line in raw_expressions.splitlines() if line.strip() and not line.strip().startswith("#")]
    else:
        expressions = [str(e).strip() for e in raw_expressions if str(e).strip()]
        
    if not expressions:
        return jsonify({"error": "No valid expressions provided"}), 400
        
    batch_id = f"BATCH_{int(time.time())}_{random.randint(1000, 9999)}"
    batch_item_records = []
    
    for idx, expr in enumerate(expressions):
        item_obj = {
            "id": f"{batch_id}_{idx}",
            "expression": expr,
            "settings": settings,
            "status": "QUEUED",
            "dry_run": dry_run,
            "auto_submit": auto_submit,
            "result": None
        }
        batch_item_records.append(item_obj)
        job_queue.put((batch_id, idx, item_obj))
        
    batch_job_record = {
        "batch_id": batch_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total": len(expressions),
        "completed": 0,
        "progress": 0.0,
        "status": "RUNNING",
        "settings": settings,
        "dry_run": dry_run,
        "auto_submit": auto_submit,
        "items": batch_item_records
    }
    
    with jobs_lock:
        batch_jobs[batch_id] = batch_job_record
        
    return jsonify({
        "success": True,
        "batch_id": batch_id,
        "total_enqueued": len(expressions),
        "status": "RUNNING"
    })

@app.route("/api/simulations/cancel", methods=["POST"])
def cancel_batch():
    with jobs_lock:
        # Clear queued items
        cancelled_count = 0
        while not job_queue.empty():
            try:
                job_queue.get_nowait()
                job_queue.task_done()
                cancelled_count += 1
            except Exception:
                break
                
        # Mark all running/pending batches as CANCELLED
        for b_id, b_data in batch_jobs.items():
            if b_data.get("status") in ["RUNNING", "PENDING"]:
                b_data["status"] = "CANCELLED"
                b_data["end_time"] = datetime.now(timezone.utc).isoformat()
                
    return jsonify({"success": True, "message": "Stopped active simulations and cancelled queue", "cancelled_items": cancelled_count})

@app.route("/api/simulations/batches", methods=["GET"])
def get_batches():
    with jobs_lock:
        summary_list = []
        for b_id, b_data in batch_jobs.items():
            summary_list.append({
                "batch_id": b_id,
                "created_at": b_data["created_at"],
                "total": b_data["total"],
                "completed": b_data["completed"],
                "progress": b_data["progress"],
                "status": b_data["status"],
                "dry_run": b_data["dry_run"],
                "settings": b_data["settings"]
            })
        return jsonify(summary_list)

@app.route("/api/simulations/batch/<batch_id>", methods=["GET"])
def get_batch_details(batch_id):
    with jobs_lock:
        if batch_id in batch_jobs:
            return jsonify(batch_jobs[batch_id])
        return jsonify({"error": "Batch ID not found"}), 404

@app.route("/api/results", methods=["GET"])
def get_results():
    alphas = []
    if not os.path.exists(RESULTS_CSV):
        return jsonify(alphas)
    try:
        with open(RESULTS_CSV, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = None
            for row in reader:
                if not row:
                    continue
                if not header:
                    header = row
                    continue
                if len(row) < 12:
                    continue
                status = row[0].strip()
                def to_float(val):
                    try:
                        return float(val) if val != "" else None
                    except ValueError:
                        return None
                sharpe = to_float(row[1])
                fitness = to_float(row[2])
                returns = to_float(row[3])
                drawdown = to_float(row[4])
                margin = to_float(row[5])
                turnover = to_float(row[6])
                universe = row[7].strip()
                delay = row[8].strip()
                decay = row[9].strip()
                neutralization = row[10].strip()
                checks_str = row[11].strip()
                code = row[-1].strip() if len(row) > 1 else ""
                
                failed_checks = checks_str.split(";") if checks_str else []
                alphas.append({
                    "status": status,
                    "sharpe": sharpe,
                    "fitness": fitness,
                    "returns": returns,
                    "drawdown": drawdown,
                    "margin": margin,
                    "turnover": turnover,
                    "universe": universe,
                    "delay": delay,
                    "decay": decay,
                    "neutralization": neutralization,
                    "failed_checks": failed_checks,
                    "code": code
                })
    except Exception as e:
        return jsonify({"error": f"Failed reading results CSV: {e}"}), 500
    return jsonify(alphas)

@app.route("/api/alpha/<alpha_id>/pnl", methods=["GET"])
def get_alpha_pnl(alpha_id):
    if alpha_id.startswith("MOCK_") or request.args.get("mock") == "true":
        # Generate mock PnL curve for Chart.js
        dates = [f"2025-01-{(i%30)+1:02d}" for i in range(100)]
        cumulative = 0
        records = []
        for d in dates:
            cumulative += random.uniform(-500, 1500)
            records.append([d, round(cumulative, 2)])
        return jsonify({"status": "SUCCESS", "alpha_id": alpha_id, "pnl": records})
        
    session, headers = get_brain_session()
    url = f"https://api.worldquantbrain.com/alphas/{alpha_id}/recordsets/pnl"
    try:
        resp = session.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return jsonify(resp.json())
        return jsonify({"error": f"BRAIN API HTTP {resp.status_code}", "text": resp.text}), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    if os.path.exists(RESULTS_CSV):
        return send_from_directory(WORKSPACE_DIR, "simulation_results.csv", as_attachment=True)
    return jsonify({"error": "No simulation results file found"}), 404

@app.route("/api/export/elite", methods=["GET"])
def export_elite():
    if os.path.exists(ELITE_FILE):
        return send_from_directory(WORKSPACE_DIR, "elite_alphas.txt", as_attachment=True)
    return jsonify({"error": "No elite alphas logged yet"}), 404

if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1 and "--port" in sys.argv:
        try:
            port_idx = sys.argv.index("--port") + 1
            if port_idx < len(sys.argv):
                port = int(sys.argv[port_idx])
        except Exception:
            pass
    elif "PORT" in os.environ:
        try:
            port = int(os.environ["PORT"])
        except Exception:
            pass
    print(f"Starting WorldQuant BRAIN Batch Alpha Portal Server on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)


