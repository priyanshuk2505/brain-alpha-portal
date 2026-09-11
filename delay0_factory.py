import requests
import json
import time
import random
import os
import csv

# ---------------------------------------------------------
# 1. CONFIGURATION & AUTHENTICATION
#    Paste your fresh cookie here when it expires
# ---------------------------------------------------------
COOKIE = "_fbp=fb.1.1778595947954.838983336151760867; _ga=GA1.1.687920460.1778595944; _ga_9RN6WVT1K1=GS2.1.s1780805757$o78$g1$t1780805827$j55$l0$h0; _rdt_uuid=1778595944372.55b2243d-1bc9-440f-a27d-c17c7e25a64c; t=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIxYmlqWThkZHVOakhHdjlzelpYd2t0RXJPQ1NMNFBuZiIsImV4cCI6MTc4MDgyMDIxNiwiYW1yIjpbInB3ZCIsImZhY2UiLCJjYXB0Y2hhIl19.j8MhvLiiQNmTLxk53UstRSNZTgghA1gT6oMUbV8eZVo; _gcl_au=1.1.326319197.1778595941.1789914189.1780763836.1780764504; _ga_FXKNEPLB1N=GS2.1.s1779733566$o7$g0$t1779733566$j60$l0$h0; __zlcmid=1XcoWMCkz0Gybrj; cookieyes-consent=consentid:V3N1Q1lGeXMxZWJjQU5ienR2TEtiUnlGMTdIN3k3cFA,consent:yes,action:yes,necessary:yes,functional:yes,analytics:yes,performance:yes,advertisement:yes,other:yes"
HEADERS = {
    "Content-Type": "application/json",
    "Cookie": COOKIE,
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
}

# ---------------------------------------------------------
# 2. DELAY 0 DATASET POOLS  (Rule 1)
#    No quarterly data, no ts_backfill, only these 4 pools
# ---------------------------------------------------------
FAST_SENTIMENT = [
    "nws18_qep_fast_d1",
    "snt_social_volume_fast_d1",
    "event_novelty_score_2",
    "nws18_bee_fast_d1"
]

OPTIONS_FLOW = [
    "pcr_vol_10",
    "implied_volatility_mean_skew_10",
    "option_breakeven_10"
]

RISK_REGIMES = [
    "parkinson_volatility_10",
    "unsystematic_risk_last_30_days",
    "beta_last_30_days_spy"
]

CORE_PRICE = [
    "open", "close", "high", "low",
    "vwap", "volume", "returns", "cap"
]

DATASET_POOL = FAST_SENTIMENT + OPTIONS_FLOW + RISK_REGIMES + CORE_PRICE

# ---------------------------------------------------------
# 3. PURE QUANTITATIVE BUCKETS  (Rule 4 — no sector/industry)
# ---------------------------------------------------------
BUCKETS = [
    'bucket(rank(cap), range="0, 1, 0.1")',
    'bucket(rank(ts_mean(volume, 20)), range="0, 1, 0.1")'
]

# Intraday price action building blocks
INTRADAY_CORES = [
    "((close - open) / (open + 1e-9))",
    "((close - vwap) / (vwap + 1e-9))",
    "((high - low)  / (vwap + 1e-9))",
    "((vwap - open) / (open + 1e-9))",
    "((close - high) / (high + 1e-9))"
]

# Regime thresholds for if_else conditions
REGIME_THRESHOLDS = {
    "parkinson_volatility_10":        [0.03, 0.05, 0.08, 0.12],
    "unsystematic_risk_last_30_days": [0.10, 0.20, 0.30],
    "beta_last_30_days_spy":          [0.80, 1.00, 1.20, 1.50]
}

# ---------------------------------------------------------
# 4. GRADIENT ENGINE  (Rule 2)
#    Tracks dataset & model weights via delta-Sharpe updates.
#    Persists to gradient_state_d0.json across runs.
# ---------------------------------------------------------
GRADIENT_STATE_FILE = "gradient_state_d0.json"
LEARNING_RATE       = 0.05
WEIGHT_CLIP         = 5.0

def load_gradient_state():
    weights = {ds: 0.0 for ds in DATASET_POOL}
    model_weights = {
        "intraday_structural": 0.0,
        "event_driven":        0.0,
        "regime_switching":    0.0
    }
    if os.path.exists(GRADIENT_STATE_FILE):
        try:
            with open(GRADIENT_STATE_FILE, "r") as f:
                state = json.load(f)
            for k, v in state.get("dataset_weights", {}).items():
                if k in weights:
                    weights[k] = float(v)
            for k, v in state.get("model_weights", {}).items():
                if k in model_weights:
                    model_weights[k] = float(v)
        except Exception:
            pass
    return weights, model_weights

def save_gradient_state(weights, model_weights):
    try:
        with open(GRADIENT_STATE_FILE, "w") as f:
            json.dump({"dataset_weights": weights, "model_weights": model_weights}, f, indent=2)
    except Exception:
        pass

def softmax_sample(weight_dict):
    import math
    keys  = list(weight_dict.keys())
    vals  = [weight_dict[k] for k in keys]
    max_v = max(vals)
    exps  = [math.exp(v - max_v) for v in vals]
    total = sum(exps)
    probs = [e / total for e in exps]
    return random.choices(keys, weights=probs, k=1)[0]

def gradient_update(weights, model_weights, dataset, model_type, delta_sharpe):
    if dataset in weights:
        weights[dataset] = max(-WEIGHT_CLIP, min(WEIGHT_CLIP,
            weights[dataset] + LEARNING_RATE * delta_sharpe))
    if model_type in model_weights:
        model_weights[model_type] = max(-WEIGHT_CLIP, min(WEIGHT_CLIP,
            model_weights[model_type] + LEARNING_RATE * delta_sharpe))
    save_gradient_state(weights, model_weights)

# Load state once at startup
DS_WEIGHTS, MODEL_WEIGHTS = load_gradient_state()

# Rolling EMA baseline for REINFORCE advantage
_baseline = 0.0
def update_baseline(sharpe):
    global _baseline
    _baseline = 0.90 * _baseline + 0.10 * sharpe
    return _baseline

# ---------------------------------------------------------
# 5. THREE-MODEL GENERATION ROUTER  (Rule 3)
# ---------------------------------------------------------

def _maybe_smooth(expr):
    """Optionally wrap in ts_decay_linear or ts_mean — window capped at 1-3."""
    if random.random() < 0.40:
        win = random.choice([1, 2, 3])
        op  = random.choice(["ts_decay_linear", "ts_mean"])
        return f"{op}({expr}, {win})"
    return expr

# --- Model A: Intraday Structural ---
def generate_intraday_structural():
    core     = random.choice(INTRADAY_CORES)
    amp_pool = {k: DS_WEIGHTS[k] for k in FAST_SENTIMENT + OPTIONS_FLOW}
    amp_ds   = softmax_sample(amp_pool)
    op       = random.choice(["rank", "zscore"])

    if random.random() < 0.25:
        amp2 = random.choice([d for d in FAST_SENTIMENT + OPTIONS_FLOW if d != amp_ds])
        body = f"({op}({amp_ds}) + rank({amp2})) * rank({core})"
    else:
        body = f"{op}({amp_ds}) * rank({core})"

    body   = _maybe_smooth(body)
    bucket = random.choice(BUCKETS)
    expr   = f"group_neutralize({body}, {bucket})"
    if random.random() > 0.5:
        expr = f"-{expr}"
    return expr, amp_ds, "intraday_structural"

# --- Model B: Event-Driven (trade_when) ---
def generate_event_driven():
    trig_pool = {k: DS_WEIGHTS[k] for k in FAST_SENTIMENT}
    trig_ds   = softmax_sample(trig_pool)
    spike_win = random.choice([5, 10, 15, 20])
    mult      = random.choice([1.5, 2.0, 2.5, 3.0])
    condition = f"{trig_ds} > ts_mean({trig_ds}, {spike_win}) * {mult}"

    sig_pool  = {k: DS_WEIGHTS[k] for k in OPTIONS_FLOW + FAST_SENTIMENT}
    sig_ds    = softmax_sample(sig_pool)
    signal    = f"rank(zscore({sig_ds}))"

    expr      = f"trade_when({condition}, {signal}, -1)"
    expr      = _maybe_smooth(expr)
    bucket    = random.choice(BUCKETS)
    expr      = f"group_neutralize({expr}, {bucket})"
    return expr, trig_ds, "event_driven"

# --- Model C: Regime-Switching (if_else) ---
def generate_regime_switching():
    reg_pool  = {k: DS_WEIGHTS[k] for k in RISK_REGIMES}
    regime_ds = softmax_sample(reg_pool)
    threshold = random.choice(REGIME_THRESHOLDS[regime_ds])
    op        = random.choice([">", "<"])
    condition = f"{regime_ds} {op} {threshold}"

    true_opts = [
        "rank((close - open) / (open + 1e-9))",
        "rank((close - vwap) / (vwap + 1e-9))",
        "rank(vwap / (close + 1e-9))",
        "zscore(high - low)"
    ]
    false_ds  = random.choice(FAST_SENTIMENT + OPTIONS_FLOW)
    true_expr  = random.choice(true_opts)
    false_expr = f"rank({false_ds})"

    expr      = f"if_else({condition}, {true_expr}, {false_expr})"
    expr      = _maybe_smooth(expr)
    bucket    = random.choice(BUCKETS)
    expr      = f"group_neutralize({expr}, {bucket})"
    return expr, regime_ds, "regime_switching"

def generate_delay0_alpha():
    """Router — picks model type from gradient policy."""
    model_type = softmax_sample(MODEL_WEIGHTS)
    if model_type == "intraday_structural":
        return generate_intraday_structural()
    elif model_type == "event_driven":
        return generate_event_driven()
    else:
        return generate_regime_switching()

# ---------------------------------------------------------
# 6. MUTATE ALPHA  (Evolution Engine)
# ---------------------------------------------------------
def mutate_alpha(winning_code):
    new_code = winning_code
    r = random.random()

    if r < 0.25:
        # Swap neutralization bucket
        for b in BUCKETS:
            if b in new_code:
                other = [ob for ob in BUCKETS if ob != b]
                new_code = new_code.replace(b, random.choice(other), 1)
                break

    elif r < 0.50:
        # Mutate smoothing window (keep within 1-3)
        for win in ["3)", "2)", "1)"]:
            if win in new_code:
                other_wins = [w for w in ["1)", "2)", "3)"] if w != win]
                new_code = new_code.replace(win, random.choice(other_wins), 1)
                break
        else:
            smooth   = random.choice(["ts_decay_linear", "ts_mean"])
            win      = random.choice([1, 2, 3])
            new_code = f"{smooth}({new_code}, {win})"

    elif r < 0.75:
        # Flip sign
        if new_code.startswith("-"):
            new_code = new_code[1:]
        else:
            new_code = "-" + new_code

    else:
        # Swap a dataset from the pool
        for ds in random.sample(DATASET_POOL, len(DATASET_POOL)):
            if ds in new_code:
                swap_to  = random.choice([d for d in DATASET_POOL if d != ds])
                new_code = new_code.replace(ds, swap_to, 1)
                break

    return new_code

# ---------------------------------------------------------
# 7. SIMULATE ALPHA
#    Same Location-header pulse-poll loop as alpha_factory.py
#    delay=0 and universe=TOP3000 are HARDCODED (Rule 5)
# ---------------------------------------------------------
def simulate_alpha(expression):
    delay          = 0
    decay          = 0
    neutralization = "NONE"   # group_neutralize() is used inside the expression
    universe       = "TOP3000"

    url = "https://api.worldquantbrain.com/simulations"

    payload = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region":          "USA",
            "universe":        universe,
            "delay":           delay,
            "decay":           decay,
            "neutralization":  neutralization,
            "truncation":      0.08,
            "language":        "FASTEXPR",
            "nanHandling":     "OFF",
            "pasteurization":  "ON",
            "unitHandling":    "VERIFY",
            "visualization":   False
        },
        "regular": expression
    }

    wait_time = 60

    while True:
        try:
            response = requests.post(url, json=payload, headers=HEADERS)

            if response.status_code == 401:
                print("❌ ERROR: Cookie expired! Paste a new one at the top of delay0_factory.py")
                return None

            elif response.status_code == 429:
                print(f"⏳ Rate Limit Hit. Sleeping {wait_time}s then retrying...")
                time.sleep(wait_time)
                wait_time = min(wait_time * 2, 900)
                continue

            wait_time = 60

            loc = response.headers.get("Location")
            if not loc:
                return None
            status_url = loc if loc.startswith("http") else "https://api.worldquantbrain.com" + loc

            # Pulse-Polling Loop
            for attempt in range(1, 61):
                time.sleep(2 if attempt <= 15 else 10)
                data   = requests.get(status_url, headers=HEADERS).json()
                status = data.get("status")

                if status in ["COMPLETE", "FINISHED"]:
                    alpha   = data.get("alpha", {})
                    is_data = alpha.get("is", {})
                    return {
                        "sharpe":   is_data.get("sharpe",   0),
                        "fitness":  is_data.get("fitness",  0),
                        "returns":  is_data.get("returns",  0),
                        "drawdown": is_data.get("drawdown", 0),
                        "margin":   is_data.get("margin",   0),
                        "universe": universe,
                        "delay":    delay,
                        "decay":    decay
                    }

                if status in ["ERROR", "WARNING", "FAIL"]:
                    error_msg = data.get("message", data.get("error", "Unknown API Error"))
                    print(f"   ❌ WQ REJECTED: {error_msg}")
                    return None

            return None

        except Exception as e:
            print(f"Network Error: {e}")
            return None

# ---------------------------------------------------------
# 8. EVOLUTION MEMORY
# ---------------------------------------------------------
RESULTS_FILE = "simulation_results_d0.csv"
ELITE_FILE   = "elite_d0_alphas.txt"

def get_winning_DNA():
    """Read the CSV to find past winning Delay-0 alphas."""
    winners = []
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["Status"] == "SUCCESS" and abs(float(row["Sharpe"])) > 1.0:
                        winners.append(row["Code"])
        except Exception:
            pass
    return winners

# ---------------------------------------------------------
# 9. MAIN FACTORY LOOP
# ---------------------------------------------------------
print("=" * 60)
print("  DELAY 0 INTRADAY FACTORY  |  Universe: TOP3000  |  Delay: 0")
print("  Elite: Sharpe > 1.3  AND  Margin > 1.5 bps")
print("=" * 60)

if not os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, "w") as f:
        f.write("Status,Sharpe,Fitness,Returns(%),Drawdown(%),Margin(bps),Universe,Delay,Decay,Model,Code\n")

while True:
    winners = get_winning_DNA()

    # 50% Evolve a winner / 50% Generate fresh
    if len(winners) > 0 and random.random() > 0.5:
        parent     = random.choice(winners)
        code       = mutate_alpha(parent)
        model_type = "mutation"
        primary_ds = "N/A"
        print(f"\n🧠 EVOLUTION: Mutating winner -> {code}")
    else:
        code, primary_ds, model_type = generate_delay0_alpha()
        print(f"\n🎲 GENERATION [{model_type}] -> {code}")

    res = simulate_alpha(code)

    with open(RESULTS_FILE, "a") as f:
        if res is not None:
            sharpe      = res["sharpe"]
            fitness     = res["fitness"]
            returns_pct = res["returns"]  * 100
            dd_pct      = res["drawdown"] * 100
            margin_bps  = res["margin"]   * 10000

            f.write(
                f"SUCCESS,{sharpe},{fitness},{returns_pct:.2f},{dd_pct:.2f},"
                f"{margin_bps:.2f},{res['universe']},{res['delay']},{res['decay']},"
                f"{model_type},\"{code}\"\n"
            )
            print(f"   📊 Sharpe: {sharpe:.3f} | Fitness: {fitness:.3f} | Margin: {margin_bps:.2f} bps")

            # Gradient update (Rule 2)
            if model_type != "mutation":
                baseline     = update_baseline(sharpe)
                delta_sharpe = sharpe - baseline
                gradient_update(DS_WEIGHTS, MODEL_WEIGHTS, primary_ds, model_type, delta_sharpe)

            # Rule 5: Elite guard — Sharpe > 1.3 AND Margin > 1.5 bps
            if abs(sharpe) > 1.3 and margin_bps > 1.5:
                print(f"   🏆 ELITE ALPHA! Sharpe: {sharpe:.3f} | Margin: {margin_bps:.2f} bps")
                with open(ELITE_FILE, "a") as elite:
                    elite.write(
                        f"Sharpe: {sharpe:.3f} | Fit: {fitness:.3f} | "
                        f"Ret: {returns_pct:.2f}% | Margin: {margin_bps:.2f} bps | "
                        f"Model: {model_type} | Code: {code}\n"
                    )
        else:
            f.write(f"FAILED,0,0,0,0,0,TOP3000,0,0,{model_type},\"{code}\"\n")

    time.sleep(5)
