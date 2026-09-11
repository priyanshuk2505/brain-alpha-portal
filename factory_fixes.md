# Factory Fixes & Alpha Generation Changes

This document tracks all the surgical changes and improvements made to `alpha_factory.py` and `af2.py` during this pair-programming session to resolve portfolio self-correlation, API math errors, weight concentration, missing commas, and nested lookback window corruptions.

---

## 1. Fixed Missing Commas in `CATEGORIZED_FIELDS`
* **Problem**: Missing commas on lines 106 and 141 caused Python to implicitly concatenate adjacent string literals (e.g., `"debt_stated_interest_rate_pctanl4_adjusted_netincome_ft"` and `"mdl177_2_earningmomentumfactor400_rev6sales_estimate_count"`), resulting in invalid/unregistered dataset field names being simulated.
* **Fix**: Added the missing commas on both lines:
  - `"debt_stated_interest_rate_pct",` (line 106)
  - `"mdl177_2_earningmomentumfactor400_rev6",` (line 141)

---

## 2. Fixed Self-Correlation (Cap Smoothing)
* **Problem**: High-value decay windows (15, 30, 45, 60) caused excessive smoothing, leading to severe portfolio self-correlation and cross-correlation with existing elite alphas.
* **Fix**: Capped all `ts_decay_linear` windows to a maximum of `10`. All random decay window selection lists were changed to `[2, 3, 5, 8, 10]`, removing `15, 30, 45, 60` completely.
* **Functions Updated**:
  - `generate_alpha_expression`
  - `mutate_time_horizons`
  - `mutate_cross_domain_interaction`
  - `increase_decay_window`
  - Main loop `cycle_decay` settings

---

## 3. Fixed API Math Errors (Whitelisting & Stabilizing Operators)
* **Problem**: Unstable block types like `log_signed` (logarithm) and `relative_val` (division by ts_delay) caused `NaN`/`Infinity` execution crashes on sparse fundamental datasets.
* **Fix**: Removed `log_signed` and `relative_val` completely. Restrained the mathematical operators strictly to `rank`, `zscore`, `ts_delta`, and `ts_corr`.
* **Functions Updated**:
  - `generate_alpha_expression`: Removed `signed_power` and `log` from the core block generation.
  - `mutate_structure`: Restricted structural blocks to `"correlation"` (`ts_corr`) and `"delta"` (`ts_delta`).
  - `mutate_non_linear_wrap`: Replaced the unstable `signed_power` wrap with standard `rank` and `zscore` wraps.

---

## 4. Fixed Nested Lookback Window Corruption (Depth-Aware Parsing)
* **Problem**: Non-greedy regex window replacements (e.g. `re.sub(r'\b(ts_decay_linear)\((.+?),\s*(\d+)\)', ...)`) matched inner commas and parentheses of nested operators like `ts_backfill(field, 60)`. This corrupted `ts_backfill`'s lookback from `60` to `10` or `30`, triggering API validation errors.
* **Fix**: Introduced a parenthesis-depth parser `replace_operator_windows(code, target_funcs, window_replace_fn)` that scans the string character-by-character to locate target functions and only replaces the lookback/decay window when `paren_depth` is exactly `0` relative to that matched function call. Nested expressions like `ts_backfill(..., 60)` are left untouched.
* **Refactoring**: Ported all window-modifying functions to use this new parser:
  - `cap_decay_windows`
  - `mutate_time_horizons`
  - `mutate_time_horizon_shift`
  - `increase_decay_window`
  - `increase_lookback_window`

---

## 5. Fixed Concentrated Weight (Rank-Wrapping Neutralization)
* **Problem**: Heavy-tailed raw signals passed into `group_neutralize` directly caused highly concentrated portfolio weights, triggering the `CONCENTRATED_WEIGHT` failure check.
* **Fix**: Ensured the inner signal of *every* `group_neutralize` call is always wrapped in `rank()`.
* **Utility Added**: 
  - `wrap_in_rank(expr)`: Wraps an expression in `rank()` if not already wrapped, avoiding redundant nesting like `rank(rank(x))`.
  - `enforce_group_neutralize_rank(code)`: Recursively scans a full alpha code and wraps the first argument of all `group_neutralize` blocks in `rank()`.
* **Functions Updated**:
  - `generate_alpha_expression`
  - `mutate_structure`
  - `mutate_cross_domain_interaction`
  - `get_elite_variants`
  - `mutate_neutralization_group`
  - Main loop coordinator (applied as a final post-processing step on the `code` variable before simulation)

---

## 6. Real-Time Alpha Mutations & Generations

Below are the exact parent-to-child structural mutations and newly generated expressions recorded during validation dry runs:

### Mutation Example #1: Structural Mutation (Ts_Delta to Ts_Corr)
* **Parent Code**:
  `normalize(ts_decay_linear(group_neutralize(rank(ts_delta(zscore(ts_backfill(gross_profit_to_assets_ratio, 60)), 5)), bucket(rank(cap), range="0, 1, 0.1")), 10))`
* **Fixes Applied**:
  - Replaced the structural block with target whitelisted `ts_corr`.
  - Enforced `rank` wrapping before neutralization.
  - Capped the outer decay window to `10`.
* **Mutated Child Code**:
  `normalize(ts_decay_linear(group_neutralize(rank(ts_corr(zscore(ts_backfill(gross_profit_to_assets_ratio, 60)), rank(ts_backfill(assets, 60)), 5)), bucket(rank(cap), range="0, 1, 0.1")), 10))`

### Mutation Example #2: Lookback & Sign Shift
* **Parent Code**:
  `normalize(ts_decay_linear(group_neutralize(group_neutralize(zscore(ts_backfill(anl4_adjusted_netincome_ft, 60)), industry), bucket(rank(cap), range="0, 1, 0.1")), 30))`
* **Fixes Applied**:
  - Radical shift on the decay window from `30` down to the capped maximum of `10`.
  - Added signal direction reversal flag (`-1 *`).
  - Wrapped neutralized expression in `rank()`.
* **Mutated Child Code**:
  `-1 * normalize(ts_decay_linear(group_neutralize(group_neutralize(zscore(ts_backfill(anl4_adjusted_netincome_ft, 60)), industry), bucket(rank(cap), range="0, 1, 0.1")), 10))`

### Mutation Example #3: Lookback Window Shift
* **Parent Code**:
  `normalize(ts_decay_linear(group_neutralize(rank(ts_corr(zscore(ts_backfill(debt_st, 60)), rank(ts_backfill(debt, 60)), 5)), industry), 10))`
* **Fixes Applied**:
  - Shifted the standard operator lookback window from `5` to `20`.
  - Kept nested `ts_backfill(..., 60)` lookback windows untouched.
* **Mutated Child Code**:
  `normalize(ts_decay_linear(group_neutralize(rank(ts_delta(rank(ts_backfill(debt_st, 60)), 20)), industry), 10))`

### New Alpha Generation Example (Standard Generation)
* **Goal**: Generate a brand new, fully whitelisted, weight-stable alpha expression.
* **Fixes Applied**:
  - Restricted all internal math functions to whitelist (`rank`, `zscore`, `ts_corr`).
  - Capped decay window to `2`.
  - Neutralization wrapped in `rank()`.
  - Nested `ts_backfill` lookback window correctly preserved at `60`.
* **Generated Alpha Code**:
  `normalize(ts_decay_linear(group_neutralize(rank(ts_corr(rank(ts_backfill(anl4_netprofit_value, 60)), zscore(ts_backfill(mdl177_2_deepvaluefactor_ttmfcfev, 60)), 5)), industry), 2))`
