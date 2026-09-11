#!/usr/bin/env python3
"""
WorldQuant BRAIN Advanced Alpha Generator (Gradient-Driven Dual-Engine Mode)
Autonomously generates, simulates, logs, and evolves mathematical trading signals
using a Discrete Policy Gradient Engine to optimize dataset and operator selection.
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
COOKIE = "t=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJoQmxlaTdyaHB1TnBQWGEzTVBjMGN4eGxmazNmMjlsTCIsImV4cCI6MTc4NjA5NjMxMiwiYW1yIjpbInB3ZCIsImZhY2UiLCJjYXB0Y2hhIl19.5jcWSd5ldqmlWg00ejT2NJGSvAgQ1drES2QwTJEWC1M; __zlcmid=1Yqohr8bEhL7s7v; cookieyes-consent=consentid:a1RDUElydWNOTEtyWFB4NHNubFI2dlNoZ291VWFIV0s,consent:no,action:yes,necessary:yes,functional:no,analytics:no,performance:no,advertisement:no,other:no"

# Categorized Premium Dataset Pool
CATEGORIZED_FIELDS = {
    "HIDDEN_EDGE": [
        "anl4_basicqfv4_actual",
        "adj_net_income_median",
        "anl4_afv4_div_high"
    ],
    "ALTERNATIVE": [
        "sentiment_score_news", "news_volume_historical", "put_call_ratio_options",
        "short_interest_pct_shares", "sentiment_buzz_weekly", "implied_volatility_call_270",
        "implied_volatility_put_270", "news_sentiment_score", "options_volume_flow",
        "short_interest_shares_outstanding", "short_interest_ratio", "news_sentiment_momentum",
        "social_sentiment_buzz", "institutional_flow_sentiment", "block_trade_options_flow"
    ],
    "PROFITABILITY": [
        "abnormal_return_earnings_release", "cash_earnings_return_on_equity",
        "consensus_analyst_rating", "domestic_ebit_value", "earnings_expectation_module_score",
        "earnings_momentum_analyst_score", "earnings_momentum_composite_score", "ebit", "ebitda",
        "fcf_yield_multiplied_forward_roe", "fcf_yield_times_forward_roe",
        "gross_profit_margin_ttm_2", "gross_profit_to_assets_ratio", "eps",
        "coefficient_variation_fy1_eps", "coefficient_variation_fy2_eps", "earnings_shortfall_metric"
    ],
    "LEVERAGE": [
        "current_liabilities_to_price", "current_liabilities_to_price_v1", "debt",
        "debt_carrying_amount_total", "debt_carrying_value", "debt_lt",
        "debt_maturities_repayments_next12m", "debt_maturities_repayments_year2",
        "debt_principal_due_year_five", "debt_repayment_year_three", "debt_repayments_total",
        "debt_st", "credit_facility_max_borrowing", "credit_facility_outstanding_amount",
        "distress_risk_measure", "employee_compensation_benefit_liabilities",
        "liquidity_cash_to_liabilities_ratio", "assets", "assets_curr",
        "debt_stated_interest_rate_pct", "anl4_adjusted_netincome_ft", 
        "anl4_ebit_value", "anl4_ebitda_value", "anl4_netprofit_value", "actual_eps_value_quarterly"
    ],
    "GROWTH": [
        "asset_growth_rate", "asset_growth_rate_sensitivityfactor", "change_in_eps_surprise",
        "earnings_revision_magnitude", "five_year_eps_stability", "five_year_eps_trend_r_squared_2",
        "forward_two_year_eps_growth_rate", "fundamental_growth_module_score",
        "long_term_earnings_growth_forecast", "long_term_growth_estimate",
        "high_low_eps_revision_sum", "sales_estimate_count", "earnings_per_share_estimate_count", 
        "anl4_afv4_eps_mean"
    ],
    "EFFICIENCY": [
        "capex", "capex_to_depreciation_linkage", "capex_to_total_assets", "cogs",
        "cash_burn_rate", "cash_burn_rate_v1", "current_ratio", "depre_amort", "employee",
        "inventory_change_avg_assets", "fnd6_newqeventv110_cogsq"
    ],
    "VALUATION": [
        "bookvalue_ps", "enterprise_value", "enterprise_value_weighted_value_score", "equity",
        "equity_value_score", "forward_book_value_to_price", "forward_cash_flow_to_price",
        "forward_ebitda_to_enterprise_value_2", "forward_sales_to_price",
        "income_statement_value_score", "inverse_peg_earnings_growth", "inverse_peg_ratio",
        "inverse_peg_ratio_emmodel", "lagged_inverse_peg_ratio"
    ]
}

# Rebuilt Tiered Fundamental Data Dictionary
FUNDAMENTAL_DATA = {"TIER_1": [], "TIER_2": [], "TIER_3": [], "TIER_4": [], "HIDDEN_EDGE": []}

TIER_1_POOL = []
TIER_2_POOL = []
TIER_3_POOL = []
TIER_4_POOL = []
HIDDEN_EDGE_POOL = []
DATASET_POOL = []
FAST_DATA = ["volume", "vwap", "returns", "close", "open", "high", "low", "cap"]
DATASET_USAGE_TRACKER = {}

def wrap_dataset_by_tier(field):
    """
    If the dataset is in FAST_DATA, it must remain raw.
    Only wrap the dataset in ts_backfill if it is a fundamental field.
    """
    if field in FAST_DATA:
        return field
    return f"ts_backfill({field}, 60)"

def initialize_dataset_tracker_from_csv():
    global DATASET_USAGE_TRACKER
    csv_file = "simulation_results.csv"
    if not os.path.exists(csv_file): return
    try:
        with open(csv_file, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Status") == "SUCCESS":
                    code = row.get("Code")
                    if code:
                        comps = get_alpha_components(code)
                        for comp in comps:
                            if comp in DATASET_POOL:
                                DATASET_USAGE_TRACKER[comp] = DATASET_USAGE_TRACKER.get(comp, 0) + 1
    except Exception:
        pass

def initialize_data_tiers():
    global FUNDAMENTAL_DATA, TIER_1_POOL, TIER_2_POOL, TIER_3_POOL, TIER_4_POOL, HIDDEN_EDGE_POOL, DATASET_POOL
    t2_keywords = ['growth', 'stability', 'trend', 'revision', 'momentum', 'expectation', 'surprise', 'rating', 'score']
    
    t1_set, t2_set, t3_set, t4_set, hidden_set = set(), set(), set(), set(), set()
    
    for cat, fields in CATEGORIZED_FIELDS.items():
        for field in fields:
            fl = field.lower()
            if cat == 'HIDDEN_EDGE':
                hidden_set.add(field)
                continue
            if cat == 'ALTERNATIVE':
                t4_set.add(field)
                continue
            is_t2 = False
            if cat == 'GROWTH':
                is_t2 = True
            else:
                if any(k in fl for k in t2_keywords):
                    is_t2 = True
                    
            if is_t2: t2_set.add(field)
            elif cat == 'OTHER_FUNDAMENTAL': t3_set.add(field)
            else: t1_set.add(field)
            
    FUNDAMENTAL_DATA["TIER_1"] = sorted(list(t1_set))
    FUNDAMENTAL_DATA["TIER_2"] = sorted(list(t2_set))
    FUNDAMENTAL_DATA["TIER_3"] = sorted(list(t3_set))
    FUNDAMENTAL_DATA["TIER_4"] = sorted(list(t4_set))
    FUNDAMENTAL_DATA["HIDDEN_EDGE"] = sorted(list(hidden_set))
    
    TIER_1_POOL, TIER_2_POOL, TIER_3_POOL, TIER_4_POOL, HIDDEN_EDGE_POOL = FUNDAMENTAL_DATA["TIER_1"], FUNDAMENTAL_DATA["TIER_2"], FUNDAMENTAL_DATA["TIER_3"], FUNDAMENTAL_DATA["TIER_4"], FUNDAMENTAL_DATA["HIDDEN_EDGE"]
    
    DATASET_POOL = sorted(list(set(TIER_1_POOL + TIER_2_POOL + TIER_3_POOL + TIER_4_POOL + HIDDEN_EDGE_POOL)), key=len, reverse=True)

# ==============================================================================
# DISCRETE POLICY GRADIENT ENGINE (REINFORCEMENT LEARNING)
# ==============================================================================

class GradientEngine:
    def __init__(self, learning_rate=0.15):
        self.lr = learning_rate
        # Initialize all datasets and operators with an equal starting weight of 1.0
        self.ds_weights = {}
        self.op_weights = {op: 1.0 for op in ["ts_delta", "ts_corr", "rank", "zscore", "sign", "divide", "multiply", "ts_rank", "group_neutralize", "if_else", "trade_when"]}
        
    def initialize_pools(self):
        for ds in DATASET_POOL + FAST_DATA:
            self.ds_weights[ds] = 1.0
            
    def get_weighted_choice(self, pool_list):
        """Picks an item from the provided list based on its learned probability weight."""
        if not pool_list: return None
        sub_dict = {k: self.ds_weights.get(k, 1.0) for k in pool_list}
        items = list(sub_dict.keys())
        weights = list(sub_dict.values())
        return random.choices(items, weights=weights, k=1)[0]
        
    def calculate_gradient_step(self, alpha_string, new_sharpe, old_sharpe):
        """
        The Optimizer: Applies the delta reward/penalty to the components.
        W_new = W_old + (Learning_Rate * Delta_Sharpe)
        """
        delta_sharpe = new_sharpe - old_sharpe
        # Clip the gradient to prevent weights from exploding to infinity
        reward = max(min(delta_sharpe, 2.0), -1.0) * self.lr
        
        for ds in self.ds_weights:
            if ds in alpha_string:
                self.ds_weights[ds] = max(0.05, self.ds_weights[ds] + reward)
                
        for op in self.op_weights:
            if op in alpha_string:
                self.op_weights[op] = max(0.05, self.op_weights[op] + reward)
                
    def print_top_weights(self):
        """Displays the AI's current highest-confidence components."""
        top_ds = sorted(self.ds_weights.items(), key=lambda x: x[1], reverse=True)[:3]
        top_op = sorted(self.op_weights.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"🧠 Gradient Engine Beliefs | Top Data: {[x[0] for x in top_ds]} | Top Ops: {[x[0] for x in top_op]}")

# Initialize globally
optimizer = GradientEngine(learning_rate=0.2)

# ==============================================================================
# ROUTING & GENERATOR FUNCTIONS
# ==============================================================================

def get_alpha_components(code):
    datasets = set()
    for ds in DATASET_POOL + FAST_DATA:
        if re.search(r'\b' + re.escape(ds) + r'\b', code):
            datasets.add(ds)
    operators = set()
    known_operators = ["ts_backfill", "zscore", "rank", "signed_power", "log", "ts_decay_linear", "group_neutralize", "normalize", "ts_mean", "ts_std_dev", "ts_delta", "ts_delay", "ts_rank", "ts_corr", "if_else", "abs", "sign", "scale", "bucket", "trade_when"]
    for op in known_operators:
        if re.search(r'\b' + re.escape(op) + r'\b', code):
            operators.add(op)
    return datasets.union(operators)

def get_historical_alphas():
    """Reads simulation_results.csv and returns a list of dictionaries with alpha details."""
    csv_file = "simulation_results.csv"
    if not os.path.exists(csv_file):
        return []
    alphas = []
    try:
        with open(csv_file, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                status = row.get("Status")
                code = row.get("Code")
                sharpe_str = row.get("Sharpe")
                if not code or not status:
                    continue
                try:
                    sharpe = float(sharpe_str) if sharpe_str else 0.0
                except ValueError:
                    sharpe = 0.0
                alphas.append({
                    "code": code,
                    "status": status,
                    "sharpe": sharpe
                })
    except Exception as e:
        print(f"Error reading CSV logs: {e}")
    return alphas

def pretrain_gradient_engine(optimizer, historical_alphas):
    """Warm-starts the gradient engine weights using successful historical alphas from the CSV."""
    print("⚙️ Warm-Starting Gradient Engine from historical CSV data...")
    count = 0
    for alpha in historical_alphas:
        if alpha.get("status") == "SUCCESS":
            sharpe = alpha.get("sharpe", 0.0)
            if sharpe > 1.0:
                code = alpha.get("code")
                if code:
                    # Extract datasets and operators
                    get_alpha_components(code)
                    optimizer.calculate_gradient_step(alpha_string=code, new_sharpe=sharpe, old_sharpe=1.0)
                    count += 1
    print(f"✅ Pre-trained optimizer on {count} successful historical alphas (Sharpe > 1.0).")

def is_cross_correlated(code, history_buffer):
    if not history_buffer: return False, 0.0, None
    new_comps = get_alpha_components(code)
    if not new_comps: return False, 0.0, None
    for hist_code in history_buffer:
        hist_comps = get_alpha_components(hist_code)
        if not hist_comps: continue
        intersection = new_comps.intersection(hist_comps)
        sim_new = len(intersection) / len(new_comps) if len(new_comps) > 0 else 0.0
        sim_hist = len(intersection) / len(hist_comps) if len(hist_comps) > 0 else 0.0
        max_sim = max(sim_new, sim_hist)
        if max_sim > 0.70: return True, max_sim, hist_code
    return False, 0.0, None

def wrap_in_rank(expr):
    expr = expr.strip()
    if expr.startswith("rank(") and expr.endswith(")"): return expr
    return f"rank({expr})"

# --- Engine 1: Event-Driven ---
def generate_event_driven_alpha(recent_datasets=None):
    """Generates signals that only trade during specific market events (trade_when)."""
    conditions = [
        "volume > (ts_mean(volume, 20) * 1.5)",
        "ts_std_dev(returns, 10) > 0.04",
        "abs(returns) > (ts_std_dev(returns, 20) * 2.0)",
        "(close - open) / (open + 1e-9) < -0.02"
    ]
    condition = random.choice(conditions)
    rare_ds = optimizer.get_weighted_choice(DATASET_POOL)
    target_expr = f"rank(zscore({wrap_dataset_by_tier(rare_ds)}))"
    
    expr = f"trade_when({condition}, {target_expr}, -1)"
    group = random.choice(['bucket(rank(cap), range="0, 1, 0.1")', 'bucket(rank(ts_mean(volume, 20)), range="0, 1, 0.1")'])
    expr = f"group_neutralize({wrap_in_rank(expr)}, {group})"
    
    return f"normalize(ts_decay_linear({expr}, {random.choice([0, 1, 2])}))"

# --- Engine 2: Vector / Regime Switching ---
def generate_vector_regime_alpha(recent_datasets=None):
    """Generates Regime-Switching alphas using if_else vector logic."""
    regime_condition = random.choice([
        "returns > 0",
        "ts_mean(volume, 5) > ts_mean(volume, 20)",
        "ts_std_dev(returns, 20) > 0.03"
    ])
    ds1 = optimizer.get_weighted_choice(DATASET_POOL)
    ds2 = optimizer.get_weighted_choice([d for d in DATASET_POOL if d != ds1])
    
    vector_block = f"if_else({regime_condition}, rank({wrap_dataset_by_tier(ds1)}), rank({wrap_dataset_by_tier(ds2)}))"
    bucket = random.choice(['bucket(rank(cap), range="0, 1, 0.1")', 'bucket(rank(ts_mean(volume, 20)), range="0, 1, 0.1")'])
    alpha = f"group_neutralize({vector_block}, {bucket})"
    
    return f"normalize(ts_decay_linear({alpha}, {random.choice([2, 5, 8])}))"

# --- Engine 3: Intelligent Fundamental ---
def generate_intelligent_fundamental_alpha():
    """Builds a specific ratio*trend block using the Gradient Optimizer's learned weights."""
    fund_ds_1 = optimizer.get_weighted_choice(HIDDEN_EDGE_POOL + TIER_1_POOL)
    fund_ds_2 = optimizer.get_weighted_choice(HIDDEN_EDGE_POOL + TIER_1_POOL)
    fast_ds = optimizer.get_weighted_choice(FAST_DATA)
    
    ratio_block = f"({wrap_dataset_by_tier(fund_ds_1)} / ({fast_ds} + 1e-5))"
    trend_window = random.choice([20, 60, 90])
    trend_block = f"sign(ts_delta({wrap_dataset_by_tier(fund_ds_2)}, {trend_window}))"
    
    core_signal = f"rank({ratio_block} * {trend_block})"
    bucket = random.choice(['bucket(rank(cap), range="0, 1, 0.1")', 'bucket(rank(volume), range="0, 1, 0.1")'])
    alpha = f"group_neutralize({core_signal}, {bucket})"
    
    return f"normalize(ts_decay_linear({alpha}, {random.choice([3, 6, 10])}))"

# --- Master Generation Router ---
def generate_alpha_expression(recent_datasets=None, history_buffer=None, universe="TOP3000"):
    """Routes generation requests to specialized sub-engines to guarantee structural diversity."""
    dice = random.random()
    if dice < 0.20:
        return generate_event_driven_alpha(recent_datasets)
    elif dice < 0.40:
        return generate_vector_regime_alpha(recent_datasets)
    elif dice < 0.70:
        return generate_intelligent_fundamental_alpha()
        
    # Standard Contrarian Fallback
    fundamental_field = optimizer.get_weighted_choice(DATASET_POOL)
    fast_field = optimizer.get_weighted_choice(FAST_DATA)
    expr = f"rank(ts_rank({wrap_dataset_by_tier(fundamental_field)}, 90)) - rank(ts_rank({fast_field}, 20))"
    group = random.choice(['bucket(rank(cap), range="0, 1, 0.1")', 'bucket(rank(ts_mean(volume, 20)), range="0, 1, 0.1")'])
    expr = f"group_neutralize({wrap_in_rank(expr)}, {group})"
    return f"normalize(ts_decay_linear({expr}, {random.choice([2, 5, 8])}))"

# ==============================================================================
# EXECUTION & POLLING
# ==============================================================================

def simulate_alpha(expression, session, headers, settings, dry_run=False):
    universe = settings.get("universe", "TOP3000")
    decay = settings.get("decay", 2)
    if decay == -1: decay = random.choice([0, 2, 4, 8])
        
    if dry_run:
        time.sleep(1)
        return {
            "status": "SUCCESS" if random.random() < 0.7 else "FAILED",
            "metrics": {"sharpe": random.uniform(0.5, 2.2), "fitness": random.uniform(0.5, 2.2), "returns": random.uniform(-0.1, 0.3), "drawdown": -0.05, "margin": 0.0002, "turnover": 0.1},
            "failed_checks": [], "universe": universe, "decay": decay
        }
            
    payload = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": settings.get("instrumentType", "EQUITY"),
            "region": settings.get("region", "USA"), "universe": universe,
            "delay": settings.get("delay", 1), "decay": decay,
            "neutralization": settings.get("neutralization", "NONE"),
            "truncation": settings.get("truncation", 0.08), "pasteurization": settings.get("pasteurization", "ON"),
            "nanHandling": settings.get("nanHandling", "OFF"), "language": "FASTEXPR", "visualization": False
        },
        "regular": expression
    }
    
    try:
        resp = session.post("https://api.worldquantbrain.com/simulations", json=payload, headers=headers)
        if resp.status_code == 429:
            time.sleep(60)
            return {"status": "HTTP_429", "error": "Rate limit", "universe": universe, "decay": decay}
        if resp.status_code not in [201, 202]:
            return {"status": f"HTTP_{resp.status_code}", "error": resp.text, "universe": universe, "decay": decay}
    except Exception as e:
        return {"status": "CONN_ERROR", "error": str(e), "universe": universe, "decay": decay}
            
    status_url = "https://api.worldquantbrain.com" + resp.headers.get("Location", "")
    for poll_count in range(150):
        try:
            poll_resp = session.get(status_url, headers=headers)
            if poll_resp.status_code == 429:
                time.sleep(30); continue
            data = poll_resp.json()
            status = data.get("status")
            if status in ["COMPLETE", "COMPLETED"]:
                # Metrics Extraction
                metrics = data.get("is") or data.get("results", {}).get("is") or data.get("alpha", {}).get("is")
                return {"status": "SUCCESS", "metrics": metrics, "failed_checks": [], "universe": universe, "decay": decay}
            elif status in ["FAILED", "ERROR"]:
                failed_checks = ["INCOMPATIBLE_UNIT"] if "unit" in str(data).lower() else []
                if "self" in str(data).lower() and "corr" in str(data).lower(): failed_checks.append("SELF_CORRELATION")
                return {"status": status, "error": data.get("message", ""), "failed_checks": failed_checks, "universe": universe, "decay": decay}
            time.sleep(3 if poll_count < 15 else 10)
        except Exception:
            time.sleep(5)
            
    return {"status": "TIMEOUT", "error": "Max polling reached", "universe": universe, "decay": decay}

def log_attempt(status, metrics, failed_checks, universe, decay, code, settings=None):
    csv_file = "simulation_results.csv"
    file_exists = os.path.exists(csv_file)
    try:
        with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Status", "Sharpe", "Fitness", "Returns(%)", "Drawdown(%)", "Margin(bps)", "Turnover(%)", "Universe", "Delay", "Decay", "Neutralization", "FailedChecks", "Code"])
            
            s_val = metrics.get("sharpe", "") if metrics else ""
            f_val = metrics.get("fitness", "") if metrics else ""
            checks_str = ";".join(failed_checks) if failed_checks else ""
            writer.writerow([status, s_val, f_val, "", "", "", "", universe, settings.get("delay", 1), decay, settings.get("neutralization", "NONE"), checks_str, code])
    except Exception as e:
        print(f"Failed to log to CSV: {e}")

# ==============================================================================
# MAIN COORDINATION LOOP
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Gradient-Driven Alpha Generator")
    parser.add_argument("--dry-run", action="store_true", help="Run offline dry-run mode")
    parser.add_argument("--iterations", type=int, default=0, help="Loop limit")
    args = parser.parse_args()
    
    print("=" * 60)
    print(" WORLDQUANT BRAIN - GRADIENT MUTATION ENGINE LAUNCHED ")
    print("=" * 60)
    
    session = requests.Session()
    cookie_str = COOKIE
    headers = {"Cookie": cookie_str, "Content-Type": "application/json"}
    token = next((p[2:] for p in cookie_str.split(";") if p.strip().startswith("t=")), None)
    if token: headers["Authorization"] = f"Bearer {token}"
    
    initialize_data_tiers()
    initialize_dataset_tracker_from_csv()
    optimizer.initialize_pools()
    alphas = get_historical_alphas()
    pretrain_gradient_engine(optimizer, alphas)
    optimizer.print_top_weights()
    
    sim_settings = {"universe": "TOP3000", "delay": 1, "decay": -1, "neutralization": "NONE"}
    previous_sharpe = 0.0
    loop_count = 0
    
    while True:
        loop_count += 1
        if args.iterations > 0 and loop_count > args.iterations: break
            
        print(f"\n--- Gradient Cycle #{loop_count} ---")
        code = generate_alpha_expression(universe=sim_settings["universe"])
        print(f"✨ [GENERATION] Code: {code}")
        
        result = simulate_alpha(code, session, headers, sim_settings, dry_run=args.dry_run)
        status = result["status"]
        metrics = result.get("metrics", {})
        
        if status == "SUCCESS" and metrics:
            current_sharpe = float(metrics.get("sharpe", 0))
            print(f"📈 Result: SUCCESS | Sharpe: {current_sharpe:.4f} | Fitness: {float(metrics.get('fitness', 0)):.4f}")
            
            # Policy Gradient Update: Reward components that improved the Sharpe
            optimizer.calculate_gradient_step(alpha_string=code, new_sharpe=current_sharpe, old_sharpe=previous_sharpe)
            optimizer.print_top_weights()
            previous_sharpe = current_sharpe
            
        else:
            print(f"❌ Result: {status} | Info: {result.get('error', 'Failed Check')} | {result.get('failed_checks', [])}")
            # Policy Gradient Update: Penalize failed runs
            optimizer.calculate_gradient_step(alpha_string=code, new_sharpe=-1.0, old_sharpe=previous_sharpe)
            
        log_attempt(status, metrics, result.get("failed_checks", []), result["universe"], result["decay"], code, settings=sim_settings)
        time.sleep(2)

if __name__ == "__main__":
    main()