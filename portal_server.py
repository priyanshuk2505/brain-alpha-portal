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
from flask import Flask, jsonify, request, render_template, send_from_directory, Response, send_file

# Setup App
app = Flask(__name__, template_folder="templates", static_folder="static")

# Directories & Files
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(WORKSPACE_DIR, "simulation_cache.json")
RESULTS_CSV = os.path.join(WORKSPACE_DIR, "simulation_results.csv")
ELITE_FILE = os.path.join(WORKSPACE_DIR, "elite_alphas.txt")
AUTH_FILE = os.path.join(WORKSPACE_DIR, "auth_credentials.json")
BATCH_JOBS_FILE = os.path.join(WORKSPACE_DIR, "batch_jobs.json")

# Default JWT — updated 2026-09-12. Replace when expired.
DEFAULT_COOKIE = "t=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1ekRNdU1WTnQ2WmZlZUZjOXRKMjNTVTFycnZsUTFhWSIsImV4cCI6MTc4OTIyNzQxOCwiYW1yIjpbInB3ZCIsImZhY2UiLCJjYXB0Y2hhIl19.E4zgwOfiLMshfDgDVvU_hraYo8yhjJ7CaTYI_qTkWzc"

# Global Auth State
auth_state = {
    "cookie": DEFAULT_COOKIE,
    "user_email": "priyanshubhadani25@gmail.com",
    "authenticated": False,
    "last_checked": None,
    "pending_persona_url": None,   # URL to POST to after face scan
    "pending_email": None,         # email pending persona verification
    "pending_password": None       # password pending persona verification
}


def load_auth_credentials():
    # 1. Check ~/.brain_credentials (official WorldQuant format: ["email", "password"])
    brain_cred_path = os.path.expanduser("~/.brain_credentials")
    if os.path.exists(brain_cred_path):
        try:
            with open(brain_cred_path, "r", encoding="utf-8") as f:
                creds = json.load(f)
                if isinstance(creds, list) and len(creds) >= 2:
                    auth_state["saved_email"] = creds[0]
                    auth_state["saved_password"] = creds[1]
                    if not auth_state.get("user_email"):
                        auth_state["user_email"] = creds[0]
        except Exception as e:
            print(f"Error loading ~/.brain_credentials: {e}")

    # 2. Check auth_credentials.json — apply saved cookie immediately to the session
    if os.path.exists(AUTH_FILE):
        try:
            with open(AUTH_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("cookie"):
                    auth_state["cookie"] = data["cookie"]
                    # *** CRITICAL FIX: actually apply the cookie to the requests.Session ***
                    _apply_session_cookie(data["cookie"])
                    print(f"[AUTH] Loaded saved cookie from {AUTH_FILE} and applied to session.")
                if data.get("user_email"):
                    auth_state["user_email"] = data["user_email"]
                if data.get("authenticated_at"):
                    auth_state["authenticated_at"] = data["authenticated_at"]
                else:
                    auth_state["authenticated_at"] = time.time()
        except Exception as e:
            print(f"Error loading auth credentials: {e}")

def save_auth_credentials(email=None, password=None):
    try:
        if not auth_state.get("authenticated_at"):
            auth_state["authenticated_at"] = time.time()
        with open(AUTH_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "cookie": auth_state["cookie"],
                "user_email": auth_state["user_email"],
                "authenticated_at": auth_state["authenticated_at"]
            }, f, indent=2)
    except Exception as e:
        print(f"Error saving auth credentials: {e}")

    if email and password:
        try:
            brain_cred_path = os.path.expanduser("~/.brain_credentials")
            with open(brain_cred_path, "w", encoding="utf-8") as f:
                json.dump([email, password], f, indent=2)
            auth_state["saved_email"] = email
            auth_state["saved_password"] = password
        except Exception as e:
            print(f"Error saving ~/.brain_credentials: {e}")

def format_brain_api_error(err_text: str) -> str:
    """Format BRAIN API JSON error body into a concise, human-readable error message."""
    if not err_text:
        return "Unknown API Error"
    try:
        data = json.loads(err_text)
        if isinstance(data, dict):
            if "settings" in data and isinstance(data["settings"], dict):
                parts = []
                for k, v in data["settings"].items():
                    if isinstance(v, list):
                        v_str = ", ".join(str(item) for item in v)
                    else:
                        v_str = str(v)
                    parts.append(f"Setting '{k}': {v_str}")
                if parts:
                    return "; ".join(parts)
            if "detail" in data:
                return str(data["detail"])
            if "message" in data:
                return str(data["message"])
            if "error" in data:
                return str(data["error"])
    except Exception:
        pass
    return err_text[:400]


# NOTE: _apply_session_cookie is defined later, so we defer calling load_auth_credentials
# until after all functions are defined. See end of startup block.


# In-Memory Cache and Batch Jobs Storage
cache_lock = threading.RLock()
jobs_lock = threading.RLock()
auth_pause_event = threading.Event()
auth_pause_event.set()  # Starts unpaused when authenticated

batch_jobs = {}  # batch_id -> dict
job_queue = Queue()

def load_batch_jobs():
    if os.path.exists(BATCH_JOBS_FILE):
        try:
            with open(BATCH_JOBS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[BATCH] Error loading batch jobs file: {e}")
    return {}

def save_batch_jobs(data=None):
    with jobs_lock:
        try:
            target = data if data is not None else batch_jobs
            with open(BATCH_JOBS_FILE, "w", encoding="utf-8") as f:
                json.dump(target, f, indent=2)
        except Exception as e:
            print(f"[BATCH] Error saving batch jobs file: {e}")

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
# Persistent session — holds JWT cookie across all simulation requests
_brain_session = requests.Session()
_brain_session.headers.update({"Content-Type": "application/json"})

# Rate limit state
rate_limit_state = {
    "limit": None,
    "remaining": None,
    "reset_seconds": None,
    "last_updated": None
}

def _update_rate_limits(headers):
    """Parse X-Ratelimit-* headers and store them."""
    try:
        if "x-ratelimit-limit" in headers:
            rate_limit_state["limit"] = int(headers["x-ratelimit-limit"])
        if "x-ratelimit-remaining" in headers:
            rate_limit_state["remaining"] = int(headers["x-ratelimit-remaining"])
        if "x-ratelimit-reset" in headers:
            rate_limit_state["reset_seconds"] = int(headers["x-ratelimit-reset"])
        rate_limit_state["last_updated"] = datetime.now(timezone.utc).isoformat()
    except Exception:
        pass

def _apply_session_cookie(cookie_str):
    """Set the JWT cookie on the persistent session."""
    _brain_session.cookies.clear()
    # Parse cookie string and set individual cookies
    for part in cookie_str.split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            _brain_session.cookies.set(k.strip(), v.strip())

def get_brain_session():
    """Return the persistent session. Cookie is already set on it."""
    cookie_str = auth_state["cookie"].strip()
    
    # Auto-format raw JWT token if pasted without 't=' prefix
    if (cookie_str.startswith("eyJ") or cookie_str.startswith("teyJ")) and ";" not in cookie_str:
        if cookie_str.startswith("teyJ"):
            cookie_str = cookie_str[1:]
        cookie_str = f"t={cookie_str}"
        auth_state["cookie"] = cookie_str
    
    _apply_session_cookie(cookie_str)
    return _brain_session

def authenticate_brain_user(email, password):
    """Authenticate using Basic Auth. On success, store JWT cookie into persistent session."""
    try:
        # Use a fresh temp session for initial auth
        temp_session = requests.Session()
        resp = temp_session.post(
            "https://api.worldquantbrain.com/authentication",
            auth=(email, password),
            timeout=15
        )
        
        if resp.status_code in [200, 201]:
            # Collect cookies from response and store them
            cookie_parts = []
            for k, v in resp.cookies.items():
                cookie_parts.append(f"{k}={v}")
            
            # Also check Set-Cookie header directly
            set_cookie = resp.headers.get("Set-Cookie", "")
            if not cookie_parts and set_cookie:
                # Extract t= JWT from Set-Cookie
                for seg in set_cookie.split(","):
                    seg = seg.strip()
                    if seg.startswith("t="):
                        jwt_part = seg.split(";")[0].strip()
                        cookie_parts.append(jwt_part)
                        break

            if cookie_parts:
                cookie_str = "; ".join(cookie_parts)
                auth_state["cookie"] = cookie_str
                # Apply to persistent session immediately
                _apply_session_cookie(cookie_str)
            
            auth_state["user_email"] = email
            auth_state["authenticated"] = True
            auth_state["last_checked"] = datetime.now(timezone.utc).isoformat()
            auth_pause_event.set()  # Unpause worker threads
            save_auth_credentials(email, password)
            print(f"[AUTH] Authenticated as {email}. Cookie: {auth_state['cookie'][:60]}...")
            return True, "Authenticated successfully with WorldQuant BRAIN", None, None

        elif resp.status_code == 401:
            www_auth = resp.headers.get("WWW-Authenticate", "")
            location = resp.headers.get("Location", "")

            if "persona" in www_auth.lower() or "inquiry" in location.lower():
                # Parse inquiry ID from Location header
                inquiry_id = None
                if "inquiry=" in location:
                    inquiry_id = location.split("inquiry=")[-1].split("&")[0]
                
                if not inquiry_id:
                    try:
                        body = resp.json()
                        inquiry_id = body.get("inquiry")
                    except Exception:
                        pass

                # The browser display URL (for user to open and do face scan)
                if inquiry_id:
                    browser_persona_url = f"https://api.worldquantbrain.com/authentication/persona?inquiry={inquiry_id}"
                else:
                    browser_persona_url = "https://api.worldquantbrain.com"

                # The API completion URL (what we POST to after face scan — per BRAIN Python SDK)
                # urljoin(resp.url, location) where resp.url = https://api.worldquantbrain.com/authentication
                from urllib.parse import urljoin
                if location:
                    api_persona_url = urljoin("https://api.worldquantbrain.com/authentication", location)
                elif inquiry_id:
                    api_persona_url = f"https://api.worldquantbrain.com/authentication/persona?inquiry={inquiry_id}"
                else:
                    api_persona_url = ""

                auth_state["authenticated"] = False
                auth_state["user_email"] = email
                # Store BOTH URLs: browser URL (for user) and API URL (for POST)
                auth_state["pending_persona_url"] = browser_persona_url   # shown to user
                auth_state["pending_api_persona_url"] = api_persona_url   # used in POST
                auth_state["pending_email"] = email
                auth_state["pending_password"] = password
                save_auth_credentials()
                print(f"[AUTH] Persona required for {email}.")
                print(f"[AUTH]   Browser URL: {browser_persona_url}")
                print(f"[AUTH]   API URL:     {api_persona_url}")
                return False, f"Face verification required for {email}. Open the link to complete.", inquiry_id, browser_persona_url
            else:
                auth_state["authenticated"] = False
                err_detail = ""
                try:
                    err_detail = resp.json().get("detail", resp.text)
                except Exception:
                    err_detail = resp.text
                return False, f"Invalid credentials: {err_detail}", None, None
        else:
            auth_state["authenticated"] = False
            return False, f"Unexpected HTTP {resp.status_code}: {resp.text[:200]}", None, None

    except Exception as e:
        auth_state["authenticated"] = False
        return False, f"Connection error: {str(e)}", None, None

def _jwt_is_expired(cookie_str):
    """Quickly decode the JWT payload and check expiry without hitting BRAIN API."""
    if not cookie_str:
        return True
    try:
        token = ""
        for part in cookie_str.split(";"):
            part = part.strip()
            if part.startswith("t="):
                token = part[2:]
                break
        if not token:
            # Fallback: check if the string itself is a raw JWT token starting with eyJ
            if "eyJ" in cookie_str:
                token = cookie_str[cookie_str.find("eyJ"):]
                token = token.split(";")[0].split(" ")[0].strip()
        if not token:
            return True
        payload_b64 = token.split(".")[1]
        padded = payload_b64 + "=" * (4 - len(payload_b64) % 4)
        import base64
        payload = json.loads(base64.urlsafe_b64decode(padded))
        exp = payload.get("exp", 0)
        return time.time() > exp
    except Exception as e:
        print(f"[AUTH] Error decoding JWT: {e}")
        return True  # treat unreadable JWT as expired

def check_auth_status():
    session = get_brain_session()
    current_cookie = auth_state.get("cookie", "")

    # ── 4-Hour JWT Device Session ──
    # WorldQuant BRAIN session tokens are valid for 4 hours (14,400s) from login.
    # While token is valid, instantly grant access without requiring email/password or Face ID.
    if current_cookie and not _jwt_is_expired(current_cookie):
        auth_state["authenticated"] = True
        auth_pause_event.set()
        return True, auth_state.get("user_email", "PK18292")

    # If JWT is expired, attempt auto-refresh with saved credentials
    if current_cookie and _jwt_is_expired(current_cookie):
        auth_state["authenticated"] = False
        auth_pause_event.clear()
        if auth_state.get("saved_email") and auth_state.get("saved_password"):
            print(f"[AUTH] JWT expired. Auto-refreshing for {auth_state['saved_email']}...")
            ok, msg, inquiry_id, persona_url = authenticate_brain_user(
                auth_state["saved_email"], auth_state["saved_password"])
            if ok:
                auth_state["authenticated_at"] = time.time()
                auth_pause_event.set()
                return True, auth_state["user_email"]
            if persona_url:
                return False, f"FACE_REQUIRED:{persona_url}"
        return False, "JWT expired. Please log in again."

    try:
        # Correct endpoint: GET /authentication (per BRAIN API docs)
        resp = session.get("https://api.worldquantbrain.com/authentication", timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            auth_state["authenticated"] = True
            auth_pause_event.set()
            user_data = data.get("user") or {}
            auth_state["user_email"] = user_data.get("id") or data.get("email") or auth_state["user_email"]
            auth_state["last_checked"] = datetime.now(timezone.utc).isoformat()
            save_auth_credentials()
            return True, auth_state["user_email"]
        elif resp.status_code == 204:
            auth_state["authenticated"] = False
            auth_pause_event.clear()
            if auth_state.get("saved_email") and auth_state.get("saved_password"):
                print(f"[AUTH] Not authenticated (204). Auto-refreshing for {auth_state['saved_email']}...")
                ok, msg, inquiry_id, persona_url = authenticate_brain_user(auth_state["saved_email"], auth_state["saved_password"])
                if ok:
                    return True, auth_state["user_email"]
                if persona_url:
                    return False, f"FACE_REQUIRED:{persona_url}"
            return False, "Not authenticated. Please log in."
        elif resp.status_code == 401:
            auth_state["authenticated"] = False
            if auth_state.get("saved_email") and auth_state.get("saved_password"):
                ok, msg, inquiry_id, persona_url = authenticate_brain_user(auth_state["saved_email"], auth_state["saved_password"])
                if ok:
                    return True, auth_state["user_email"]
                if persona_url:
                    return False, f"FACE_REQUIRED:{persona_url}"
            return False, "Session expired. Please re-login."
        else:
            auth_state["authenticated"] = False
            return False, f"HTTP {resp.status_code} from BRAIN. Please re-login."

    except Exception as e:
        auth_state["authenticated"] = False
        return False, str(e)

# -----------------------------------------------------------------------------
# Core Simulation & API Functionality
# -----------------------------------------------------------------------------
def extract_metrics(data, session, headers=None):
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
                resp = session.get(alpha_url, timeout=5)
                if resp.status_code == 200:
                    a_data = resp.json()
                    if "is" in a_data and isinstance(a_data["is"], dict):
                        return a_data["is"]
                elif resp.status_code == 429:
                    time.sleep(3)
            except Exception:
                time.sleep(1)
    return None


def _build_sim_payload(expression, settings):
    """Build the simulation payload dict from expression + settings."""
    region = settings.get("region", "USA")
    neut = settings.get("neutralization", "INDUSTRY")
    # WorldQuant BRAIN API rejects RAM neutralization across all regions (returns HTTP 400)
    if neut == "RAM":
        neut = "INDUSTRY"
        print(f"[SIM] Auto-corrected invalid RAM neutralization to INDUSTRY for region '{region}'")

    raw_universe = str(settings.get("universe", "TOP3000")).strip()
    # Auto-align universe if region and universe mismatch
    if region == "USA" and any(raw_universe.startswith(prefix) for prefix in ["GLB_", "EUR_", "ASI_", "IND_", "CHN_", "KOR_", "HKG_", "DEU_", "GBR_"]):
        raw_universe = "TOP3000"
        print(f"[SIM] Auto-aligned universe for USA region to 'TOP3000'")
    elif region == "EUR" and raw_universe == "TOP3000":
        raw_universe = "EUR_TOP1000"
    elif region == "ASI" and raw_universe == "TOP3000":
        raw_universe = "ASI_TOP1000"
    elif region == "IND" and raw_universe == "TOP3000":
        raw_universe = "IND_TOP500"
    elif region == "CHN" and raw_universe == "TOP3000":
        raw_universe = "CHN_TOP1000"

    payload_settings = {
        "instrumentType": settings.get("instrumentType", "EQUITY"),
        "region": region,
        "universe": raw_universe,
        "delay": int(settings.get("delay", 1)),
        "decay": int(settings.get("decay", 0)),
        "neutralization": neut,
        "truncation": float(settings.get("truncation", 0.08)),
        "pasteurization": settings.get("pasteurization", "ON"),
        "nanHandling": "ON" if str(settings.get("nanHandling", "")).upper() == "ON" else "OFF",
        "language": settings.get("language", "FASTEXPR"),
        "unitHandling": settings.get("unitHandling", "VERIFY"),
        "visualization": False,
    }
    # Optional settings — only include if set to non-default values
    test_period = settings.get("testPeriod", "")
    if test_period and test_period not in ["", "P0Y0M", "P0Y"]:
        payload_settings["testPeriod"] = test_period
    max_trade = settings.get("maxTrade", "OFF")
    if max_trade and max_trade.upper() != "OFF":
        payload_settings["maxTrade"] = max_trade.upper()
    max_position = settings.get("maxPosition", "OFF")
    if max_position and max_position.upper() != "OFF":
        payload_settings["maxPosition"] = max_position.upper()
    return {
        "type": "REGULAR",
        "settings": payload_settings,
        "regular": expression.strip()
    }

def _poll_simulation(session, status_url, alpha_hash, universe, decay, slot_id=None):
    """Poll a simulation URL until complete. Returns result dict."""
    poll_count = 0
    cache = load_cache()
    while poll_count < 300:
        if cancel_event.is_set():
            return {"status": "CANCELLED", "error": "Cancelled by user", "hash": alpha_hash}
        try:
            poll_resp = session.get(status_url, timeout=15)
            _update_rate_limits(poll_resp.headers)

            if poll_resp.status_code == 429:
                wait = int(poll_resp.headers.get("Retry-After", 10))
                print(f"[POLL] 429 rate limited on {status_url}, sleeping {wait}s")
                time.sleep(wait)
                continue

            if poll_resp.status_code not in [200]:
                return {"status": f"POLL_HTTP_{poll_resp.status_code}", "error": poll_resp.text[:200], "hash": alpha_hash}

            data = poll_resp.json()
            retry_after = poll_resp.headers.get("Retry-After")
            status = data.get("status", "")
            progress = data.get("progress", 0)
            alpha_id = data.get("alpha")

            if slot_id is not None and slot_id in slot_status:
                with slot_lock:
                    slot_status[slot_id]["progress_pct"] = f"{round(float(progress) * 100, 1)}%"

            if status in ["COMPLETE", "WARNING"] or progress == 1.0 or (alpha_id and isinstance(alpha_id, str) and progress == 0 and not status):
                failed_checks = []
                metrics = None

                if alpha_id and isinstance(alpha_id, str):
                    try:
                        a_resp = session.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}", timeout=10)
                        if a_resp.status_code == 200:
                            a_data = a_resp.json()
                            metrics = a_data.get("is") or {}
                            checks = a_data.get("is", {}).get("checks", [])
                            failed_checks = [c["name"] for c in checks if c.get("result") == "FAIL"]
                            print(f"[SIM] Complete: alpha={alpha_id} sharpe={metrics.get('sharpe')} fails={failed_checks}")
                    except Exception as e:
                        print(f"[SIM] Error fetching alpha {alpha_id}: {e}")

                if metrics is None:
                    metrics = extract_metrics(data, session, None)

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
                    return {"status": "METRICS_MISSING", "alpha_id": alpha_id, "error": "Simulation complete but metrics unavailable", "hash": alpha_hash}

            elif status in ["FAILED", "ERROR", "TIMEOUT", "CANCEL", "CANCELLED"]:
                err = data.get("message") or data.get("error") or f"Simulation {status}"
                print(f"[SIM] Failed: {err}")
                return {"status": status, "error": err, "failed_checks": [], "hash": alpha_hash}

            # Status is WAITING or SIMULATING — keep polling
            wait_time = 3
            if retry_after:
                try:
                    wait_time = max(float(retry_after), 2)
                except Exception:
                    pass
            time.sleep(wait_time)
            poll_count += 1

        except Exception as e:
            print(f"[POLL] Exception on {status_url}: {e}")
            time.sleep(5)
            poll_count += 1

    return {"status": "TIMEOUT", "error": "Exceeded 300 polling attempts", "hash": alpha_hash}

def run_single_simulation(expression, settings, dry_run=False, slot_id=None):
    alpha_hash = get_alpha_hash(expression, settings)
    cache = load_cache()
    universe = settings.get("universe", "TOP3000")
    decay = settings.get("decay", 0)

    # 1. Deduplication Cache Lookup
    if alpha_hash in cache:
        cached_entry = cache[alpha_hash]
        print(f"[CACHE] Hit for {alpha_hash[:12]}")
        return {
            "status": "CACHED_DUPLICATE",
            "alpha_id": cached_entry.get("alpha_id"),
            "metrics": cached_entry.get("metrics"),
            "failed_checks": cached_entry.get("failed_checks", []),
            "cached": True,
            "hash": alpha_hash
        }

    # 2. Dry Run (Mock)
    if dry_run:
        time.sleep(random.uniform(0.3, 0.8))
        if random.random() < 0.8:
            metrics = {
                "sharpe": round(random.uniform(0.2, 2.4), 4),
                "fitness": round(random.uniform(0.4, 2.2), 4),
                "returns": round(random.uniform(-0.05, 0.35), 4),
                "drawdown": round(random.uniform(-0.25, -0.01), 4),
                "margin": round(random.uniform(0.00005, 0.00035), 6),
                "turnover": round(random.uniform(0.05, 0.85), 4)
            }
            alpha_id = f"MOCK_{alpha_hash[:8].upper()}"
            result = {"status": "SUCCESS", "alpha_id": alpha_id, "metrics": metrics,
                      "failed_checks": [], "universe": universe, "decay": decay, "cached": False, "hash": alpha_hash}
            cache[alpha_hash] = result
            save_cache(cache)
            return result
        else:
            return {"status": "FAILED", "error": "Mock check failed", "universe": universe, "decay": decay, "cached": False, "hash": alpha_hash}

    # 3. Live BRAIN Simulation
    session = get_brain_session()
    payload = _build_sim_payload(expression, settings)

    print(f"[SIM] Submitting: {expression[:60]} | {settings.get('universe')} delay={settings.get('delay')} neut={settings.get('neutralization')}")

    backoff = 15
    resp = None
    for attempt in range(6):
        if cancel_event.is_set():
            return {"status": "CANCELLED", "error": "Cancelled by user", "hash": alpha_hash}
        try:
            resp = session.post("https://api.worldquantbrain.com/simulations", json=payload, timeout=20)
            _update_rate_limits(resp.headers)
            print(f"[SIM] POST attempt {attempt+1}: HTTP {resp.status_code}")

            if resp.status_code in [401, 403]:
                print(f"[SIM] HTTP {resp.status_code} Auth error — IMMEDIATELY PAUSING ALL WORKER SLOTS (0 WQ REQUESTS)...")
                auth_state["authenticated"] = False
                auth_pause_event.clear()  # INSTANTLY FREEZE ALL 8 WORKER THREADS

                # Attempt background auto-refresh with saved credentials
                if auth_state.get("saved_email") and auth_state.get("saved_password"):
                    ok, msg, inquiry_id, persona_url = authenticate_brain_user(auth_state["saved_email"], auth_state["saved_password"])
                    if ok:
                        print("[SIM] Auto-refresh succeeded! Unpausing worker threads...")
                        auth_state["authenticated"] = True
                        auth_pause_event.set()
                        session = get_brain_session()
                        time.sleep(1)
                        continue
                    elif persona_url:
                        auth_state["pending_persona_url"] = persona_url
                        print(f"[SIM] Face verification required ({persona_url}). Workers 100% frozen until user completes Face ID scan.")

                # Block worker thread completely until user completes Face ID & calls auth_pause_event.set()
                print("[SIM] Worker slot waiting on auth_pause_event...")
                auth_pause_event.wait()
                session = get_brain_session()
                continue


            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", backoff))
                print(f"[SIM] Rate limited (429), sleeping {wait}s (remaining={rate_limit_state.get('remaining')})")
                time.sleep(wait)
                backoff = min(backoff * 2, 120)
                continue

            if resp.status_code == 400:
                err_text = resp.text
                err_upper = err_text.upper()
                if any(kw in err_upper for kw in ["LIMIT", "CONCURRENT", "SIMULATION", "THROTTLE", "REACHED", "TOO MANY"]):
                    wait = 6 * (attempt + 1)
                    print(f"[SIM] Concurrency/Limit HTTP 400 on attempt {attempt+1}, sleeping {wait}s...")
                    time.sleep(wait)
                    continue
                else:
                    formatted_err = format_brain_api_error(err_text)
                    print(f"[SIM] Error response (400): {formatted_err}")
                    return {"status": "HTTP_400", "error": formatted_err, "hash": alpha_hash}

            if resp.status_code in [201, 202]:
                break

            formatted_err = format_brain_api_error(resp.text)
            print(f"[SIM] Error response: {formatted_err}")
            return {"status": f"HTTP_{resp.status_code}", "error": formatted_err, "hash": alpha_hash}

        except Exception as e:
            print(f"[SIM] Request exception: {e}")
            time.sleep(5)

    if not resp or resp.status_code not in [201, 202]:
        return {"status": "REQUEST_FAILED", "error": "Could not reach BRAIN API after retries", "hash": alpha_hash}

    status_url = resp.headers.get("Location", "")
    if not status_url:
        return {"status": "NO_LOCATION", "error": "No Location header in simulation response", "hash": alpha_hash}
    if not status_url.startswith("http"):
        status_url = "https://api.worldquantbrain.com" + status_url

    print(f"[SIM] Polling: {status_url}")
    return _poll_simulation(session, status_url, alpha_hash, universe, decay, slot_id=slot_id)

def submit_alpha_to_brain(alpha_id, dry_run=False):
    if dry_run or alpha_id.startswith("MOCK_"):
        return True, "Mock submission"
    session = get_brain_session()
    try:
        resp = session.post("https://api.worldquantbrain.com/submissions", json={"alpha": alpha_id}, timeout=10)
        if resp.status_code in [200, 201, 202]:
            return True, f"Submitted (HTTP {resp.status_code})"
        return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
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

            # Check for Zero Warning & Sharpe >= 2.0 condition
            HIGH_SHARPE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "high_sharpe_zero_warnings.txt")
            if s_val >= 2.0 and not failed_checks:
                with open(HIGH_SHARPE_FILE, "a", encoding="utf-8") as f_high:
                    f_high.write(f"Expression: {expression}\n")
                    f_high.write(f"Alpha ID: {result.get('alpha_id', 'N/A')}\n")
                    f_high.write(f"Sharpe: {s_val:.4f}, Fitness: {f_val:.4f}, Returns: {returns}%, Margin(bps): {margin}, Turnover: {turnover}%\n")
                    f_high.write(f"Settings: Universe={universe}, Delay={delay}, Neutralization={neutralization}, Region={region}\n")
                    f_high.write("=" * 70 + "\n\n")
                print(f"[EXCELLENT] Saved High Sharpe (>=2.0, 0 Warnings) Alpha: {expression[:50]}")

            # Check for Submitable Alphas (Sharpe >= 1.25, Fitness >= 1.0, Margin >= 10bps, Turnover <= 70%, 0 failed checks)
            t_val = float(metrics.get("turnover", 1.0))
            if s_val >= 1.25 and f_val >= 1.0 and m_val >= 0.0001 and t_val <= 0.70 and not failed_checks:
                SUBMITABLE_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "submitable_alphas.txt")
                SUBMITABLE_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "submitable_alphas.csv")
                with open(SUBMITABLE_TXT, "a", encoding="utf-8") as f_sub:
                    f_sub.write(f"Expression: {expression}\n")
                    f_sub.write(f"Alpha ID: {result.get('alpha_id', 'N/A')}\n")
                    f_sub.write(f"Sharpe: {s_val:.4f}, Fitness: {f_val:.4f}, Returns: {returns}%, Margin: {margin}bps, Turnover: {turnover}%\n")
                    f_sub.write(f"Settings: Universe={universe}, Delay={delay}, Neutralization={neutralization}, Region={region}\n")
                    f_sub.write("-" * 65 + "\n")
                sub_exists = os.path.exists(SUBMITABLE_CSV)
                with open(SUBMITABLE_CSV, "a", newline="", encoding="utf-8") as f_sub_csv:
                    w = csv.writer(f_sub_csv)
                    if not sub_exists:
                        w.writerow(["AlphaID", "Sharpe", "Fitness", "Returns(%)", "Margin(bps)", "Turnover(%)", "Universe", "Region", "Neutralization", "Expression"])
                    w.writerow([result.get('alpha_id', 'N/A'), s_val, f_val, returns, margin, turnover, universe, region, neutralization, expression])
                print(f"[SUBMITABLE] Saved submitable alpha: {result.get('alpha_id')} (Sharpe {s_val:.2f})")
        
        # Check for Region-Agnostic GLB logging
        if region == "GLB" or settings.get("region") == "GLB":
            log_region_agnostic_result(result, expression, settings)
    except Exception as e:
        print(f"Error logging to CSV: {e}")

REGION_AGNOSTIC_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "region_agnostic_alpha_results.csv")

def log_region_agnostic_result(result, expression, settings, orig_sharpe=None):
    try:
        metrics = result.get("metrics") or {}
        s_val = float(metrics.get("sharpe", 0.0))
        f_val = float(metrics.get("fitness", 0.0))
        r_val = float(metrics.get("returns", 0.0))
        m_val = float(metrics.get("margin", 0.0))
        t_val = float(metrics.get("turnover", 0.0))
        fc = result.get("failed_checks", [])
        fc_str = ";".join(fc) if fc else "NONE"
        status = result.get("status", "UNKNOWN")
        
        pass_fail = "PASS" if (s_val >= 1.25 and not fc and status in ["SUCCESS", "CACHED_DUPLICATE"]) else "FAIL"
        
        file_exists = os.path.exists(REGION_AGNOSTIC_CSV)
        with open(REGION_AGNOSTIC_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if not file_exists:
                w.writerow(["Index", "OriginalSharpe", "GLB_Sharpe", "GLB_Fitness", "GLB_Returns(%)", "GLB_Margin(bps)", "GLB_Turnover(%)", "FailedChecks", "PassFail", "AlphaID", "Expression"])
            
            row_idx = 1
            if file_exists:
                with open(REGION_AGNOSTIC_CSV, "r", encoding="utf-8") as rf:
                    row_idx = max(1, len(rf.readlines()))
            
            w.writerow([
                row_idx,
                orig_sharpe if orig_sharpe is not None else "N/A",
                s_val,
                f_val,
                r_val,
                round(m_val * 10000, 2),
                t_val,
                fc_str,
                pass_fail,
                result.get("alpha_id", "N/A"),
                expression
            ])
            print(f"[REGION-AGNOSTIC LOG] Saved GLB result: Sharpe={s_val:.2f}, Result={pass_fail}, AlphaID={result.get('alpha_id')}")
    except Exception as e:
        print(f"Error logging to region_agnostic_alpha_results.csv: {e}")


BATCH_RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "batch_results")
os.makedirs(BATCH_RESULTS_DIR, exist_ok=True)

def save_batch_csv(batch_id):
    """Write all simulation results for a specific batch to batch_results/<batch_id>.csv"""
    if batch_id not in batch_jobs:
        return None
    b_data = batch_jobs[batch_id]
    filepath = os.path.join(BATCH_RESULTS_DIR, f"{batch_id}.csv")
    try:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Index", "Status", "Sharpe", "Fitness", "Returns(%)", "Drawdown(%)", "Margin(bps)", "Turnover(%)", "FailedChecks", "AlphaID", "Expression"])
            for idx, item in enumerate(b_data.get("items", [])):
                res = item.get("result") or {}
                m = res.get("metrics") or {}
                fc = ";".join(res.get("failed_checks", []))
                writer.writerow([
                    idx + 1,
                    item.get("status", "QUEUED"),
                    m.get("sharpe", ""),
                    m.get("fitness", ""),
                    m.get("returns", ""),
                    m.get("drawdown", ""),
                    m.get("margin", ""),
                    m.get("turnover", ""),
                    fc,
                    res.get("alpha_id", ""),
                    item.get("expression", "")
                ])
        return filepath
    except Exception as e:
        print(f"Error saving batch CSV: {e}")
        return None

# ── Startup: load saved credentials NOW (all helpers are defined above) ──────
# This is the fix for "already logged in" not working across restarts.
# load_auth_credentials() calls _apply_session_cookie() which requires
# _brain_session to exist \u2014 which it does by line 132 above.
load_auth_credentials()
print(f"[STARTUP] Auth state: email={auth_state.get('user_email')} cookie={'SET' if auth_state.get('cookie') else 'NONE'}")

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Background Queue Worker — 8 Parallel Slots (GLB capped at 4, USA/Others 8)
# Global WorldQuant API concurrency limiter (max 2 active simulations across all slots)
brain_sim_semaphore = threading.BoundedSemaphore(2)

def worker_slot(slot_id):
    """Each slot runs as a permanent daemon thread, pulling from job_queue."""
    while True:
        # Pause completely if authentication is lost or Face ID scan is pending
        if not auth_pause_event.is_set():
            with slot_lock:
                slot_status[slot_id].update({
                    "status": "PAUSED_AUTH",
                    "expression": "Paused — waiting for Re-login / Face ID verification...",
                    "batch_id": None, "item_index": None, "start_time": None
                })
            auth_pause_event.wait()
            with slot_lock:
                slot_status[slot_id].update({"status": "IDLE", "expression": None})

        job_item = job_queue.get()
        if job_item is None:
            job_queue.task_done()
            continue

        batch_id, item_index, item = job_item

        # Skip immediately if cancelled
        if cancel_event.is_set():
            with jobs_lock:
                if batch_id in batch_jobs:
                    batch_jobs[batch_id]["items"][item_index]["status"] = "CANCELLED"
                    batch_jobs[batch_id]["completed"] += 1
                    completed = batch_jobs[batch_id]["completed"]
                    total = batch_jobs[batch_id]["total"]
                    batch_jobs[batch_id]["progress"] = round((completed / total) * 100, 1)
                    if completed == total:
                        batch_jobs[batch_id]["status"] = "CANCELLED"
            job_queue.task_done()
            continue

        expression = item["expression"]
        settings = item["settings"]
        dry_run = item["dry_run"]
        auto_submit = item.get("auto_submit", False)
        region = settings.get("region", "USA")

        # Acquire concurrency lock across all regions (max 2 active at once)
        brain_sim_semaphore.acquire()

        try:
            # Mark slot as busy
            with slot_lock:
                slot_status[slot_id].update({
                    "status": "SIMULATING",
                    "expression": expression[:80] + ("..." if len(expression) > 80 else ""),
                    "batch_id": batch_id,
                    "item_index": item_index,
                    "start_time": datetime.now(timezone.utc).isoformat()
                })

            with jobs_lock:
                if batch_id in batch_jobs:
                    batch_jobs[batch_id]["items"][item_index]["status"] = "SIMULATING"
                    batch_jobs[batch_id]["items"][item_index]["slot"] = slot_id + 1
                    batch_jobs[batch_id]["items"][item_index]["start_time"] = datetime.now(timezone.utc).isoformat()

            res = run_single_simulation(expression, settings, dry_run=dry_run, slot_id=slot_id)

            # Auto-submit check — only submit if Sharpe >= 0.5 and no PROD_CORRELATION or SELF_CORRELATION failures
            metrics = res.get("metrics") or {}
            sharpe = float(metrics.get("sharpe", 0.0))
            failed_checks = res.get("failed_checks", [])
            has_corr_fail = any(kw in str(fc).upper() for fc in failed_checks for kw in ["PROD_CORRELATION", "SELF_CORRELATION"])

            if auto_submit and res.get("status") in ["SUCCESS", "CACHED_DUPLICATE"] and sharpe >= 0.5 and not has_corr_fail:
                alpha_id = res.get("alpha_id")
                if alpha_id:
                    sub_ok, sub_msg = submit_alpha_to_brain(alpha_id, dry_run=dry_run)
                    res["submitted"] = sub_ok
                    res["submit_msg"] = sub_msg

            log_result_to_csv(res, expression, settings)
        finally:
            brain_sim_semaphore.release()

        with jobs_lock:
            if batch_id in batch_jobs:
                batch_jobs[batch_id]["items"][item_index]["status"] = res.get("status")
                batch_jobs[batch_id]["items"][item_index]["result"] = res
                batch_jobs[batch_id]["items"][item_index]["slot"] = slot_id + 1
                batch_jobs[batch_id]["completed"] += 1
                completed = batch_jobs[batch_id]["completed"]
                total = batch_jobs[batch_id]["total"]
                batch_jobs[batch_id]["progress"] = round((completed / total) * 100, 1)
                if completed == total:
                    batch_jobs[batch_id]["status"] = "COMPLETED"
                    batch_jobs[batch_id]["end_time"] = datetime.now(timezone.utc).isoformat()
                save_batch_jobs()

        # Mark slot as idle
        with slot_lock:
            slot_status[slot_id].update({
                "status": "IDLE",
                "expression": None,
                "batch_id": None,
                "item_index": None,
                "start_time": None
            })

        job_queue.task_done()

# Restore persisted batch jobs from disk on startup
loaded_batch_jobs = load_batch_jobs()
if loaded_batch_jobs:
    with jobs_lock:
        batch_jobs.update(loaded_batch_jobs)
    # Re-enqueue unfinished items into worker queue
    for b_id, b_data in batch_jobs.items():
        if b_data.get("status") in ["RUNNING", "PENDING"]:
            items = b_data.get("items", [])
            for task_idx, item_obj in enumerate(items):
                if item_obj.get("status") in ["QUEUED", "SIMULATING", "PENDING"]:
                    item_obj["status"] = "QUEUED"
                    job_queue.put((b_id, task_idx, item_obj))
    print(f"[BATCH] Restored {len(batch_jobs)} batch jobs from disk, re-enqueued pending items into worker queue.")

def auto_replenish_loop():
    """Background daemon thread to auto-replenish queue and maintain active job_queue."""
    while True:
        try:
            time.sleep(15)
            with jobs_lock:
                # 1. If job_queue in memory is empty, re-enqueue all QUEUED items from active batches
                if job_queue.empty():
                    re_count = 0
                    for b_id, b_data in batch_jobs.items():
                        if isinstance(b_data, dict) and b_data.get("status") in ["RUNNING", "PENDING"]:
                            items = b_data.get("items", [])
                            for task_idx, item_obj in enumerate(items):
                                if item_obj.get("status") in ["QUEUED", "SIMULATING", "PENDING"]:
                                    item_obj["status"] = "QUEUED"
                                    job_queue.put((b_id, task_idx, item_obj))
                                    re_count += 1
                    if re_count > 0:
                        print(f"[QUEUE-RECOVERY] Re-enqueued {re_count} QUEUED items into in-memory job_queue.")

                # Ensure all 8 worker threads are alive
                for sid in range(MAX_CONCURRENT_SIMS):
                    if sid >= len(worker_threads) or not worker_threads[sid].is_alive():
                        t = threading.Thread(target=worker_slot, args=(sid,), daemon=True)
                        t.start()
                        if sid < len(worker_threads):
                            worker_threads[sid] = t
                        else:
                            worker_threads.append(t)
                        print(f"[WORKER-HEALTH] Respawned dead worker thread for slot {sid+1}")

                # 2. Check overall remaining total for auto-replenish
                remaining_total = 0
                for b in batch_jobs.values():
                    if isinstance(b, dict) and b.get("status") in ["RUNNING", "PENDING"]:
                        tot = b.get("total", 0)
                        comp = b.get("completed", 0)
                        remaining_total += max(0, tot - comp)
                
                if remaining_total < 1000:
                    print(f"[AUTO-REPLENISH] Queue low ({remaining_total} remaining). Generating 1,000 new Alphas...")
                    from auto_replenish import create_batch
                    for _ in range(2):
                        b_id, b_data = create_batch(500)
                        batch_jobs[b_id] = b_data
                        items = b_data.get("items", [])
                        for task_idx, item_obj in enumerate(items):
                            job_queue.put((b_id, task_idx, item_obj))
                        print(f"[AUTO-REPLENISH] Added and enqueued batch {b_id}: {b_data['name']}")
                    save_batch_jobs()
        except Exception as e:
            print(f"[AUTO-REPLENISH] Error: {e}")

# Launch Auto-Replenish background daemon thread
t_replenish = threading.Thread(target=auto_replenish_loop, daemon=True)
t_replenish.start()

# Launch all 8 worker threads
worker_threads = []
for _slot_id in range(MAX_CONCURRENT_SIMS):
    t = threading.Thread(target=worker_slot, args=(_slot_id,), daemon=True)
    t.start()
    worker_threads.append(t)




# -----------------------------------------------------------------------------
# REST API Endpoints
# -----------------------------------------------------------------------------
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

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
        "last_checked": auth_state["last_checked"],
        "rate_limit": rate_limit_state
    })

@app.route("/api/auth/update", methods=["POST"])
def update_auth():
    data = request.get_json() or {}
    new_cookie = data.get("cookie")
    if new_cookie:
        auth_state["cookie"] = new_cookie.strip()
        _apply_session_cookie(new_cookie.strip())  # Apply to persistent session
        ok, details = check_auth_status()
        return jsonify({"success": ok, "details": details, "user_email": auth_state["user_email"]})
    return jsonify({"success": False, "error": "No cookie string provided"}), 400

@app.route("/api/simulations/ratelimit", methods=["GET"])
def get_rate_limit():
    """Return current rate limit state from last simulation POST."""
    return jsonify(rate_limit_state)

@app.route("/api/health", methods=["GET"])
def get_system_health():
    """System health endpoint for background platform and WorldQuant error monitoring."""
    is_auth, details = check_auth_status()
    with jobs_lock:
        remaining = 0
        running = 0
        for b in batch_jobs.values():
            if isinstance(b, dict):
                if b.get("status") in ["RUNNING", "PENDING"]:
                    running += 1
                    tot = b.get("total", 0)
                    comp = b.get("completed", 0)
                    remaining += max(0, tot - comp)

    return jsonify({
        "status": "OK" if is_auth else "AUTH_REQUIRED",
        "authenticated": is_auth,
        "user_email": auth_state.get("user_email"),
        "pending_persona_url": auth_state.get("pending_persona_url"),
        "remaining_queue": remaining,
        "running_batches": running,
        "rate_limit": rate_limit_state
    })


@app.route("/api/results/region-agnostic", methods=["GET"])
def get_region_agnostic_results():
    filepath = os.path.join(WORKSPACE_DIR, "region_agnostic_alpha_results.csv")
    if not os.path.exists(filepath):
        return jsonify({"results": [], "total": 0})
    rows = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    except Exception as e:
        print(f"Error reading region_agnostic_alpha_results.csv: {e}")
    return jsonify({"results": rows, "total": len(rows)})

@app.route("/download/region-agnostic", methods=["GET"])
def download_region_agnostic_csv():
    filepath = os.path.join(WORKSPACE_DIR, "region_agnostic_alpha_results.csv")
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, download_name="region_agnostic_alpha_results.csv")
    return jsonify({"error": "No region agnostic results file found"}), 404



@app.route("/api/auth/login", methods=["POST"])
def login_auth():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400
    ok, details, inquiry_id, persona_url = authenticate_brain_user(email, password)
    return jsonify({
        "success": ok,
        "message": details,
        "user_email": auth_state["user_email"],
        "requires_persona": bool(inquiry_id),
        "inquiry_id": inquiry_id,
        "persona_url": persona_url
    })

@app.route("/api/auth/complete-persona", methods=["POST"])
def complete_persona():
    """
    Called AFTER the user completes the face scan in the browser tab.
    Per BRAIN Python SDK: POST to the API persona URL (api.worldquantbrain.com/authentication/persona?inquiry=...)
    with the SAME session AND basic auth (email:password). Without basic auth you get 403.
    """
    email    = auth_state.get("pending_email") or ""
    password = auth_state.get("pending_password") or ""

    # Use the stored API URL (not the browser display URL)
    api_url = auth_state.get("pending_api_persona_url") or ""

    # Fallback: reconstruct from the browser URL if we only have that
    if not api_url:
        browser_url = auth_state.get("pending_persona_url") or ""
        if "inquiry=" in browser_url:
            inquiry_id = browser_url.split("inquiry=")[-1].split("&")[0]
            api_url = f"https://api.worldquantbrain.com/authentication/persona?inquiry={inquiry_id}"

    if not api_url:
        return jsonify({"success": False, "message": "No pending face verification. Please log in first."}), 400
    if not email or not password:
        return jsonify({"success": False, "message": "No saved credentials. Please enter email and password again."}), 400

    session = get_brain_session()
    try:
        print(f"[PERSONA] POSTing to API URL: {api_url}")
        # *** CRITICAL: must include basic auth (email:password) — per BRAIN Python SDK ***
        resp = session.post(api_url, auth=(email, password), timeout=30)
        print(f"[PERSONA] Response: HTTP {resp.status_code} — {resp.text[:200]}")

        if resp.status_code in [200, 201]:
            # Grab JWT from response cookies or Set-Cookie header
            cookie_parts = [f"{k}={v}" for k, v in resp.cookies.items()]
            if not cookie_parts:
                set_cookie = resp.headers.get("Set-Cookie", "")
                for seg in set_cookie.split(","):
                    seg = seg.strip()
                    if seg.startswith("t="):
                        cookie_parts.append(seg.split(";")[0].strip())
                        break

            if cookie_parts:
                cookie_str = "; ".join(cookie_parts)
                auth_state["cookie"] = cookie_str
                _apply_session_cookie(cookie_str)

            auth_state["authenticated"] = True
            auth_pause_event.set()  # UNPAUSE ALL WORKER THREADS IMMEDIATELY
            auth_state["last_checked"] = datetime.now(timezone.utc).isoformat()
            auth_state["pending_persona_url"] = None
            auth_state["pending_api_persona_url"] = None

            try:
                body = resp.json()
                uid = (body.get("user") or {}).get("id") or body.get("email")
                if uid:
                    auth_state["user_email"] = uid
            except Exception:
                pass

            save_auth_credentials(email, password)
            print(f"[PERSONA] ✅ Face verification complete. Authenticated as {auth_state['user_email']}")
            return jsonify({"success": True, "message": "Face verification complete!", "user_email": auth_state["user_email"]})

        elif resp.status_code == 401:
            # Face scan done but credentials wrong — shouldn't happen
            return jsonify({"success": False, "message": "Credentials rejected (401). Check email/password."}), 401

        elif resp.status_code == 403:
            # 403 = face scan not yet completed in the browser
            return jsonify({"success": False, "message": "Face scan not completed yet (403). Please finish the scan in the browser tab first, then click Verify."}), 403

        elif resp.status_code in [409, 410]:
            # 409/410 = inquiry expired or already used — generate fresh inquiry ID
            print(f"[PERSONA] Inquiry {api_url} returned HTTP {resp.status_code}. Generating fresh inquiry ID...")
            ok, msg, inq, purl = authenticate_brain_user(email, password)
            if ok:
                auth_pause_event.set()
                return jsonify({"success": True, "message": "Authenticated successfully.", "user_email": auth_state["user_email"]})
            return jsonify({
                "success": False,
                "requires_persona": True,
                "persona_url": purl,
                "message": f"Previous Face ID inquiry expired. Please scan using the fresh link."
            })


        else:
            return jsonify({"success": False, "message": f"Unexpected response from BRAIN: HTTP {resp.status_code} — {resp.text[:200]}"}), 400

    except Exception as e:
        return jsonify({"success": False, "message": f"Error completing face verification: {str(e)}"}), 500


def clean_single_expression(expr_str):
    if not expr_str:
        return ""
    s = str(expr_str).strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?", "", s).rstrip("`").strip()
    # Strip wrapping quotes or trailing/leading commas
    while len(s) > 1 and ((s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")) or s.startswith(",") or s.endswith(",")):
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            s = s[1:-1].strip()
        elif s.startswith(","):
            s = s[1:].strip()
        elif s.endswith(","):
            s = s[:-1].strip()
    return s

@app.route("/api/simulations/batch", methods=["POST"])
def enqueue_batch():
    data = request.get_json() or {}
    raw_expressions = data.get("expressions", [])
    settings = data.get("settings", {})
    # Auto-correct RAM neutralization (deprecated by WorldQuant BRAIN API)
    if settings.get("neutralization") == "RAM":
        settings["neutralization"] = "INDUSTRY"
        print(f"[BATCH] Auto-corrected RAM neutralization to INDUSTRY for region {settings.get('region')}")

    dry_run = data.get("dry_run", False) or settings.get("dry_run", False)
    auto_submit = data.get("auto_submit", False) or settings.get("auto_submit", False)
    
    expressions = []
    if isinstance(raw_expressions, str):
        raw_str = raw_expressions.strip()
        if raw_str.startswith("```"):
            raw_str = re.sub(r"^```(?:json)?", "", raw_str).rstrip("`").strip()
        if raw_str.startswith("["):
            try:
                parsed = json.loads(raw_str)
                if isinstance(parsed, list):
                    raw_expressions = parsed
            except Exception:
                pass
    
    if isinstance(raw_expressions, list):
        for item in raw_expressions:
            c = clean_single_expression(item)
            if c:
                expressions.append(c)
    else:
        for line in str(raw_expressions).splitlines():
            c = clean_single_expression(line)
            if c and not c.startswith("#"):
                expressions.append(c)
        
    if not expressions:
        return jsonify({"error": "No valid expressions provided"}), 400

    # Expand Multi-Universe and Multi-Neutralization selections if requested
    raw_univ = str(settings.get("universe", "TOP3000")).strip()
    if raw_univ == "ALL_UNIVERSES":
        target_universes = ["TOP3000", "TOP2000", "TOP1000", "TOP500", "TOP200"]
    elif "," in raw_univ:
        target_universes = [u.strip() for u in raw_univ.split(",") if u.strip()]
    else:
        target_universes = [raw_univ if raw_univ else "TOP3000"]

    target_neut = [settings.get("neutralization", "INDUSTRY")]
    if settings.get("neutralization") == "ALL_NEUT":
        target_neut = ["INDUSTRY", "SUBINDUSTRY", "SECTOR", "MARKET"]

    batch_id = f"BATCH_{int(time.time())}_{random.randint(1000, 9999)}"
    batch_item_records = []
    task_idx = 0

    for expr in expressions:
        for u in target_universes:
            for n in target_neut:
                item_settings = dict(settings)
                item_settings["universe"] = u
                item_settings["neutralization"] = n
                item_obj = {
                    "id": f"{batch_id}_{task_idx}",
                    "expression": expr,
                    "settings": item_settings,
                    "status": "QUEUED",
                    "dry_run": dry_run,
                    "auto_submit": auto_submit,
                    "result": None
                }
                batch_item_records.append(item_obj)
                task_idx += 1

    batch_job_record = {
        "batch_id": batch_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total": len(batch_item_records),
        "completed": 0,
        "progress": 0.0,
        "status": "RUNNING",
        "settings": settings,
        "dry_run": dry_run,
        "auto_submit": auto_submit,
        "items": batch_item_records
    }
    
    # 1. Register in batch_jobs FIRST under lock so worker threads find batch_id immediately
    with jobs_lock:
        batch_jobs[batch_id] = batch_job_record

    # 2. Push all items to job_queue
    for t_idx, item_obj in enumerate(batch_item_records):
        job_queue.put((batch_id, t_idx, item_obj))

    # 3. Save to disk in background thread to avoid blocking HTTP response
    threading.Thread(target=save_batch_jobs, daemon=True).start()
        
    return jsonify({
        "success": True,
        "batch_id": batch_id,
        "total_enqueued": len(expressions),
        "status": "RUNNING"
    })

@app.route("/api/simulations/cancel", methods=["POST"])
def cancel_batch():
    global cancel_event

    # 1. Signal all workers to skip pending jobs
    cancel_event.set()

    # 2. Drain the queue so workers don't pick up new items
    cancelled_count = 0
    while not job_queue.empty():
        try:
            job_queue.get_nowait()
            job_queue.task_done()
            cancelled_count += 1
        except Exception:
            break

    # 3. Mark all running batches as CANCELLED
    with jobs_lock:
        for b_id, b_data in batch_jobs.items():
            if b_data.get("status") in ["RUNNING", "PENDING"]:
                b_data["status"] = "CANCELLED"
                b_data["end_time"] = datetime.now(timezone.utc).isoformat()
                for item in b_data.get("items", []):
                    if item.get("status") in ["QUEUED", "SIMULATING"]:
                        item["status"] = "CANCELLED"
        save_batch_jobs()

    # 4. Reset all slots to IDLE
    with slot_lock:
        for sid in slot_status:
            slot_status[sid].update({
                "status": "IDLE", "expression": None,
                "batch_id": None, "item_index": None, "start_time": None
            })

    # 5. Clear cancel flag so new batches can run
    cancel_event.clear()

    return jsonify({"success": True, "message": f"Cancelled queue and stopped all {cancelled_count} pending jobs. All 8 slots now idle."})

@app.route("/api/simulations/cancel/item", methods=["POST"])
def cancel_single_item():
    """Cancel a single queued item by batch_id + item_index."""
    data = request.get_json() or {}
    batch_id = data.get("batch_id")
    item_index = data.get("item_index")
    if batch_id is None or item_index is None:
        return jsonify({"success": False, "error": "batch_id and item_index required"}), 400
    item_index = int(item_index)
    with jobs_lock:
        if batch_id not in batch_jobs:
            return jsonify({"success": False, "error": "Batch not found"}), 404
        items = batch_jobs[batch_id].get("items", [])
        if item_index >= len(items):
            return jsonify({"success": False, "error": "Item index out of range"}), 400
        item = items[item_index]
        if item["status"] in ["QUEUED", "SIMULATING"]:
            item["status"] = "CANCELLED"
            batch_jobs[batch_id]["completed"] += 1
            total = batch_jobs[batch_id]["total"]
            completed = batch_jobs[batch_id]["completed"]
            batch_jobs[batch_id]["progress"] = round((completed / total) * 100, 1)
            if completed == total:
                batch_jobs[batch_id]["status"] = "CANCELLED"
            save_batch_jobs()
            return jsonify({"success": True, "message": f"Item {item_index} in batch {batch_id} cancelled."})
        return jsonify({"success": False, "error": f"Item status is {item['status']}, cannot cancel"}), 400


@app.route("/api/settings/options", methods=["GET"])
def get_settings_options():
    """Return all available dropdown options for frontend settings."""
    return jsonify({
        "regions": ["USA", "GLB", "EUR", "ASI", "CHN", "KOR", "HKG", "IND", "DEU", "GBR"],
        "universes": ["TOP3000", "MINVOL1M", "MINVOL10M", "TOPDIV3000", "TOP2000", "TOP1000", "TOP500", "TOP200"],
        "neutralizations": [
            {"value": "NONE", "label": "None"},
            {"value": "RAM", "label": "RAM"},
            {"value": "STATISTICAL", "label": "Statistical"},
            {"value": "CROWDING", "label": "Crowding Factors"},
            {"value": "FAST", "label": "Fast Factors"},
            {"value": "SLOW", "label": "Slow Factors"},
            {"value": "MARKET", "label": "Market"},
            {"value": "SECTOR", "label": "Sector"},
            {"value": "INDUSTRY", "label": "Industry"},
            {"value": "SUBINDUSTRY", "label": "Subindustry"},
            {"value": "COUNTRY", "label": "Country / Region"},
            {"value": "SLOW_FAST", "label": "Slow + Fast Factors"}
        ],
        "delays": [0, 1],
        "languages": [
            {"value": "FASTEXPR", "label": "Fast Expression"},
            {"value": "PYTHON", "label": "Python"}
        ],
        "instrumentTypes": ["EQUITY"],
        "pasteurizations": ["ON", "OFF"],
        "nanHandlings": ["OFF", "ON"],
        "unitHandlings": ["VERIFY", "OFF"],
        "maxTrades": ["OFF", "ON"],
        "maxPositions": ["OFF", "ON"]
    })


@app.route("/api/simulations/slots", methods=["GET"])
def get_slots():
    with slot_lock:
        return jsonify(list(slot_status.values()))


@app.route("/api/alphas/<alpha_id>/submit", methods=["POST"])
def submit_single_alpha_route(alpha_id):
    """Manually submit a completed alpha to WorldQuant BRAIN for approval/production."""
    if not alpha_id or alpha_id.startswith("MOCK_"):
        return jsonify({"success": False, "error": "Cannot submit mock alpha ID"}), 400
    ok, msg = submit_alpha_to_brain(alpha_id)
    if ok:
        return jsonify({"success": True, "message": f"Alpha {alpha_id} submitted: {msg}"})
    return jsonify({"success": False, "error": f"Submission failed: {msg}"}), 400


@app.route("/api/reports/high-sharpe", methods=["GET"])
def get_high_sharpe_report():
    """Retrieve all high-Sharpe (>= 2.0) alphas with zero warnings saved in high_sharpe_zero_warnings.txt."""
    high_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "high_sharpe_zero_warnings.txt")
    if not os.path.exists(high_file):
        return jsonify({"exists": False, "count": 0, "content": "No high-Sharpe (>=2.0, 0 warnings) alphas saved yet."})
    try:
        with open(high_file, "r", encoding="utf-8") as f:
            content = f.read()
        count = content.count("Expression:")
        return jsonify({"exists": True, "count": count, "content": content})
    except Exception as e:
        return jsonify({"exists": False, "error": str(e)}), 500


@app.route("/api/reports/submitable", methods=["GET"])
def get_submitable_report():
    """Retrieve all submitable alphas saved in submitable_alphas.txt."""
    sub_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "submitable_alphas.txt")
    if not os.path.exists(sub_file):
        return jsonify({"exists": False, "count": 0, "content": "No submitable alphas saved yet."})
    try:
        with open(sub_file, "r", encoding="utf-8") as f:
            content = f.read()
        count = content.count("Expression:")
        return jsonify({"exists": True, "count": count, "content": content})
    except Exception as e:
        return jsonify({"exists": False, "error": str(e)}), 500


@app.route("/api/simulations/batch/<batch_id>/csv", methods=["GET"])
def download_batch_csv(batch_id):
    """Generate and return CSV file for a specific batch."""
    filepath = save_batch_csv(batch_id)
    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "Batch CSV not found"}), 404
    return send_file(filepath, as_attachment=True, download_name=f"batch_{batch_id}.csv")

@app.route("/api/simulations/batches", methods=["GET"])
def get_batches():
    with jobs_lock:
        summary_list = []
        for b_id, b_data in batch_jobs.items():
            if not isinstance(b_data, dict):
                continue
            simulating_count = sum(1 for item in b_data.get("items", []) if isinstance(item, dict) and item.get("status") == "SIMULATING")
            total = b_data.get("total", 0)
            completed = b_data.get("completed", 0)
            summary_list.append({
                "batch_id": b_id,
                "created_at": b_data.get("created_at", ""),
                "total": total,
                "completed": completed,
                "progress": b_data.get("progress", 0.0),
                "status": b_data.get("status", "UNKNOWN"),
                "dry_run": b_data.get("dry_run", False),
                "settings": b_data.get("settings", {}),
                "simulating_now": simulating_count,
                "queued_remaining": max(0, total - completed - simulating_count)
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
        
    session = get_brain_session()
    url = f"https://api.worldquantbrain.com/alphas/{alpha_id}/recordsets/pnl"
    try:
        resp = session.get(url, timeout=10)
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
    print(f"Starting WorldQuant BRAIN Batch Alpha Portal Server on port {port} (all network interfaces)...")
    app.run(host="0.0.0.0", port=port, debug=False)


