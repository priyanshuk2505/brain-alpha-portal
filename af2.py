#!/usr/bin/env python3
"""
WorldQuant BRAIN Advanced Alpha Generator (Dual-Engine Mode)
Autonomously generates, simulates, logs, and evolves mathematical trading signals
using either the Feedback-Driven Fundamental Engine or the 101 Formulaic Alphas Engine.
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
COOKIE = "_fbp=fb.1.1778595947954.838983336151760867; _ga=GA1.1.687920460.1778595944; _ga_9RN6WVT1K1=GS2.1.s1780775155$o77$g1$t1780775347$j49$l0$h0; _rdt_uuid=1778595944372.55b2243d-1bc9-440f-a27d-c17c7e25a64c; t=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIwVDJuRDEwd3kzTUdCZGM3eTdLZXp3UWFpNnp5SFRsTCIsImV4cCI6MTc4MDc3ODk0MSwiYW1yIjpbInB3ZCIsImZhY2UiLCJjYXB0Y2hhIl19.J8I3m4k4VoJsIKAS9IT6PMl1MZdTClRRWfs7woc_2Ng; _gcl_au=1.1.326319197.1778595941.1789914189.1780763836.1780764504; _ga_FXKNEPLB1N=GS2.1.s1779733566$o7$g0$t1779733566$j60$l0$h0; __zlcmid=1XcoWMCkz0Gybrj; cookieyes-consent=consentid:V3N1Q1lGeXMxZWJjQU5ienR2TEtiUnlGMTdIN3k3cFA,consent:yes,action:yes,necessary:yes,functional:yes,analytics:yes,performance:yes,advertisement:yes,other:yes"

# Categorized Premium Dataset Pool for Thematic Fundamental Signals
CATEGORIZED_FIELDS = {
    "ALTERNATIVE": [
        
        "sentiment_score_news",
        "news_volume_historical",
        "put_call_ratio_options",
        "short_interest_pct_shares",
        "sentiment_buzz_weekly",
        "implied_volatility_call_270",
        "implied_volatility_put_270",
        "news_sentiment_score",
        "options_volume_flow",
        "short_interest_shares_outstanding",
        "short_interest_ratio",
        "news_sentiment_momentum",
        "social_sentiment_buzz",
        "institutional_flow_sentiment",
        "block_trade_options_flow",
        "snt_social_value",
        "snt_social_value_fast_d1",
        "snt_social_volume",
        "snt_social_volume_fast_d1",
        "daily_equity_mood_indicator",
        "snt1_d1_dynamicfocusrank",
        "weekly_equity_mood_index",
        "historical_volatility_10",
        "historical_volatility_120",
        "historical_volatility_150",
        "historical_volatility_180",
        "historical_volatility_20",
        "historical_volatility_30",
        "historical_volatility_60",
        "historical_volatility_90",
        "implied_volatility_call_10",
        "implied_volatility_call_1080",
        "implied_volatility_call_120",
        "implied_volatility_call_150",
        "implied_volatility_call_180",
        "implied_volatility_call_20",
        "implied_volatility_call_30",
        "implied_volatility_call_360",
        "implied_volatility_call_60",
        "implied_volatility_call_720",
        "implied_volatility_call_90",
        "implied_volatility_mean_10",
        "implied_volatility_mean_1080",
        "implied_volatility_mean_120",
        "implied_volatility_mean_150",
        "implied_volatility_mean_180",
        "implied_volatility_mean_20",
        "implied_volatility_mean_270",
        "implied_volatility_mean_30",
        "implied_volatility_mean_360",
        "implied_volatility_mean_60",
        "implied_volatility_mean_720",
        "implied_volatility_mean_90",
        "implied_volatility_mean_skew_10",
        "implied_volatility_mean_skew_1080",
        "implied_volatility_mean_skew_120",
        "implied_volatility_mean_skew_150",
        "implied_volatility_mean_skew_180",
        "implied_volatility_mean_skew_20",
        "implied_volatility_mean_skew_270",
        "implied_volatility_mean_skew_30",
        "implied_volatility_mean_skew_360",
        "implied_volatility_mean_skew_60",
        "implied_volatility_mean_skew_720",
        "implied_volatility_mean_skew_90",
        "implied_volatility_put_10",
        "implied_volatility_put_1080",
        "implied_volatility_put_120",
        "implied_volatility_put_150",
        "implied_volatility_put_180",
        "implied_volatility_put_20",
        "implied_volatility_put_30",
        "implied_volatility_put_360",
        "implied_volatility_put_60",
        "implied_volatility_put_720",
        "implied_volatility_put_90",
        "parkinson_volatility_10",
        "parkinson_volatility_120",
        "parkinson_volatility_150",
        "parkinson_volatility_180",
        "parkinson_volatility_20",
        "parkinson_volatility_30",
        "parkinson_volatility_60",
        "parkinson_volatility_90",
        "pcr_oi_10",
        "pcr_oi_1080",
        "pcr_oi_120",
        "pcr_oi_150",
        "pcr_oi_180",
        "pcr_oi_20",
        "pcr_oi_270",
        "pcr_oi_30",
        "pcr_oi_360",
        "pcr_oi_60",
        "pcr_oi_720",
        "pcr_oi_90",
        "pcr_oi_all",
        "pcr_vol_10",
        "pcr_vol_1080",
        "pcr_vol_120",
        "pcr_vol_150",
        "pcr_vol_180",
        "pcr_vol_20",
        "pcr_vol_270",
        "pcr_vol_30",
        "pcr_vol_360",
        "pcr_vol_60",
        "pcr_vol_720",
        "pcr_vol_90",
        "pcr_vol_all",
        "beta_last_30_days_spy",
        "beta_last_360_days_spy",
        "beta_last_60_days_spy",
        "beta_last_90_days_spy",
        "correlation_last_30_days_spy",
        "correlation_last_360_days_spy",
        "correlation_last_60_days_spy",
        "correlation_last_90_days_spy",
        "systematic_risk_last_30_days",
        "systematic_risk_last_360_days",
        "systematic_risk_last_60_days",
        "systematic_risk_last_90_days",
        "unsystematic_risk_last_30_days",
        "unsystematic_risk_last_360_days",
        "unsystematic_risk_last_60_days",
        "unsystematic_risk_last_90_days",
        "analyst_revision_rank_derivative",
        "cashflow_efficiency_rank_derivative",
        "composite_factor_score_derivative",
        "earnings_certainty_rank_derivative",
        "fscore_bfl_surface",
        "fscore_bfl_surface_accel",
        "fscore_bfl_total",
        "fscore_surface"
    ],
    "PROFITABILITY": [
        
        "adj_net_income_median",
        "abnormal_return_earnings_release",
        "cash_earnings_return_on_equity",
        "consensus_analyst_rating",
        "domestic_ebit_value",
        "earnings_expectation_module_score",
        "earnings_momentum_analyst_score",
        "earnings_momentum_composite_score",
        "earnings_momentum_composite_score_2",
        "earnings_torpedo_indicator",
        "ebit",
        "ebitda",
        "fcf_yield_multiplied_forward_roe",
        "fcf_yield_times_forward_roe",
        "fcf_yield_times_forward_roe_2",
        "gross_profit_margin_ttm_2",
        "gross_profit_to_assets_ratio",
        "mdl177_2_earningmomentumfactor400_cvfy1eps",
        "mdl177_2_earningmomentumfactor400_cvfy2eps",
        "mdl177_2_earningmomentumfactor400_dypeg",
        "mdl177_2_earningmomentumfactor400_epsrm",
        "mdl177_2_earningmomentumfactor400_fcfroey1p",
        "mdl177_2_earningmomentumfactor400_fqsurstd",
        "mdl177_2_earningmomentumfactor400_fy1epsskew",
        "mdl177_2_earningmomentumfactor400_hlep",
        "mdl177_2_earningmomentumfactor400_numrevq1",
        "mdl177_2_earningmomentumfactor400_numrevy1",
        "mdl177_2_earningmomentumfactor400_salesurp",
        "mdl177_2_earningmomentumfactor400_stdevfy1epsp",
        "mdl177_2_earningmomentumfactor400_stdevfy2epsp",
        "mdl177_2_earningmomentumfactor400_stockrating",
        "mdl177_2_earningmomentumfactor400_sucf",
        "mdl177_2_earningmomentumfactor400_sue",
        "mdl177_2_earningmomentumfactor400_surp",
        "eps",
        "coefficient_variation_fy1_eps",
        "coefficient_variation_fy2_eps",
        "earnings_shortfall_metric",
        "fnd6_newqeventv110_ibcomq",
        "fy2_eps_estimate_dispersion",
        "mdl177_2_earningmomentumfactor400_qepsferr",
        "snt1_cored1_score",
        "snt1_d1_analystcoverage",
        "snt1_d1_buyrecpercent",
        "snt1_d1_dtstsespe",
        "snt1_d1_earningssurprise",
        "snt1_d1_earningstorpedo",
        "snt1_d1_netrecpercent",
        "snt1_d1_sellrecpercent",
        "fscore_bfl_profitability",
        "fscore_bfl_quality",
        "fscore_profitability",
        "fscore_quality"
    ],
    "LEVERAGE": [
        "current_liabilities_to_price",
        "current_liabilities_to_price_v1",
        "debt",
        "debt_carrying_amount_total",
        "debt_carrying_value",
        "debt_lt",
        "debt_maturities_repayments_next12m",
        "debt_maturities_repayments_year2",
        "debt_principal_due_year_five",
        "debt_repayment_year_three",
        "debt_repayments_total",
        "debt_repayments_total_2",
        "debt_st",
        "credit_facility_max_borrowing",
        "credit_facility_max_borrowing_2",
        "credit_facility_outstanding_amount",
        "credit_facility_outstanding_balance",
        "credit_risk_premium_indicator",
        "distress_risk_measure",
        "employee_compensation_benefit_liabilities",
        "liquidity_cash_to_liabilities_ratio",
        "assets",
        "assets_curr",
        "debt_stated_interest_rate_pct",
        "anl4_adjusted_netincome_ft", 
        "anl4_ebit_value", 
        "anl4_ebitda_value", 
        "anl4_netprofit_value", 
        "actual_eps_value_quarterly"
    ],
    "GROWTH": [
        
        "asset_growth_rate",
        "asset_growth_rate_sensitivityfactor",
        "change_in_eps_surprise",
        "earnings_revision_magnitude",
        "five_year_eps_stability",
        "five_year_eps_trend_r_squared_2",
        "five_year_eps_trend_slope_2",
        "forward_two_year_eps_growth_rate",
        "fundamental_growth_module_score",
        "mdl177_2_earningmomentumfactor400_chg6mltg",
        "mdl177_2_earningmomentumfactor400_egp",
        "mdl177_2_earningmomentumfactor400_ltg",
        "mdl177_2_earningmomentumfactor400_perg",
        "mdl177_2_earningmomentumfactor400_q1aepsg",
        "mdl177_2_earningmomentumfactor400_y1aepsg",
        "mdl177_2_earningmomentumfactor400_y2aepsg",
        "mdl177_2_earningmomentumfactor400_y2repsg",
        "mdl177_2_earningmomentumfactor400_y3sur",
        "long_term_earnings_growth_forecast",
        "long_term_growth_estimate",
        "long_term_growth_forecast_2",
        "high_low_eps_revision_sum",
        "mdl177_2_earningmomentumfactor400_lagegp",
        "mdl177_2_earningmomentumfactor400_ratrev6m",
        "mdl177_2_earningmomentumfactor400_rev1q1",
        "mdl177_2_earningmomentumfactor400_rev3y1",
        "mdl177_2_earningmomentumfactor400_rev3y2",
        "mdl177_2_earningmomentumfactor400_rev6",
        "sales_estimate_count",
        "earnings_per_share_estimate_count",
        "anl4_afv4_eps_mean",
        "snt1_d1_earningsrevision",
        "snt1_d1_longtermepsgrowthest",
        "snt1_d1_netearningsrevision",
        "fscore_bfl_growth",
        "fscore_bfl_momentum",
        "fscore_growth",
        "fscore_momentum"
    ],
    "EFFICIENCY": [
        "capex",
        "capex_to_depreciation_linkage",
        "capex_to_total_assets",
        "cogs",
        "cash_burn_rate",
        "cash_burn_rate_v1",
        "current_ratio",
        "depre_amort",
        "employee",
        "equipment_maximum_useful_life",
        "inventory_change_avg_assets",
        "mdl177_2_earningsqualityfactor_chgsgasale",
        "mdl177_2_earningsqualityfactor_chgshare",
        "mdl177_2_earningsqualityfactor_cogsinvt",
        "mdl177_2_earningsqualityfactor_dpcapex",
        "mdl177_2_earningsqualityfactor_epschgetr",
        "mdl177_2_earningsqualityfactor_erc",
        "mdl177_2_earningsqualityfactor_indrelrecd_",
        "mdl177_2_earningsqualityfactor_ncfeps",
        "mdl177_2_earningsqualityfactor_opincltd",
        "mdl177_2_earningsqualityfactor_saleeps",
        "mdl177_2_earningsqualityfactor_salegpm",
        "mdl177_2_earningsqualityfactor_salerec",
        "mdl177_2_earningsqualityfactor_ttmaccu",
        "mdl177_2_earningsqualityfactor_uaccl",
        "mdl177_2_earningsqualityfactor_uar",
        "mdl177_2_earningsqualityfactor_udep",
        "mdl177_2_earningsqualityfactor_uinv",
        "mdl177_2_earningsqualityfactor_wcacc",
        "mdl177_2_earningsqualityfactor_yoychgaa",
        "fnd6_newqeventv110_cogsq"
    ],
    "VALUATION": [
        
        "anl4_afv4_div_high",
        "bookvalue_ps",
        "enterprise_value",
        "enterprise_value_weighted_value_score",
        "equity",
        "equity_value_score",
        "forward_book_value_to_price",
        "forward_cash_flow_to_price",
        "forward_ebitda_to_enterprise_value_2",
        "forward_sales_to_price",
        "income_statement_value_score",
        "inverse_peg_earnings_growth",
        "inverse_peg_ratio",
        "inverse_peg_ratio_2",
        "inverse_peg_ratio_2_emmodel",
        "inverse_peg_ratio_emmodel",
        "lagged_inverse_peg_ratio",
        "mdl177_2_5yearrelativevaluefactor_rel5ybp",
        "mdl177_2_5yearrelativevaluefactor_rel5ycfp",
        "mdl177_2_5yearrelativevaluefactor_rel5ycoreepsp",
        "mdl177_2_5yearrelativevaluefactor_rel5ydivp",
        "mdl177_2_5yearrelativevaluefactor_rel5yebitdap",
        "mdl177_2_5yearrelativevaluefactor_rel5yep",
        "mdl177_2_5yearrelativevaluefactor_rel5yfcfp",
        "mdl177_2_5yearrelativevaluefactor_rel5yocfp",
        "mdl177_2_5yearrelativevaluefactor_rel5ysp",
        "mdl177_2_deepvaluefactor_acqmul",
        "mdl177_2_deepvaluefactor_bp",
        "mdl177_2_deepvaluefactor_cashp",
        "mdl177_2_deepvaluefactor_cashsev",
        "mdl177_2_deepvaluefactor_coreepsp",
        "mdl177_2_deepvaluefactor_divyield",
        "mdl177_2_deepvaluefactor_ebitdaev",
        "mdl177_2_deepvaluefactor_ebitdap",
        "mdl177_2_deepvaluefactor_ebop",
        "mdl177_2_deepvaluefactor_f12mepssev",
        "mdl177_2_deepvaluefactor_fwdep",
        "mdl177_2_deepvaluefactor_indidivy",
        "mdl177_2_deepvaluefactor_navp",
        "mdl177_2_deepvaluefactor_nnastp",
        "mdl177_2_deepvaluefactor_past",
        "mdl177_2_deepvaluefactor_proformaep",
        "mdl177_2_deepvaluefactor_ttmcapexp",
        "mdl177_2_deepvaluefactor_ttmcfp",
        "mdl177_2_deepvaluefactor_ttmepa",
        "mdl177_2_deepvaluefactor_ttmepb",
        "mdl177_2_deepvaluefactor_ttmfcfev",
        "mdl177_2_deepvaluefactor_ttmfcfp",
        "mdl177_2_deepvaluefactor_ttmgfp",
        "mdl177_2_deepvaluefactor_ttmocfp",
        "mdl177_2_deepvaluefactor_ttmpiqp",
        "mdl177_2_deepvaluefactor_ttmsaleev",
        "mdl177_2_deepvaluefactor_ttmsp",
        "mdl177_2_deepvaluemodel2_dv_currroe",
        "mdl177_2_deepvaluemodel_chgshare",
        "mdl177_2_deepvaluemodel_dv_yoychgat",
        "mdl177_2_deepvaluemodel_dvm_composite",
        "mdl177_2_deepvaluemodel_indidivy",
        "mdl177_2_deepvaluemodel_ttmfcfev",
        "mdl177_2_garpanalystmodel_qgp_alert",
        "mdl177_2_garpanalystmodel_qgp_avgrating",
        "mdl177_2_garpanalystmodel_qgp_chgvaluation",
        "mdl177_2_garpanalystmodel_qgp_composite",
        "mdl177_2_garpanalystmodel_qgp_growthval",
        "mdl177_2_garpanalystmodel_qgp_relgrowth",
        "mdl177_2_garpanalystmodel_qgp_relpegy",
        "mdl177_2_garpanalystmodel_qgp_roefcf",
        "mdl177_2_garpanalystmodel_qgp_valuation",
        "mdl177_2_garpanalystmodel_qgp_wratingchg",
        "mdl177_2_garpmodel_gpm_composite",
        "snt1_d1_downtargetpercent",
        "snt1_d1_fundamentalfocusrank",
        "snt1_d1_nettargetpercent",
        "snt1_d1_stockrank",
        "snt1_d1_uptargetpercent",
        "call_breakeven_10",
        "call_breakeven_1080",
        "call_breakeven_120",
        "call_breakeven_150",
        "call_breakeven_180",
        "call_breakeven_20",
        "call_breakeven_270",
        "call_breakeven_30",
        "call_breakeven_360",
        "call_breakeven_60",
        "call_breakeven_720",
        "call_breakeven_90",
        "forward_price_10",
        "forward_price_1080",
        "forward_price_120",
        "forward_price_150",
        "forward_price_180",
        "forward_price_20",
        "forward_price_270",
        "forward_price_30",
        "forward_price_360",
        "forward_price_60",
        "forward_price_720",
        "forward_price_90",
        "option_breakeven_10",
        "option_breakeven_1080",
        "option_breakeven_120",
        "option_breakeven_150",
        "option_breakeven_180",
        "option_breakeven_20",
        "option_breakeven_270",
        "option_breakeven_30",
        "option_breakeven_360",
        "option_breakeven_60",
        "option_breakeven_720",
        "option_breakeven_90",
        "put_breakeven_10",
        "put_breakeven_1080",
        "put_breakeven_120",
        "put_breakeven_150",
        "put_breakeven_180",
        "put_breakeven_20",
        "put_breakeven_270",
        "put_breakeven_30",
        "put_breakeven_360",
        "put_breakeven_60",
        "put_breakeven_720",
        "put_breakeven_90",
        "fscore_bfl_value"
    ],
    "OTHER_FUNDAMENTAL": [
        "deferred_tax_liabilities_total_4",
        "deferred_tax_liability_property_plant_equipment",
        "derivative_liability_fair_value",
        "doubtful_accounts_provision_2",
        "fair_value_derivative_liabilities",
        "fnd6_cptrank_gvkeymap",
        "latin_america_sales_exposure",
        "market_volatility_index",
        "accumulated_amortization_finite_intangibles",
        "accumulated_depreciation_depletion_amortization_ppne",
        "accumulated_oci_net_of_tax_value",
        "acquisition_total_purchase_price",
        "acquisition_total_purchase_value",
        "allocated_sbp_expense_total",
        "allowance_for_doubtful_accounts_2",
        "annual_deferred_income_tax_expense",
        "annual_intangible_amortization_expense_second_year",
        "annual_intangible_assets_net_carrying_value",
        "antidilutive_securities_eps_exclusion_count",
        "antidilutive_securities_excluded_eps",
        "business_acquisition_payments_net",
        "cash",
        "cash_st",
        "cashflow",
        "cashflow_dividends",
        "cashflow_fin",
        "cashflow_invst",
        "cashflow_op",
        "common_shares_outstanding_total",
        "common_stock_buyback_payments",
        "common_stock_issuance_proceeds",
        "common_stock_issuance_proceeds_2",
        "common_stock_repurchase_payment",
        "common_stock_shares_outstanding_count",
        "comprehensive_income_net_tax",
        "comprehensive_income_net_tax_value",
        "current_federal_tax_expense_amount",
        "current_foreign_tax_expense_value",
        "current_income_tax_expense_amount",
        "current_minimum_operating_lease_payment",
        "current_state_local_tax_expense_amount",
        "debt_instrument_interest_rate_percent",
        "debt_issuance_costs_expense",
        "debt_issuance_proceeds",
        "debt_issuance_proceeds_2",
        "deferred_federal_income_tax_expense",
        "deferred_income_tax_expense_amount",
        "deferred_local_income_tax_expense",
        "deferred_tax_assets_compensation_benefits",
        "deferred_tax_assets_credit_carryforward",
        "deferred_tax_assets_expense_reserves",
        "deferred_tax_assets_loss_carryforward",
        "deferred_tax_assets_net_value",
        "deferred_tax_assets_valuation_allowance_value",
        "derivative_asset_fair_value_2",
        "diluted_shares_outstanding_adjustment",
        "diluted_shares_outstanding_adjustment_avg",
        "dividends_to_gross_profit",
        "effective_tax_rate_continuing_ops_2",
        "emea_sales_exposure",
        "equity_awards_granted_non_option_period",
        "exercisable_options_avg_exercise_price_2",
        "exercisable_options_count",
        "federal_statutory_tax_rate",
        "fifteen_to_thirtysix_week_price_ratio",
        "fifty_to_two_hundred_day_price_ratio",
        "financial_statement_value_score",
        "finite_intangibles_gross_value",
        "fn_avg_diluted_sharesout_adj_a",
        "fn_avg_diluted_sharesout_adj_q",
        "fn_comp_fair_value_assumptions_weighted_avg_vol_rate_a",
        "fn_comp_not_rec_stock_options_a",
        "fn_comp_options_exercisable_weighted_avg_a",
        "fn_comprehensive_income_net_of_tax_q",
        "fnd6_acdo",
        "fnd6_acodo",
        "fnd6_acox",
        "fnd6_acqgdwl",
        "fnd6_acqintan",
        "fnd6_adesinda_curcd",
        "fnd6_aldo",
        "fnd6_am",
        "fnd6_aodo",
        "fnd6_aox",
        "fnd6_aqc",
        "fnd6_aqi",
        "fnd6_aqs",
        "fnd6_beta",
        "fnd6_capxs",
        "fnd6_capxv",
        "fnd6_caxts",
        "fnd6_ceql",
        "fnd6_ch",
        "fnd6_ci",
        "fnd6_cibegni",
        "fnd6_cicurr",
        "fnd6_cidergl",
        "fnd6_cik",
        "fnd6_cimii",
        "fnd6_ciother",
        "fnd6_cipen",
        "fnd6_cisecgl",
        "fnd6_citotal",
        "fnd6_city",
        "fnd6_cld2",
        "fnd6_cld3",
        "fnd6_cld4",
        "fnd6_cld5",
        "fnd6_cogss",
        "fnd6_cptmfmq_actq",
        "fnd6_cptmfmq_atq",
        "fnd6_cptmfmq_ceqq",
        "fnd6_cptmfmq_dlttq",
        "fnd6_cptmfmq_dpq",
        "fnd6_cptmfmq_lctq",
        "fnd6_cptmfmq_oibdpq",
        "fnd6_cptmfmq_opepsq",
        "fnd6_cptmfmq_saleq",
        "fnd6_cptnewqeventv110_actq",
        "fnd6_cptnewqeventv110_apq",
        "fnd6_cptnewqeventv110_atq",
        "fnd6_cptnewqeventv110_ceqq",
        "fnd6_cptnewqeventv110_dlttq",
        "fnd6_cptnewqeventv110_dpq",
        "fnd6_cptnewqeventv110_epsf12",
        "fnd6_cptnewqeventv110_epsfxq",
        "fnd6_cptnewqeventv110_epsx12",
        "fnd6_cptnewqeventv110_lctq",
        "fnd6_cptnewqeventv110_ltq",
        "fnd6_cptnewqeventv110_nopiq",
        "fnd6_cptnewqeventv110_oeps12",
        "fnd6_cptnewqeventv110_oiadpq",
        "fnd6_cptnewqeventv110_oibdpq",
        "fnd6_cptnewqeventv110_opepsq",
        "fnd6_cptnewqeventv110_rectq",
        "fnd6_cptnewqeventv110_req",
        "fnd6_cptnewqeventv110_saleq",
        "fnd6_cptnewqv1300_actq",
        "fnd6_cptnewqv1300_apq",
        "fnd6_cptnewqv1300_atq",
        "fnd6_cptnewqv1300_ceqq",
        "fnd6_cptnewqv1300_dlttq",
        "fnd6_cptnewqv1300_dpq",
        "fnd6_cptnewqv1300_epsf12",
        "fnd6_cptnewqv1300_epsfxq",
        "fnd6_cptnewqv1300_epsx12",
        "fnd6_cptnewqv1300_lctq",
        "fnd6_cptnewqv1300_ltq",
        "fnd6_cptnewqv1300_nopiq",
        "fnd6_cptnewqv1300_oeps12",
        "fnd6_cptnewqv1300_oiadpq",
        "fnd6_cptnewqv1300_oibdpq",
        "fnd6_cptnewqv1300_opepsq",
        "fnd6_cptnewqv1300_rectq",
        "fnd6_cptnewqv1300_req",
        "fnd6_cptnewqv1300_saleq",
        "fnd6_cshpri",
        "fnd6_cshr",
        "fnd6_cshtr",
        "fnd6_cshtrq",
        "fnd6_cstkcv",
        "fnd6_cstkcvq",
        "fnd6_curcddv",
        "fnd6_currencya_curcd",
        "fnd6_currencyqv1300_curcd",
        "fnd6_dc",
        "fnd6_dclo",
        "fnd6_dcpstk",
        "fnd6_dcvsr",
        "fnd6_dcvsub",
        "fnd6_dcvt",
        "fnd6_dd",
        "fnd6_dd1",
        "fnd6_dd1q",
        "fnd6_dd2",
        "fnd6_dd3",
        "fnd6_dd4",
        "fnd6_dd5",
        "fnd6_dilavx",
        "fnd6_divd",
        "fnd6_dlcch",
        "fnd6_dltis",
        "fnd6_dlto",
        "fnd6_dltp",
        "fnd6_dltr",
        "fnd6_dm",
        "fnd6_dn",
        "fnd6_donr",
        "fnd6_dps",
        "fnd6_dpvieb",
        "fnd6_drc",
        "fnd6_drlt",
        "fnd6_ds",
        "fnd6_dudd",
        "fnd6_dvpa",
        "fnd6_dvrated",
        "fnd6_dxd2",
        "fnd6_dxd3",
        "fnd6_dxd4",
        "fnd6_dxd5",
        "fnd6_ein",
        "fnd6_emps",
        "fnd6_esopct",
        "fnd6_esopnr",
        "fnd6_esopr",
        "fnd6_esubc",
        "fnd6_esubs",
        "fnd6_eventv110_aqdq",
        "fnd6_eventv110_aqepsq",
        "fnd6_eventv110_cstkcvq",
        "fnd6_eventv110_dd1q",
        "fnd6_eventv110_dtedq",
        "fnd6_eventv110_dteepsq",
        "fnd6_eventv110_gdwlid12",
        "fnd6_eventv110_gdwlidq",
        "fnd6_eventv110_gdwlieps12",
        "fnd6_eventv110_gdwliepsq",
        "fnd6_eventv110_gldq",
        "fnd6_eventv110_glepsq",
        "fnd6_eventv110_npq",
        "fnd6_eventv110_nrtxtdq",
        "fnd6_eventv110_nrtxtepsq",
        "fnd6_eventv110_optdrq",
        "fnd6_eventv110_optlifeq",
        "fnd6_eventv110_optvolq",
        "fnd6_eventv110_pncd12",
        "fnd6_eventv110_pncdq",
        "fnd6_eventv110_pnceps12",
        "fnd6_eventv110_pncepsq",
        "fnd6_eventv110_pncidq",
        "fnd6_eventv110_pncwidq",
        "fnd6_eventv110_pncwiepsq",
        "fnd6_eventv110_setdq",
        "fnd6_eventv110_setepsq",
        "fnd6_eventv110_spced12",
        "fnd6_eventv110_spidq",
        "fnd6_eventv110_spiepsq",
        "fnd6_eventv110_txdbcaq",
        "fnd6_eventv110_txdbclq",
        "fnd6_eventv110_wddq",
        "fnd6_eventv110_wdepsq",
        "fnd6_eventv110_xaccq",
        "fnd6_exre",
        "fnd6_fatb",
        "fnd6_fatc",
        "fnd6_fate",
        "fnd6_fatl",
        "fnd6_fatn",
        "fnd6_fato",
        "fnd6_fatp",
        "fnd6_fiao",
        "fnd6_fic",
        "fnd6_fopo",
        "fnd6_fopox",
        "fnd6_fyrc",
        "fnd6_gdwls",
        "fnd6_ias",
        "fnd6_ibmii",
        "fnd6_ibs",
        "fnd6_idesindq_curcd",
        "fnd6_idit",
        "fnd6_iints",
        "fnd6_incorp",
        "fnd6_intan",
        "fnd6_intc",
        "fnd6_intpn",
        "fnd6_intseg",
        "fnd6_invfg",
        "fnd6_invo",
        "fnd6_invrm",
        "fnd6_invwip",
        "fnd6_itcb",
        "fnd6_itci",
        "fnd6_ivaco",
        "fnd6_ivaeq",
        "fnd6_ivaeqs",
        "fnd6_ivao",
        "fnd6_ivch",
        "fnd6_ivst",
        "fnd6_ivstch",
        "fnd6_lcox",
        "fnd6_lcoxdr",
        "fnd6_lifr",
        "fnd6_lno",
        "fnd6_loc",
        "fnd6_lol2",
        "fnd6_loxdr",
        "fnd6_lqpl1",
        "fnd6_lul3",
        "fnd6_mfma1_aoloch",
        "fnd6_mfma1_apalch",
        "fnd6_mfma1_at",
        "fnd6_mfma1_capx",
        "fnd6_mfma1_csho",
        "fnd6_mfma1_dp",
        "fnd6_mfma1_dpc",
        "fnd6_mfma1_invch",
        "fnd6_mfma2_oancf",
        "fnd6_mfma2_opeps",
        "fnd6_mfma2_recch",
        "fnd6_mfma2_revt",
        "fnd6_mfma2_txach",
        "fnd6_mfmq_cheq",
        "fnd6_mfmq_cogsq",
        "fnd6_mfmq_cshprq",
        "fnd6_mfmq_dlcq",
        "fnd6_mfmq_ibcomq",
        "fnd6_mfmq_mibtq",
        "fnd6_mfmq_piq",
        "fnd6_mibn",
        "fnd6_mibt",
        "fnd6_mkvalt",
        "fnd6_mkvaltq",
        "fnd6_mrc1",
        "fnd6_mrc2",
        "fnd6_mrc3",
        "fnd6_mrc4",
        "fnd6_mrc5",
        "fnd6_mrct",
        "fnd6_mrcta",
        "fnd6_msa",
        "fnd6_naicss",
        "fnd6_newa1v1300_aco",
        "fnd6_newa1v1300_acominc",
        "fnd6_newa1v1300_act",
        "fnd6_newa1v1300_ano",
        "fnd6_newa1v1300_ao",
        "fnd6_newa1v1300_aocidergl",
        "fnd6_newa1v1300_aociother",
        "fnd6_newa1v1300_aocipen",
        "fnd6_newa1v1300_aol2",
        "fnd6_newa1v1300_aoloch",
        "fnd6_newa1v1300_ap",
        "fnd6_newa1v1300_apalch",
        "fnd6_newa1v1300_aqpl1",
        "fnd6_newa1v1300_at",
        "fnd6_newa1v1300_aul3",
        "fnd6_newa1v1300_bkvlps",
        "fnd6_newa1v1300_caps",
        "fnd6_newa1v1300_capx",
        "fnd6_newa1v1300_ceq",
        "fnd6_newa1v1300_ceqt",
        "fnd6_newa1v1300_che",
        "fnd6_newa1v1300_chech",
        "fnd6_newa1v1300_cogs",
        "fnd6_newa1v1300_cshfd",
        "fnd6_newa1v1300_cshi",
        "fnd6_newa1v1300_csho",
        "fnd6_newa1v1300_cstk",
        "fnd6_newa1v1300_dcom",
        "fnd6_newa1v1300_dlc",
        "fnd6_newa1v1300_dltt",
        "fnd6_newa1v1300_dp",
        "fnd6_newa1v1300_dpact",
        "fnd6_newa1v1300_dpc",
        "fnd6_newa1v1300_dv",
        "fnd6_newa1v1300_dvc",
        "fnd6_newa1v1300_dvt",
        "fnd6_newa1v1300_ebit",
        "fnd6_newa1v1300_ebitda",
        "fnd6_newa1v1300_emp",
        "fnd6_newa1v1300_epsfi",
        "fnd6_newa1v1300_epsfx",
        "fnd6_newa1v1300_epspi",
        "fnd6_newa1v1300_epspx",
        "fnd6_newa1v1300_fca",
        "fnd6_newa1v1300_fincf",
        "fnd6_newa1v1300_gdwl",
        "fnd6_newa1v1300_gp",
        "fnd6_newa1v1300_ib",
        "fnd6_newa1v1300_ibadj",
        "fnd6_newa1v1300_ibc",
        "fnd6_newa1v1300_ibcom",
        "fnd6_newa1v1300_icapt",
        "fnd6_newa1v1300_intano",
        "fnd6_newa1v1300_invch",
        "fnd6_newa1v1300_invt",
        "fnd6_newa1v1300_ivncf",
        "fnd6_newa1v1300_lco",
        "fnd6_newa1v1300_lct",
        "fnd6_newa1v1300_lo",
        "fnd6_newa1v1300_lse",
        "fnd6_newa1v1300_lt",
        "fnd6_newa2v1300_mib",
        "fnd6_newa2v1300_mii",
        "fnd6_newa2v1300_ni",
        "fnd6_newa2v1300_nopi",
        "fnd6_newa2v1300_oancf",
        "fnd6_newa2v1300_oiadp",
        "fnd6_newa2v1300_oibdp",
        "fnd6_newa2v1300_opeps",
        "fnd6_newa2v1300_optexd",
        "fnd6_newa2v1300_pi",
        "fnd6_newa2v1300_ppegt",
        "fnd6_newa2v1300_ppent",
        "fnd6_newa2v1300_prsho",
        "fnd6_newa2v1300_rdip",
        "fnd6_newa2v1300_rdipa",
        "fnd6_newa2v1300_rdipd",
        "fnd6_newa2v1300_rdipeps",
        "fnd6_newa2v1300_re",
        "fnd6_newa2v1300_recch",
        "fnd6_newa2v1300_rect",
        "fnd6_newa2v1300_reuna",
        "fnd6_newa2v1300_revt",
        "fnd6_newa2v1300_sale",
        "fnd6_newa2v1300_seq",
        "fnd6_newa2v1300_seqo",
        "fnd6_newa2v1300_spced",
        "fnd6_newa2v1300_spceeps",
        "fnd6_newa2v1300_spi",
        "fnd6_newa2v1300_stkco",
        "fnd6_newa2v1300_tstk",
        "fnd6_newa2v1300_tstkn",
        "fnd6_newa2v1300_txach",
        "fnd6_newa2v1300_txdb",
        "fnd6_newa2v1300_txditc",
        "fnd6_newa2v1300_txp",
        "fnd6_newa2v1300_txt",
        "fnd6_newa2v1300_wcap",
        "fnd6_newa2v1300_xidoc",
        "fnd6_newa2v1300_xint",
        "fnd6_newa2v1300_xoptd",
        "fnd6_newa2v1300_xopteps",
        "fnd6_newa2v1300_xrd",
        "fnd6_newa2v1300_xsga",
        "fnd6_newq_xoptdqp",
        "fnd6_newq_xoptepsqp",
        "fnd6_newq_xoptqp",
        "fnd6_newqeventv110_acchgq",
        "fnd6_newqeventv110_acomincq",
        "fnd6_newqeventv110_acoq",
        "fnd6_newqeventv110_altoq",
        "fnd6_newqeventv110_ancq",
        "fnd6_newqeventv110_anoq",
        "fnd6_newqeventv110_aociderglq",
        "fnd6_newqeventv110_aociotherq",
        "fnd6_newqeventv110_aocipenq",
        "fnd6_newqeventv110_aocisecglq",
        "fnd6_newqeventv110_aol2q",
        "fnd6_newqeventv110_aoq",
        "fnd6_newqeventv110_aqaq",
        "fnd6_newqeventv110_aqpl1q",
        "fnd6_newqeventv110_aqpq",
        "fnd6_newqeventv110_aul3q",
        "fnd6_newqeventv110_capsq",
        "fnd6_newqeventv110_cheq",
        "fnd6_newqeventv110_chq",
        "fnd6_newqeventv110_cibegniq",
        "fnd6_newqeventv110_cicurrq",
        "fnd6_newqeventv110_ciderglq",
        "fnd6_newqeventv110_cimiiq",
        "fnd6_newqeventv110_ciotherq",
        "fnd6_newqeventv110_cipenq",
        "fnd6_newqeventv110_ciq",
        "fnd6_newqeventv110_cisecglq",
        "fnd6_newqeventv110_citotalq",
        "fnd6_newqeventv110_csh12q",
        "fnd6_newqeventv110_cshfdq",
        "fnd6_newqeventv110_cshiq",
        "fnd6_newqeventv110_cshopq",
        "fnd6_newqeventv110_cshoq",
        "fnd6_newqeventv110_cshprq",
        "fnd6_newqeventv110_cstkeq",
        "fnd6_newqeventv110_cstkq",
        "fnd6_newqeventv110_dcomq",
        "fnd6_newqeventv110_diladq",
        "fnd6_newqeventv110_dilavq",
        "fnd6_newqeventv110_dlcq",
        "fnd6_newqeventv110_doq",
        "fnd6_newqeventv110_dpactq",
        "fnd6_newqeventv110_drcq",
        "fnd6_newqeventv110_drltq",
        "fnd6_newqeventv110_dteaq",
        "fnd6_newqeventv110_dtepq",
        "fnd6_newqeventv110_dvpq",
        "fnd6_newqeventv110_epsfiq",
        "fnd6_newqeventv110_epspiq",
        "fnd6_newqeventv110_epspxq",
        "fnd6_newqeventv110_esopctq",
        "fnd6_newqeventv110_esopnrq",
        "fnd6_newqeventv110_esoprq",
        "fnd6_newqeventv110_esoptq",
        "fnd6_newqeventv110_fcaq",
        "fnd6_newqeventv110_gdwlamq",
        "fnd6_newqeventv110_gdwlia12",
        "fnd6_newqeventv110_gdwliaq",
        "fnd6_newqeventv110_gdwlipq",
        "fnd6_newqeventv110_gdwlq",
        "fnd6_newqeventv110_glaq",
        "fnd6_newqeventv110_glcea12",
        "fnd6_newqeventv110_glceaq",
        "fnd6_newqeventv110_glced12",
        "fnd6_newqeventv110_glcedq",
        "fnd6_newqeventv110_glceeps12",
        "fnd6_newqeventv110_glceepsq",
        "fnd6_newqeventv110_glcepq",
        "fnd6_newqeventv110_glpq",
        "fnd6_newqeventv110_hedgeglq",
        "fnd6_newqeventv110_ibadj12",
        "fnd6_newqeventv110_ibadjq",
        "fnd6_newqeventv110_ibmiiq",
        "fnd6_newqeventv110_ibq",
        "fnd6_newqeventv110_icaptq",
        "fnd6_newqeventv110_intanoq",
        "fnd6_newqeventv110_intanq",
        "fnd6_newqeventv110_invfgq",
        "fnd6_newqeventv110_invoq",
        "fnd6_newqeventv110_invrmq",
        "fnd6_newqeventv110_invtq",
        "fnd6_newqeventv110_invwipq",
        "fnd6_newqeventv110_ivltq",
        "fnd6_newqeventv110_ivstq",
        "fnd6_newqeventv110_lcoq",
        "fnd6_newqeventv110_lltq",
        "fnd6_newqeventv110_lnoq",
        "fnd6_newqeventv110_lol2q",
        "fnd6_newqeventv110_loq",
        "fnd6_newqeventv110_loxdrq",
        "fnd6_newqeventv110_lqpl1q",
        "fnd6_newqeventv110_lseq",
        "fnd6_newqeventv110_ltmibq",
        "fnd6_newqeventv110_lul3q",
        "fnd6_newqeventv110_mibnq",
        "fnd6_newqeventv110_mibq",
        "fnd6_newqeventv110_mibtq",
        "fnd6_newqeventv110_miiq",
        "fnd6_newqeventv110_msaq",
        "fnd6_newqeventv110_nrtxtq",
        "fnd6_newqeventv110_oepf12",
        "fnd6_newqeventv110_oepsxq",
        "fnd6_newqeventv110_optfvgrq",
        "fnd6_newqeventv110_optrfrq",
        "fnd6_newqeventv110_piq",
        "fnd6_newqeventv110_pnc12",
        "fnd6_newqeventv110_pnciapq",
        "fnd6_newqeventv110_pnciaq",
        "fnd6_newqeventv110_pncidpq",
        "fnd6_newqeventv110_pnciepspq",
        "fnd6_newqeventv110_pnciepsq",
        "fnd6_newqeventv110_pncippq",
        "fnd6_newqeventv110_pncipq",
        "fnd6_newqeventv110_pncpd12",
        "fnd6_newqeventv110_pncpdq",
        "fnd6_newqeventv110_pncpeps12",
        "fnd6_newqeventv110_pncpepsq",
        "fnd6_newqeventv110_pncpq",
        "fnd6_newqeventv110_pncwiapq",
        "fnd6_newqeventv110_pncwiaq",
        "fnd6_newqeventv110_pncwidpq",
        "fnd6_newqeventv110_pncwiepq",
        "fnd6_newqeventv110_pncwippq",
        "fnd6_newqeventv110_pncwipq",
        "fnd6_newqeventv110_pnrshoq",
        "fnd6_newqeventv110_ppegtq",
        "fnd6_newqeventv110_ppentq",
        "fnd6_newqeventv110_prcaq",
        "fnd6_newqeventv110_prcd12",
        "fnd6_newqeventv110_prcdq",
        "fnd6_newqeventv110_prce12",
        "fnd6_newqeventv110_prceps12",
        "fnd6_newqeventv110_prcepsq",
        "fnd6_newqeventv110_prcpd12",
        "fnd6_newqeventv110_prcpdq",
        "fnd6_newqeventv110_prcpeps12",
        "fnd6_newqeventv110_prcpepsq",
        "fnd6_newqeventv110_prcpq",
        "fnd6_newqeventv110_prcraq",
        "fnd6_newqeventv110_prshoq",
        "fnd6_newqeventv110_pstknq",
        "fnd6_newqeventv110_pstkq",
        "fnd6_newqeventv110_pstkrq",
        "fnd6_newqeventv110_rcaq",
        "fnd6_newqeventv110_rcdq",
        "fnd6_newqeventv110_rcepsq",
        "fnd6_newqeventv110_rcpq",
        "fnd6_newqeventv110_rdipaq",
        "fnd6_newqeventv110_rdipdq",
        "fnd6_newqeventv110_rdipepsq",
        "fnd6_newqeventv110_rdipq",
        "fnd6_newqeventv110_recdq",
        "fnd6_newqeventv110_rectaq",
        "fnd6_newqeventv110_rectoq",
        "fnd6_newqeventv110_rectrq",
        "fnd6_newqeventv110_reunaq",
        "fnd6_newqeventv110_revtq",
        "fnd6_newqeventv110_rrpq",
        "housing_starts_indicator",
        "iddescriptiontypecoveragedateCoveragealphaCount",
        "implied_minus_realized_volatility_2",
        "implied_option_volatility",
        "industrial_production_indicator",
        "industry_adjusted_doubtful_receivables",
        "industry_rel_ttm_sales_to_ev",
        "industry_relative_book_to_market",
        "industry_relative_ebitda_to_price",
        "industry_relative_eps_to_price",
        "industry_relative_fcf_to_price",
        "industry_relative_return_4w",
        "industry_relative_return_5d",
        "industry_relative_sales_to_price",
        "industry_relative_sales_to_price_v1",
        "inflation_rate_indicator",
        "mdl177_2_globaldevnorthamerica_v502_aci",
        "mdl177_2_globaldevnorthamerica_v502_acp",
        "mdl177_2_globaldevnorthamerica_v502_acqmul",
        "mdl177_2_globaldevnorthamerica_v502_actrtn12m",
        "mdl177_2_globaldevnorthamerica_v502_actrtn18m",
        "mdl177_2_globaldevnorthamerica_v502_actrtn1m",
        "mdl177_2_globaldevnorthamerica_v502_actrtn24m",
        "mdl177_2_globaldevnorthamerica_v502_actrtn2m",
        "mdl177_2_globaldevnorthamerica_v502_actrtn36m",
        "mdl177_2_globaldevnorthamerica_v502_actrtn3m",
        "mdl177_2_globaldevnorthamerica_v502_actrtn60m",
        "mdl177_2_globaldevnorthamerica_v502_actrtn6m",
        "mdl177_2_globaldevnorthamerica_v502_actrtn9m",
        "mdl177_2_globaldevnorthamerica_v502_alpha60m",
        "mdl177_2_globaldevnorthamerica_v502_aspanratio"
    ]
}

# Rebuilt Tiered Fundamental Data Dictionary
FUNDAMENTAL_DATA = {
    "TIER_1": [],
    "TIER_2": [],
    "TIER_3": [],
    "TIER_4": []
}

TIER_1_POOL = []
TIER_2_POOL = []
TIER_3_POOL = []
TIER_4_POOL = []
DATASET_POOL = []
FAST_DATA = ["volume", "vwap", "returns", "close", "open", "high", "low", "cap"]
DATASET_USAGE_TRACKER = {}

def wrap_dataset_by_tier(field):
    """
    If the dataset is in FAST_DATA, it must remain raw.
    Only wrap the dataset in ts_backfill if it is from the Fundamental tiers.
    """
    if field in FAST_DATA:
        return field
    return f"ts_backfill({field}, 60)"

def initialize_dataset_tracker_from_csv():
    """
    Populates DATASET_USAGE_TRACKER from the historical CSV file.
    """
    global DATASET_USAGE_TRACKER
    csv_file = "simulation_results_delay0.csv"
    if not os.path.exists(csv_file):
        return
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
    except Exception as e:
        print(f"Error loading DATASET_USAGE_TRACKER from CSV: {e}")

def initialize_data_tiers():
    """
    Dynamically categorizes all fields from CATEGORIZED_FIELDS into four tiers:
    - TIER_1: Core fundamental ratios (margins, EBITDA, sales, assets, debt, capex, FCF/ROE, cash, etc.) plus new fields
    - TIER_2: Growth rates, eps stability, momentum/expectation scores, and analyst ratings
    - TIER_3: All other fields (raw fnd6_ data, taxes, region exposures, etc.)
    - TIER_4: Alternative data (sentiment, options flow, short interest)
    """
    global FUNDAMENTAL_DATA, TIER_1_POOL, TIER_2_POOL, TIER_3_POOL, TIER_4_POOL, DATASET_POOL
    t2_keywords = ['growth', 'stability', 'trend', 'revision', 'momentum', 'expectation', 'surprise', 'rating', 'score', 'earningmomentum']
    
    t1_set = set()
    t2_set = set()
    t3_set = set()
    t4_set = set()
    
    for cat, fields in CATEGORIZED_FIELDS.items():
        for field in fields:
            fl = field.lower()
            if cat == 'ALTERNATIVE':
                t4_set.add(field)
                continue
                
            is_t2 = False
            if cat == 'GROWTH':
                is_t2 = True
            else:
                cleaned_fl = fl.replace('operating', '')
                if any(k in cleaned_fl for k in t2_keywords):
                    is_t2 = True
                    
            if is_t2:
                t2_set.add(field)
            elif cat == 'OTHER_FUNDAMENTAL':
                t3_set.add(field)
            else:
                t1_set.add(field)
                
    # Merge the new fundamental fields into TIER_1 explicitly
    new_t1_fields = [
        "anl4_afv4_div_high",
        "adj_net_income_median",
        "anl4_adjusted_netincome_ft",
        "anl4_ebit_value",
        "anl4_ebitda_value",
        "anl4_netprofit_value",
        "actual_eps_value_quarterly",
        "sales_estimate_count",
        "earnings_per_share_estimate_count",
        "anl4_afv4_eps_mean",
        "anl4_ptp_flag",
        "anl4_ebitda_flag",
        "anl4_netprofit_flag",
        "anl4_fcf_flag"
    ]
    for field in new_t1_fields:
        t1_set.add(field)
        # Remove from other sets if they exist there to ensure zero overlap
        if field in t2_set:
            t2_set.remove(field)
        if field in t3_set:
            t3_set.remove(field)
        if field in t4_set:
            t4_set.remove(field)
            
    # Remove duplicates and overlaps to ensure clean partitioning
    for f in list(t1_set):
        if f in t2_set:
            t1_set.remove(f)
        if f in t4_set:
            t1_set.remove(f)
    for f in list(t3_set):
        if f in t2_set:
            t3_set.remove(f)
        elif f in t1_set:
            t3_set.remove(f)
        elif f in t4_set:
            t3_set.remove(f)
            
    FUNDAMENTAL_DATA["TIER_1"] = sorted(list(t1_set))
    FUNDAMENTAL_DATA["TIER_2"] = sorted(list(t2_set))
    FUNDAMENTAL_DATA["TIER_3"] = sorted(list(t3_set))
    FUNDAMENTAL_DATA["TIER_4"] = sorted(list(t4_set))
    
    TIER_1_POOL = FUNDAMENTAL_DATA["TIER_1"]
    TIER_2_POOL = FUNDAMENTAL_DATA["TIER_2"]
    TIER_3_POOL = FUNDAMENTAL_DATA["TIER_3"]
    TIER_4_POOL = FUNDAMENTAL_DATA["TIER_4"]
    
    # Sort DATASET_POOL by length descending to prevent substring matching errors during mutation
    DATASET_POOL = sorted(list(set(TIER_1_POOL + TIER_2_POOL + TIER_3_POOL + TIER_4_POOL)), key=len, reverse=True)

def print_meta_data_line(code, universe, goal="Improve Sharpe", metric="None", action="Standard Generation"):
    """
    Parses the final alpha code and prints the [META] debug line.
    Format: [META] Goal: <goal> | Metric: <metric> | Action: <action> | Tier: <T1/T2/T3> | Data: <field_name> | Math: <operator> | Univ: <TOP_X>
    """
    # 1. Identify dataset and tier
    found_ds = "Unknown"
    found_tier = "Unknown"
    for ds in DATASET_POOL:
        if ds in code:
            found_ds = ds
            if ds in TIER_1_POOL:
                found_tier = "T1"
            elif ds in TIER_2_POOL:
                found_tier = "T2"
            elif ds in TIER_3_POOL:
                found_tier = "T3"
            elif ds in TIER_4_POOL:
                found_tier = "T4"
            break
            
    # 2. Identify math operator
    found_math = "Unknown"
    if "zscore(" in code:
        found_math = "zscore"
    elif "rank(" in code:
        found_math = "rank"
    elif "signed_power(" in code or "signedpower(" in code:
        found_math = "signedpower"
    elif "log(" in code:
        found_math = "log"
    elif "decay_linear(" in code or "ts_decay_linear(" in code:
        found_math = "decay_linear"
        
    # Map the action string to the exact wording expected or readable
    action_display = action
    if action == "STRUCTURAL_MUTATION":
        action_display = "Structural Mutation"
    elif action == "TIER_1_SWAP":
        action_display = "Tier 1 Swap"
    elif action == "UNIT_WRAP":
        action_display = "Unit Wrap"
    elif action == "STANDARD":
        action_display = "Feedback Mutation"
        
    print(f"[META] Goal: {goal} | Metric: {metric} | Action: {action_display} | Tier: {found_tier} | Data: {found_ds} | Math: {found_math} | Univ: {universe}")

class GradientEngine:
    def __init__(self, learning_rate=0.15):
        self.lr = learning_rate
        self.ds_weights = {}
        self.op_weights = {
            op: 1.0 for op in [
                "ts_backfill", "zscore", "rank", "signed_power", "log", "decay_linear", 
                "ts_decay_linear", "group_neutralize", "normalize", "ts_mean", "ts_std_dev", 
                "ts_delta", "ts_delay", "ts_arg_max", "ts_arg_min", "ts_rank", "ts_sum", 
                "ts_product", "ts_corr", "ts_covariance", "if_else", "abs", "sign", "scale", 
                "bucket", "group_rank", "trade_when", "divide"
            ]
        }
        
    def initialize_pools(self):
        for ds in DATASET_POOL + FAST_DATA:
            self.ds_weights[ds] = 1.0
            
    def get_weighted_choice(self, pool_list):
        """Picks an item from the provided list based on its learned probability weight."""
        if not pool_list:
            return None
        sub_dict = {k: self.ds_weights.get(k, 1.0) for k in pool_list}
        items = list(sub_dict.keys())
        weights = list(sub_dict.values())
        if sum(weights) <= 0:
            weights = [1.0] * len(weights)
        return random.choices(items, weights=weights, k=1)[0]
        
    def get_weighted_op_choice(self, op_list):
        """Picks an operator from the provided list based on its learned probability weight."""
        if not op_list:
            return None
        sub_dict = {k: self.op_weights.get(k, 1.0) for k in op_list}
        items = list(sub_dict.keys())
        weights = list(sub_dict.values())
        if sum(weights) <= 0:
            weights = [1.0] * len(weights)
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
        top_ds = sorted(self.ds_weights.items(), key=lambda x: x[1], reverse=True)[:5]
        top_op = sorted(self.op_weights.items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"🧠 Gradient Engine Beliefs | Top Data: {[x[0] for x in top_ds]} | Top Ops: {[x[0] for x in top_op]}")

# Initialize globally
optimizer = GradientEngine(learning_rate=0.2)

def pretrain_gradient_engine(optimizer, historical_alphas):
    """Warm-starts the gradient engine weights using successful historical alphas from the CSV."""
    print("⚙️ Warm-Starting Gradient Engine from historical CSV data...")
    count = 0
    for alpha in historical_alphas:
        if alpha.get("status") == "SUCCESS":
            metrics = alpha.get("metrics", {})
            sharpe = metrics.get("sharpe", 0.0) if metrics else 0.0
            if sharpe > 1.0:
                code = alpha.get("code")
                if code:
                    # Extract datasets and operators
                    get_alpha_components(code)
                    optimizer.calculate_gradient_step(alpha_string=code, new_sharpe=sharpe, old_sharpe=1.0)
                    count += 1
    print(f"✅ Pre-trained optimizer on {count} successful historical alphas (Sharpe > 1.0).")

def get_alpha_components(code):
    """
    Extracts all unique datasets and mathematical operators from the alpha code.
    """
    datasets = set()
    # Check all items in DATASET_POOL (sorted by length descending in initialize_data_tiers)
    for ds in DATASET_POOL:
        if re.search(r'\b' + re.escape(ds) + r'\b', code):
            datasets.add(ds)
            
    # Add price/volume fields for formulaic alphas
    price_fields = ["open", "close", "high", "low", "volume", "vwap", "returns", "cap"]
    for pf in price_fields:
        if re.search(r'\b' + re.escape(pf) + r'\b', code):
            datasets.add(pf)
    adv_matches = re.findall(r'\badv\d+\b', code)
    for am in adv_matches:
        datasets.add(am)
        
    # Extract operators
    operators = set()
    known_operators = [
        "ts_backfill", "zscore", "rank", "signed_power", "log", "decay_linear", 
        "ts_decay_linear", "group_neutralize", "normalize", "ts_mean", "ts_std_dev", 
        "ts_delta", "ts_delay", "ts_arg_max", "ts_arg_min", "ts_rank", "ts_sum", 
        "ts_product", "ts_corr", "ts_covariance", "if_else", "abs", "sign", "scale", 
        "bucket", "group_rank", "trade_when", "divide"
    ]
    for op in known_operators:
        if re.search(r'\b' + re.escape(op) + r'\b', code):
            operators.add(op)
            
    # Add arithmetic symbols
    arithmetics = ["+", "-", "*", "/", "<", ">", "==", "<=", ">="]
    for ar in arithmetics:
        if ar in code:
            operators.add(ar)
            
    return datasets.union(operators)

def is_cross_correlated(code, history_buffer):
    """
    Compares the new alpha code against the history buffer.
    If it shares > 70% of datasets and operators, returns True, similarity score, and the correlated alpha.
    """
    if not history_buffer:
        return False, 0.0, None
        
    new_comps = get_alpha_components(code)
    if not new_comps:
        return False, 0.0, None
        
    for hist_code in history_buffer:
        hist_comps = get_alpha_components(hist_code)
        if not hist_comps:
            continue
        intersection = new_comps.intersection(hist_comps)
        # Compute similarity relative to both sets
        sim_new = len(intersection) / len(new_comps) if len(new_comps) > 0 else 0.0
        sim_hist = len(intersection) / len(hist_comps) if len(hist_comps) > 0 else 0.0
        max_sim = max(sim_new, sim_hist)
        if max_sim > 0.70:
            return True, max_sim, hist_code
            
    return False, 0.0, None

# Populate Tiers immediately on startup
initialize_data_tiers()
initialize_dataset_tracker_from_csv()

def get_group_neutralize_bounds(code):
    """
    Finds the start index, end index, and internal content of the outermost group_neutralize block.
    """
    idx = code.find("group_neutralize(")
    if idx == -1:
        return None
        
    open_count = 1
    start_args = idx + len("group_neutralize(")
    i = start_args
    while i < len(code) and open_count > 0:
        if code[i] == '(':
            open_count += 1
        elif code[i] == ')':
            open_count -= 1
        i += 1
        
    if open_count == 0:
        end_idx = i
        content = code[start_args:end_idx-1]
        return idx, end_idx, content
    return None

def split_arguments(content):
    """
    Splits content by the last top-level comma.
    """
    paren_depth = 0
    bracket_depth = 0
    quote_char = None
    last_comma_idx = -1
    
    for idx, char in enumerate(content):
        if quote_char:
            if char == quote_char:
                quote_char = None
            continue
        elif char in ('"', "'"):
            quote_char = char
            continue
            
        if char == '(':
            paren_depth += 1
        elif char == ')':
            paren_depth -= 1
        elif char == '[':
            bracket_depth += 1
        elif char == ']':
            bracket_depth -= 1
        elif char == ',' and paren_depth == 0 and bracket_depth == 0:
            last_comma_idx = idx
            
    if last_comma_idx != -1:
        arg1 = content[:last_comma_idx].strip()
        arg2 = content[last_comma_idx+1:].strip()
        return arg1, arg2
    return content, ""

def extract_core_expression(code):
    """
    Recursively extracts the core expression inside group_neutralize wrappers.
    """
    bounds = get_group_neutralize_bounds(code)
    if not bounds:
        return code
    start_idx, end_idx, content = bounds
    arg1, arg2 = split_arguments(content)
    return extract_core_expression(arg1)

def wrap_in_rank(expr):
    expr = expr.strip()
    if expr.startswith("rank(") and expr.endswith(")"):
        depth = 0
        is_outer = True
        for i, c in enumerate(expr):
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0 and i < len(expr) - 1:
                    is_outer = False
                    break
        if is_outer:
            return expr
    return f"rank({expr})"

def replace_operator_windows(code, target_funcs, window_replace_fn):
    res = []
    i = 0
    while i < len(code):
        matched_func = None
        for func in target_funcs:
            if code[i:].startswith(func + "("):
                matched_func = func
                break
        
        if matched_func:
            start_args = i + len(matched_func) + 1
            paren_depth = 1
            j = start_args
            while j < len(code) and paren_depth > 0:
                if code[j] == '(':
                    paren_depth += 1
                elif code[j] == ')':
                    paren_depth -= 1
                j += 1
            
            if paren_depth == 0:
                args_content = code[start_args:j-1]
                depth = 0
                comma_idx = -1
                for idx_char, char in enumerate(args_content):
                    if char == '(':
                        depth += 1
                    elif char == ')':
                        depth -= 1
                    elif char == ',' and depth == 0:
                        comma_idx = idx_char
                
                if comma_idx != -1:
                    expr_part = args_content[:comma_idx].strip()
                    window_part = args_content[comma_idx+1:].strip()
                    
                    try:
                        window_val = int(window_part)
                        new_window = window_replace_fn(matched_func, window_val)
                        expr_clean = replace_operator_windows(expr_part, target_funcs, window_replace_fn)
                        replaced_call = f"{matched_func}({expr_clean}, {new_window})"
                        res.append(replaced_call)
                        i = j
                        continue
                    except ValueError:
                        pass
        
        res.append(code[i])
        i += 1
        
    return "".join(res)

def cap_decay_windows(code):
    def replace_fn(func, val):
        return min(val, 10)
    return replace_operator_windows(code, ["ts_decay_linear", "decay_linear"], replace_fn)

def enforce_group_neutralize_rank(code):
    bounds = get_group_neutralize_bounds(code)
    if not bounds:
        return code
    start_idx, end_idx, content = bounds
    arg1, arg2 = split_arguments(content)
    arg1_clean = enforce_group_neutralize_rank(arg1)
    arg1_wrapped = wrap_in_rank(arg1_clean)
    pre = code[:start_idx]
    post = code[end_idx:]
    return pre + f"group_neutralize({arg1_wrapped}, {arg2})" + post

def get_elite_variants(code):
    """
    Generates three neutralization variants for an elite candidate.
    """
    bounds = get_group_neutralize_bounds(code)
    if not bounds:
        core = code
        variant_a = f"group_neutralize({wrap_in_rank(core)}, industry)"
        variant_b = f"group_neutralize({wrap_in_rank(f'group_neutralize({wrap_in_rank(core)}, industry)')}, bucket(rank(cap), range=\"0, 1, 0.1\"))"
        variant_c = f"group_neutralize({wrap_in_rank(core)}, bucket(rank(ts_mean(volume, 20)), range=\"0, 1, 0.1\"))"
        return [cap_decay_windows(enforce_group_neutralize_rank(v)) for v in [variant_a, variant_b, variant_c]]
        
    start_idx, end_idx, content = bounds
    core = extract_core_expression(code)
    
    pre = code[:start_idx]
    post = code[end_idx:]
    
    var_a_neutralize = f"group_neutralize({wrap_in_rank(core)}, industry)"
    var_b_neutralize = f"group_neutralize({wrap_in_rank(f'group_neutralize({wrap_in_rank(core)}, industry)')}, bucket(rank(cap), range=\"0, 1, 0.1\"))"
    var_c_neutralize = f"group_neutralize({wrap_in_rank(core)}, bucket(rank(ts_mean(volume, 20)), range=\"0, 1, 0.1\"))"
    
    return [
        cap_decay_windows(enforce_group_neutralize_rank(pre + var_a_neutralize + post)),
        cap_decay_windows(enforce_group_neutralize_rank(pre + var_b_neutralize + post)),
        cap_decay_windows(enforce_group_neutralize_rank(pre + var_c_neutralize + post))
    ]

# ==============================================================================
# ENGINE 1: FUNDAMENTAL ENGINE FUNCTIONS
# ==============================================================================

def select_thematic_field(recent_datasets, category=None):
    """
    Selects a category and a field from it, respecting the recent_datasets forbidden list.
    If category is provided, selects from that specific category.
    """
    if category is None:
        categories = list(CATEGORIZED_FIELDS.keys())
        category = random.choice(categories)
        
    fields = CATEGORIZED_FIELDS[category]
    available = [f for f in fields if f not in recent_datasets]
    
    if not available:
        available = fields
        
    return category, random.choice(available)

def generate_event_driven_alpha(recent_datasets=None, history_buffer=None, universe="TOP3000"):
    """
    Generates event-driven alpha expressions using the trade_when(condition, target_expression, -1) operator.
    Trades only during specific volatility or volume events.
    """
    if recent_datasets is None:
        recent_datasets = []
        
    # Get a rare dataset from bottom 20%
    sorted_dataset_pool = sorted(DATASET_POOL, key=lambda f: DATASET_USAGE_TRACKER.get(f, 0))
    N = max(1, int(len(sorted_dataset_pool) * 0.20))
    rare_pool = [f for f in sorted_dataset_pool[:N] if f not in recent_datasets]
    if not rare_pool:
        rare_pool = sorted_dataset_pool[:N]
    x = optimizer.get_weighted_choice(rare_pool)
    
    # Target expression: rank or zscore of wrap_dataset_by_tier(x)
    op = optimizer.get_weighted_op_choice(["rank", "zscore"])
    target_expr = f"{op}({wrap_dataset_by_tier(x)})"
    
    # Volatility or volume conditions
    conditions = [
        "volume > (ts_mean(volume, 20) * 1.5)",
        "ts_std_dev(returns, 10) > 0.05",
        "abs(returns) > (ts_std_dev(returns, 20) * 2.0)",
        "ts_delta(close, 5) > ts_std_dev(close, 20)"
    ]
    condition = random.choice(conditions)
    
    # Construct trade_when expression
    expr = f"trade_when({condition}, {target_expr}, -1)"
    
    # Apply group neutralization: replace the standard group with the restored buckets list
    group = random.choice(["subindustry", "industry", 'bucket(rank(cap), range="0, 1, 0.1")', 'bucket(rank(ts_mean(volume, 20)), range="0, 1, 0.1")'])
    expr = f"group_neutralize({wrap_in_rank(expr)}, {group})"
    
    # Wrap in normalize(ts_decay_linear())
    decay_window = random.choice([2, 3, 5, 8, 10])
    expr = f"normalize(ts_decay_linear({expr}, {decay_window}))"
    
    # Random reversion sign
    if random.random() < 0.5:
        expr = f"-1 * {expr}"
        
    # Anti-Cloning check (re-mutation)
    attempts = 0
    while expr in history_buffer and attempts < 10:
        print(f"⚠️ Generated event-driven expression already in HISTORY_BUFFER: {expr}. Forcing structural re-mutation...")
        if random.random() < 0.5:
            expr = mutate_structure(expr, recent_datasets)
        else:
            expr = mutate_dataset(expr, recent_datasets)
        attempts += 1
        
    return cap_decay_windows(expr)

def generate_alpha_expression(recent_datasets=None, history_buffer=None, universe="TOP3000"):
    """
    Generates alpha expressions using weighted data tiers, core math blocks, and anti-cloning.
    Routes 30% of calls to generate_event_driven_alpha().
    """
    if random.random() < 0.30:
        return generate_event_driven_alpha(recent_datasets, history_buffer, universe)

    if recent_datasets is None:
        recent_datasets = []
    if history_buffer is None:
        history_buffer = []
        
    # 1. Tier selection (weighted)
    tier = random.choices(["TIER_1", "TIER_2", "TIER_3"], weights=[0.70, 0.20, 0.10], k=1)[0]
    pool = FUNDAMENTAL_DATA[tier]
        
    available = [f for f in pool if f not in recent_datasets]
    if not available:
        available = pool
        
    # Sort available by usage count ascending and prioritize bottom 20%
    available_sorted = sorted(available, key=lambda f: DATASET_USAGE_TRACKER.get(f, 0))
    cutoff = max(1, int(len(available_sorted) * 0.20))
    x = optimizer.get_weighted_choice(available_sorted[:cutoff])
    x_wrapped = wrap_dataset_by_tier(x)
    
    # 2. Core Math Block selection
    # Math operators strictly restricted to rank, zscore, ts_delta, ts_rank (ts_corr removed)
    if random.random() < 0.75:
        # Contrarian Value vs Price structure
        fundamental_field = x
        fundamental_wrapped = wrap_dataset_by_tier(fundamental_field)
        fast_field = optimizer.get_weighted_choice(["close", "volume", "vwap", "returns"])
        fast_wrapped = wrap_dataset_by_tier(fast_field)
        expr = f"rank(ts_rank({fundamental_wrapped}, 90)) - rank(ts_rank({fast_wrapped}, 20))"
    else:
        # Other Mean-Reversion operators
        math_op = optimizer.get_weighted_op_choice(["zscore", "rank", "ts_delta", "ts_rank"])
        if math_op == "zscore":
            expr = f"zscore({x_wrapped})"
        elif math_op == "rank":
            expr = f"rank({x_wrapped})"
        elif math_op == "ts_delta":
            standard_op = optimizer.get_weighted_op_choice(["rank", "zscore"])
            expr = f"ts_delta({standard_op}({x_wrapped}), {random.choice([5, 10])})"
        else:  # ts_rank
            expr = f"ts_rank({x_wrapped}, {random.choice([20, 60, 90])})"
        
    # Apply group neutralization: 70% custom bucket, 30% group neutralization
    if random.random() < 0.70:
        bucket_op = random.choice([
            'bucket(rank(cap), range="0, 1, 0.1")',
            'bucket(rank(ts_mean(volume, 20)), range="0, 1, 0.1")'
        ])
        expr = f"group_neutralize({wrap_in_rank(expr)}, {bucket_op})"
    else:
        group = random.choice(["subindustry", "industry", 'bucket(rank(cap), range="0, 1, 0.1")', 'bucket(rank(ts_mean(volume, 20)), range="0, 1, 0.1")'])
        expr = f"group_neutralize({wrap_in_rank(expr)}, {group})"
    
    # Wrap in normalize(ts_decay_linear())
    decay_window = random.choice([2, 3, 5, 8, 10])
    expr = f"normalize(ts_decay_linear({expr}, {decay_window}))"
        
    # Random reversion test
    if random.random() < 0.5:
        expr = f"-1 * {expr}"
        
    # 3. Anti-Cloning check (re-mutation)
    attempts = 0
    while expr in history_buffer and attempts < 10:
        print(f"⚠️ Generated expression already in HISTORY_BUFFER: {expr}. Forcing structural re-mutation...")
        if random.random() < 0.5:
            expr = mutate_structure(expr, recent_datasets)
        else:
            expr = mutate_dataset(expr, recent_datasets)
        attempts += 1
        
    return cap_decay_windows(expr)

# ==============================================================================
# ENGINE 2: 101 FORMULAIC ALPHAS ENGINE FUNCTIONS
# ==============================================================================

def get_random_terminal():
    terminals = ["open", "close", "high", "low", "volume", "vwap", "returns", "cap"]
    if random.random() < 0.3:
        window = random.choice([20, 60, 120, 150, 180])
        return f"adv{window}"
    return random.choice(terminals)

def generate_formulaic_expression(depth=0):
    """
    Generates nested formulaic expressions matching the style of the 101 Formulaic Alphas PDF
    using verified WorldQuant BRAIN FastExpr operators.
    """
    if depth >= 2:
        return get_random_terminal()
        
    op_type = random.choice(["unary", "binary_ts", "binary_two_expr", "arithmetic", "ternary"])
    
    if op_type == "unary":
        op = random.choice(["rank", "scale", "log", "abs", "sign"])
        inner = generate_formulaic_expression(depth + 1)
        if op == "log":
            return f"log(abs({inner}) + 1e-5)"
        return f"{op}({inner})"
        
    elif op_type == "binary_ts":
        op = random.choice([
            "ts_delay", "ts_delta", "ts_decay_linear", "group_neutralize",
            "ts_arg_max", "ts_arg_min", "ts_rank", "ts_sum", "ts_std_dev",
            "ts_product", "ts_mean"
        ])
        inner = generate_formulaic_expression(depth + 1)
        if op == "group_neutralize":
            group = random.choice(["subindustry", "industry", 'bucket(rank(cap), range="0, 1, 0.1")', 'bucket(rank(ts_mean(volume, 20)), range="0, 1, 0.1")'])
            return f"group_neutralize({wrap_in_rank(inner)}, {group})"
        elif op == "ts_decay_linear":
            window = random.choice([2, 3, 5, 8, 10])
            return f"ts_decay_linear({inner}, {window})"
        else:
            window = random.choice([2, 5, 10, 20, 30])
            return f"{op}({inner}, {window})"
            
    elif op_type == "binary_two_expr":
        op = random.choice(["ts_corr", "ts_covariance"])
        inner1 = generate_formulaic_expression(depth + 1)
        inner2 = generate_formulaic_expression(depth + 1)
        window = random.choice([5, 10, 20, 30])
        return f"{op}({inner1}, {inner2}, {window})"
        
    elif op_type == "arithmetic":
        op = random.choice(["+", "-", "*", "/"])
        inner1 = generate_formulaic_expression(depth + 1)
        inner2 = generate_formulaic_expression(depth + 1)
        if op == "/":
            return f"({inner1} / (abs({inner2}) + 1e-5))"
        return f"({inner1} {op} {inner2})"
        
    else:  # ternary
        cond = random.choice(["returns < 0", "close > open", "volume > adv20", "high > low"])
        if random.random() < 0.5:
            cond = cond.replace("returns", get_random_terminal())
            cond = cond.replace("close", get_random_terminal())
            cond = cond.replace("open", get_random_terminal())
            cond = cond.replace("volume", get_random_terminal())
        expr1 = generate_formulaic_expression(depth + 1)
        expr2 = generate_formulaic_expression(depth + 1)
        return f"if_else({cond}, {expr1}, {expr2})"

def mutate_formulaic_alpha(code, metrics=None):
    """
    Mutator optimized for the Formulaic Engine.
    Swaps windows, terminals, operators, or wraps expression in a new operator.
    Supports feedback-driven mutations using metrics/failed_checks.
    """
    failed_checks = metrics.get("failed_checks", []) if metrics else []
    if "CONCENTRATED_WEIGHT" in failed_checks:
        print("💡 Feedback-driven formulaic mutation: Concentrated Weight. Wrapping expression in group_neutralize.")
        if "group_neutralize(" not in code:
            group = random.choice(["subindustry", "industry", 'bucket(rank(cap), range="0, 1, 0.1")', 'bucket(rank(ts_mean(volume, 20)), range="0, 1, 0.1")'])
            return cap_decay_windows(f"group_neutralize({wrap_in_rank(code)}, {group})")
            
    original_code = code
    for attempt in range(5):
        r = random.random()
        if r < 0.30:
            def repl(m):
                val = int(m.group(2))
                new_val = random.choice([2, 5, 10, 15, 20, 30])
                return f"{m.group(1)}{new_val}{m.group(3)}"
            code = re.sub(r'(,\s*)(\d+)(\s*\))', repl, code)
        elif r < 0.60:
            terminals = ["open", "close", "high", "low", "volume", "vwap", "returns", "cap", "adv20", "adv60", "adv120", "adv180"]
            found_terminals = [t for t in terminals if t in code]
            if found_terminals:
                target = random.choice(found_terminals)
                remaining = [t for t in terminals if t != target]
                replacement = random.choice(remaining)
                code = code.replace(target, replacement)
        elif r < 0.85:
            ts_ops = ["ts_delay", "ts_delta", "ts_decay_linear", "ts_arg_max", "ts_arg_min", "ts_rank", "ts_sum", "ts_std_dev", "ts_product", "ts_mean"]
            found_ts_ops = [op for op in ts_ops if f"{op}(" in code.lower()]
            if found_ts_ops:
                target = random.choice(found_ts_ops)
                remaining = [op for op in ts_ops if op != target]
                replacement = random.choice(remaining)
                pattern = re.compile(r'\b' + re.escape(target) + r'\b', re.IGNORECASE)
                code = pattern.sub(replacement, code)
            
            groups = ["subindustry", "industry", 'bucket(rank(cap), range="0, 1, 0.1")', 'bucket(rank(ts_mean(volume, 20)), range="0, 1, 0.1")']
            found_groups = [g for g in groups if g in code]
            if found_groups:
                target = random.choice(found_groups)
                remaining = [g for g in groups if g != target]
                replacement = random.choice(remaining)
                code = code.replace(target, replacement)
                
            if "ts_corr(" in code.lower():
                code = re.sub(r'\bts_corr\b', 'ts_covariance', code, flags=re.IGNORECASE)
            elif "ts_covariance(" in code.lower():
                code = re.sub(r'\bts_covariance\b', 'ts_corr', code, flags=re.IGNORECASE)
        else:
            op = random.choice(["-1 * ({})", "rank({})", "scale({})", "abs({})", "sign({})"])
            code = op.format(code)
            
        if code != original_code:
            return cap_decay_windows(code)
            
    op = random.choice(["-1 * ({})", "rank({})", "scale({})", "abs({})", "sign({})"])
    return cap_decay_windows(op.format(original_code))

# ==============================================================================
# MUTATOR FUNCTIONS FOR FUNDAMENTAL ENGINE
# ==============================================================================

def hide_backfill(code):
    return re.sub(r'\bts_backfill\(([^,)]+),\s*60\)', r'__BACKFILL_\1__', code)

def restore_backfill(code):
    return re.sub(r'__BACKFILL_([a-zA-Z0-9_]+)__', r'ts_backfill(\1, 60)', code)

def increase_decay_window(code):
    """
    Finds the ts_decay_linear or decay_linear operator and increases the decay window value to reduce trading turnover.
    """
    def replace_fn(func, val):
        larger_windows = [w for w in [2, 3, 5, 8, 10] if w > val]
        return random.choice(larger_windows) if larger_windows else 10
    return replace_operator_windows(code, ["ts_decay_linear", "decay_linear"], replace_fn)

def increase_lookback_window(code):
    """
    Finds the ts_mean, ts_delta, or ts_std_dev operator and increases the smoothing window.
    If it is a zscore operator, converts it to rank(ts_mean(base, 10)) to introduce smoothing.
    """
    target_funcs = ["ts_mean", "ts_delta", "ts_std_dev"]
    has_changed = [False]
    def replace_fn(func, val):
        larger_windows = [w for w in [10, 20, 30, 40, 60] if w > val]
        new_val = random.choice(larger_windows) if larger_windows else 60
        if new_val != val:
            has_changed[0] = True
        return new_val
        
    new_code = replace_operator_windows(code, target_funcs, replace_fn)
    if has_changed[0]:
        return new_code
        
    # If no lookback window was changed, check if it contains zscore and rewrite it
    start = 0
    while True:
        idx = code.find("zscore(", start)
        if idx == -1:
            break
        open_count = 1
        i = idx + len("zscore(")
        while i < len(code) and open_count > 0:
            if code[i] == '(':
                open_count += 1
            elif code[i] == ')':
                open_count -= 1
            if open_count == 0:
                break
            i += 1
        if open_count == 0:
            inner = code[idx + len("zscore("):i]
            replacement = f"rank(ts_mean({inner}, 10))"
            code = code[:idx] + replacement + code[i + 1:]
            start = idx + len(replacement)
        else:
            start = idx + 1
    return code

def mutate_neutralization_group(code):
    """
    Finds group_neutralize or group_rank operator and swaps the neutralization classification category,
    respecting the 70% bucket / 30% group split.
    """
    idx = code.find("group_neutralize(")
    func_name = "group_neutralize"
    if idx == -1:
        idx = code.find("group_rank(")
        func_name = "group_rank"
        if idx == -1:
            return code
            
    open_count = 1
    start_args = idx + len(func_name) + 1
    i = start_args
    while i < len(code) and open_count > 0:
        if code[i] == '(':
            open_count += 1
        elif code[i] == ')':
            open_count -= 1
        i += 1
        
    if open_count == 0:
        start_idx = idx
        end_idx = i
        content = code[start_args:end_idx-1]
        arg1, arg2 = split_arguments(content)
        
        # 70% chance of custom bucket, 30% chance of group neutralization
        if random.random() < 0.70:
            new_group = random.choice([
                'bucket(rank(cap), range="0, 1, 0.1")',
                'bucket(rank(ts_mean(volume, 20)), range="0, 1, 0.1")'
            ])
        else:
            groups = ["subindustry", "industry", 'bucket(rank(cap), range="0, 1, 0.1")', 'bucket(rank(ts_mean(volume, 20)), range="0, 1, 0.1")']
            if arg2 in groups:
                remaining = [g for g in groups if g != arg2]
                new_group = random.choice(remaining) if remaining else arg2
            else:
                new_group = random.choice(groups)
                
        if func_name == "group_neutralize":
            new_neutralize = f"{func_name}({wrap_in_rank(arg1)}, {new_group})"
        else:
            new_neutralize = f"{func_name}({arg1}, {new_group})"
        return code[:start_idx] + new_neutralize + code[end_idx:]
    return code

def flip_alpha_sign(code):
    """
    Toggles the reversion sign of the alpha signal.
    """
    if code.startswith("-1 * "):
        return code[5:]
    else:
        return f"-1 * {code}"

def mutate_structure(code, recent_datasets=None, generate_variants=False):
    """
    Finds the core structural block in the code and replaces it with a different one.
    Enforces rank/zscore wrapping before mathematical arithmetic in structural blocks.
    """
    if generate_variants:
        return get_elite_variants(code)
        
    if recent_datasets is None:
        recent_datasets = []
        
    # Find all datasets present in the code
    found_ds = []
    for ds in DATASET_POOL:
        if ds in code:
            found_ds.append(ds)
            
    if not found_ds:
        return code
        
    x = found_ds[0]
    if len(found_ds) > 1:
        y = found_ds[1]
    else:
        # Choose a different dataset y
        available = [ds for ds in DATASET_POOL if ds != x and ds not in recent_datasets]
        if not available:
            available = [ds for ds in DATASET_POOL if ds != x]
        y = random.choice(available) if available else x
        
    d = random.choice([5, 10, 20])
    
    # Wrap base datasets using wrap_dataset_by_tier for data continuity and lookback requirements
    x_wrapped = wrap_dataset_by_tier(x)
    y_wrapped = wrap_dataset_by_tier(y)
    
    # Generate new structural block: restricted to contrarian, ts_rank, and delta (ts_corr removed)
    if random.random() < 0.75:
        block_type = "contrarian"
    else:
        block_type = random.choice(["ts_rank", "delta"])
    
    # Helper to find field category
    def get_field_category(field):
        for cat, fields in CATEGORIZED_FIELDS.items():
            if field in fields:
                return cat
        return "OTHER_FUNDAMENTAL"
        
    cat1 = get_field_category(x)
    cat2 = get_field_category(y)
    
    if block_type == "contrarian":
        fundamental_wrapped = x_wrapped
        fast_field = random.choice(["close", "volume", "vwap", "returns"])
        fast_wrapped = wrap_dataset_by_tier(fast_field)
        new_block = f"rank(ts_rank({fundamental_wrapped}, 90)) - rank(ts_rank({fast_wrapped}, 20))"
        operator = "Contrarian_Value_vs_Price"
        mode = "Contrarian"
        category_str = f"{cat1} vs Price"
        tool_str = f"{x} & {fast_field}"
    elif block_type == "ts_rank":
        new_block = f"ts_rank({x_wrapped}, {random.choice([20, 60, 90])})"
        operator = "Ts_Rank"
        mode = "TsRank"
        category_str = cat1
        tool_str = x
    else: # delta
        op_x = random.choice(["rank", "zscore"])
        new_block = f"ts_delta({op_x}({x_wrapped}), {d})"
        operator = "Ts_Delta"
        mode = "Delta"
        category_str = cat1
        tool_str = x
        
    print(f"[DEBUG] [MUTATION] Category: {category_str} | Tool: {tool_str} | Operator: {operator} | Mode: {mode}")
        
    # Enforce 70% custom bucket, 30% standard group split
    if random.random() < 0.70:
        group = random.choice([
            'bucket(rank(cap), range="0, 1, 0.1")',
            'bucket(rank(ts_mean(volume, 20)), range="0, 1, 0.1")'
        ])
    else:
        group = random.choice(["subindustry", "industry", 'bucket(rank(cap), range="0, 1, 0.1")', 'bucket(rank(ts_mean(volume, 20)), range="0, 1, 0.1")'])
    
    decay_match = re.search(r'\b(ts_decay_linear|decay_linear)\((.+?),\s*(\d+)\)', code, re.IGNORECASE)
    if decay_match:
        decay_window = min(int(decay_match.group(3)), 10)
    else:
        decay_window = random.choice([2, 3, 5, 8, 10])
    decay_func = "ts_decay_linear"
    
    # Rebuild
    new_code = f"group_neutralize({wrap_in_rank(new_block)}, {group})"
    new_code = f"normalize({decay_func}({new_code}, {decay_window}))"
    
    if code.startswith("-1 * "):
        new_code = f"-1 * {new_code}"
        
    return cap_decay_windows(new_code)

def mutate_dataset(code, recent_datasets=None):
    """
    Swaps the premium dataset string present in the code with a different one from the pool,
    respecting dataset rotation.
    """
    if recent_datasets is None:
        recent_datasets = []
        
    current_ds = None
    for ds in DATASET_POOL:
        if ds in code:
            current_ds = ds
            break
            
    if current_ds:
        # Filter available by rotation
        available = [ds for ds in DATASET_POOL if ds != current_ds and ds not in recent_datasets]
        if not available:
            available = [ds for ds in DATASET_POOL if ds != current_ds]
            
        if available:
            new_ds = optimizer.get_weighted_choice(available)
            return code.replace(current_ds, new_ds)
            
    return code

def mutate_time_horizons(code):
    """
    Mutates lookback windows (ts_mean, ts_delta, ts_std_dev, ts_arg_max, ts_arg_min, ts_rank, decay_linear)
    without corrupting numbers inside the dataset strings.
    """
    target_funcs = ["ts_mean", "ts_delta", "ts_std_dev", "ts_arg_max", "ts_arg_min", "ts_rank", "ts_decay_linear", "decay_linear"]
    def replace_fn(func, val):
        if func in ["ts_decay_linear", "decay_linear"]:
            return random.choice([2, 3, 5, 8, 10])
        elif func == "ts_rank":
            return random.choice([20, 60, 90])
        else:
            return random.choice([3, 5, 10, 20])
    return cap_decay_windows(replace_operator_windows(code, target_funcs, replace_fn))

def mutate_time_horizon_shift(code):
    """
    Finds any ts_ operators (like ts_mean, ts_delta, ts_std_dev, ts_rank, decay_linear)
    and radically shifts the window (e.g., if <= 10 -> 60, if >= 40 -> 5).
    """
    target_funcs = ["ts_mean", "ts_delta", "ts_std_dev", "ts_arg_max", "ts_arg_min", "ts_rank", "ts_decay_linear", "decay_linear"]
    def replace_fn(func, val):
        if func in ["ts_decay_linear", "decay_linear"]:
            if val <= 5:
                return 10
            else:
                return random.choice([2, 3])
        elif func == "ts_rank":
            if val <= 20:
                return 90
            elif val >= 90:
                return 20
            else:
                return random.choice([20, 90])
        else:
            if val <= 10:
                return 60
            elif val >= 40:
                return 5
            else:
                return random.choice([5, 60])
    return cap_decay_windows(replace_operator_windows(code, target_funcs, replace_fn))

def mutate_orthogonal_data_swap(code):
    """
    Finds the current dataset in the alpha code. Check which category it belongs to in CATEGORIZED_FIELDS.
    Forces a swap to a dataset in a completely different category.
    """
    found_ds = []
    for ds in DATASET_POOL:
        if ds in code:
            found_ds.append(ds)
            
    if not found_ds:
        return code
        
    current_ds = found_ds[0]
    
    current_category = None
    for cat, fields in CATEGORIZED_FIELDS.items():
        if current_ds in fields:
            current_category = cat
            break
            
    other_categories = [cat for cat in CATEGORIZED_FIELDS.keys() if cat != current_category]
    if not other_categories:
        other_categories = list(CATEGORIZED_FIELDS.keys())
        
    target_category = random.choice(other_categories)
    target_fields = CATEGORIZED_FIELDS[target_category]
    
    valid_targets = [f for f in target_fields if f in DATASET_POOL and f != current_ds]
    if not valid_targets:
        valid_targets = [f for f in DATASET_POOL if f != current_ds]
        
    if not valid_targets:
        return code
        
    new_ds = random.choice(valid_targets)
    return code.replace(current_ds, new_ds)

def mutate_non_linear_wrap(code):
    """
    Wraps the core data block (ts_backfill(field, 60)) in rank() or zscore()
    to break linear correlation.
    """
    pattern = r'\bts_backfill\(([a-zA-Z0-9_]+),\s*60\)'
    
    wrap_op = random.choice([
        "rank({})",
        "zscore({})"
    ])
    
    match = re.search(pattern, code)
    if match:
        start, end = match.span()
        # Perform the wrap on the first match
        wrapped = wrap_op.format(match.group(0))
        return code[:start] + wrapped + code[end:]
        
    return code

def mutate_cross_domain_interaction(code):
    """
    Constructs an interactive signal multiplying a Tier 1 (Fundamental) dataset 
    with a Tier 4 (Alternative) dataset, wrapped in a bucket-neutralized, decay-linear structure.
    """
    t1_field = optimizer.get_weighted_choice(TIER_1_POOL)
    t4_field = optimizer.get_weighted_choice(TIER_4_POOL)
    
    # Construct interaction core
    core = f"rank(ts_backfill({t1_field}, 60)) * rank(ts_backfill({t4_field}, 60))"
    
    # 70% bucket neutralization, 30% group neutralization
    if random.random() < 0.70:
        bucket_op = random.choice([
            'bucket(rank(cap), range="0, 1, 0.1")',
            'bucket(rank(ts_mean(volume, 20)), range="0, 1, 0.1")'
        ])
        neutralized = f"group_neutralize({wrap_in_rank(core)}, {bucket_op})"
        neut_label = bucket_op
    else:
        group = random.choice(["subindustry", "industry", 'bucket(rank(cap), range="0, 1, 0.1")', 'bucket(rank(ts_mean(volume, 20)), range="0, 1, 0.1")'])
        neutralized = f"group_neutralize({wrap_in_rank(core)}, {group})"
        neut_label = group
    
    # Decay window wrap
    decay_window = random.choice([2, 3, 5, 8, 10])
    expr = f"normalize(ts_decay_linear({neutralized}, {decay_window}))"
        
    # Reversion test
    if random.random() < 0.5:
        expr = f"-1 * {expr}"
        
    print(f"[MUTATION] [CROSS-DOMAIN] Multiplied {t1_field} x {t4_field} with neutralization {neut_label}")
    return cap_decay_windows(expr)

def get_mutation_direction(metrics):
    """
    DIAGNOSTIC_ENGINE: Analyzes checks and performance metrics to determine optimization direction.
    """
    if not metrics:
        return {"action": "STANDARD", "metric": "None", "goal": "Improve Sharpe"}
        
    failed_checks = metrics.get("failed_checks", [])
    if isinstance(failed_checks, str):
        failed_checks = [failed_checks]
        
    # Check direct metrics for self correlation
    self_corr_val = metrics.get("self_correlation") or metrics.get("selfCorrelation")
    if self_corr_val is not None:
        try:
            val = float(self_corr_val)
            if val > 0.95:
                return {
                    "action": "SCRAP_AND_REBUILD",
                    "metric": f"Self-Correlation ({val:.4f})",
                    "goal": "Reduce Self-Correlation"
                }
            elif val > 0.85:
                return {
                    "action": "TIME_HORIZON_SHIFT",
                    "metric": f"Self-Correlation ({val:.4f})",
                    "goal": "Reduce Self-Correlation"
                }
            elif val > 0.70:
                action = random.choice(["ORTHOGONAL_DATA_SWAP", "NON_LINEAR_WRAP"])
                return {
                    "action": action,
                    "metric": f"Self-Correlation ({val:.4f})",
                    "goal": "Reduce Self-Correlation"
                }
        except (ValueError, TypeError):
            pass
            
    # Check failed_checks for self correlation as fallback
    has_self_corr = False
    for check in failed_checks:
        if "self" in check.lower() and "corr" in check.lower():
            has_self_corr = True
            break
            
    if has_self_corr:
        return {
            "action": "STRUCTURAL_MUTATION",
            "metric": "Self-Correlation",
            "goal": "Reduce Self-Correlation"
        }
        
    # Check for low Sharpe or Fitness
    sharpe = metrics.get("sharpe")
    fitness = metrics.get("fitness")
    
    sharpe_val = None
    fitness_val = None
    if sharpe is not None:
        try:
            sharpe_val = float(sharpe)
        except (ValueError, TypeError):
            pass
    if fitness is not None:
        try:
            fitness_val = float(fitness)
        except (ValueError, TypeError):
            pass
            
    if (sharpe_val is not None and sharpe_val < 1.0) or (fitness_val is not None and fitness_val < 1.0):
        t_metric = []
        if sharpe_val is not None and sharpe_val < 1.0:
            t_metric.append(f"Sharpe ({sharpe_val:.2f})")
        if fitness_val is not None and fitness_val < 1.0:
            t_metric.append(f"Fitness ({fitness_val:.2f})")
        metric_str = " & ".join(t_metric) if t_metric else "Sharpe/Fitness < 1.0"
        
        return {
            "action": "TIER_1_SWAP",
            "metric": metric_str,
            "goal": "Improve Sharpe"
        }
        
    # Check for Incompatible unit error
    has_unit_error = False
    for check in failed_checks:
        if "unit" in check.lower() or "incompatible" in check.lower():
            has_unit_error = True
            break
            
    error_msg = metrics.get("error") or ""
    if "unit" in str(error_msg).lower() or "incompatible" in str(error_msg).lower():
        has_unit_error = True
        
    if has_unit_error:
        return {
            "action": "UNIT_WRAP",
            "metric": "Incompatible Unit",
            "goal": "Standardize Units"
        }
        
    return {"action": "STANDARD", "metric": "None", "goal": "Improve Sharpe"}

def wrap_unwrapped_raw_inputs(code, wrap_op="rank"):
    """
    Ensures all ts_backfill(field, 60) occurrences in code are wrapped in rank(), zscore(), or scale().
    If any are unwrapped, wraps them with wrap_op (which defaults to 'rank').
    """
    pattern = r'\bts_backfill\(([a-zA-Z0-9_]+),\s*60\)'
    new_code = ""
    last_pos = 0
    for match in re.finditer(pattern, code):
        start, end = match.span()
        new_code += code[last_pos:start]
        
        # Check if the text immediately preceding the match (ignoring whitespace) is an operator
        before_slice = code[:start].rstrip()
        is_wrapped = False
        for op in ["rank(", "zscore(", "scale("]:
            if before_slice.endswith(op):
                is_wrapped = True
                break
                
        if is_wrapped:
            new_code += match.group(0)
        else:
            new_code += f"{wrap_op}({match.group(0)})"
        last_pos = end
    new_code += code[last_pos:]
    return new_code

def mutate_alpha_feedback(winning_code, metrics, recent_datasets=None):
    """
    Feedback-Driven Mutation Engine:
    Actively learns from the weaknesses of the alpha to perform targeted metric optimization.
    Also forces structural changes to the signal composition.
    Ensures the child code is never identical to the parent code.
    """
    if recent_datasets is None:
        recent_datasets = []
        
    failed_checks = metrics.get("failed_checks", []) if metrics else []
    if isinstance(failed_checks, str):
        failed_checks = [c.strip() for c in failed_checks.split(";")]
        
    sharpe = float(metrics.get("sharpe", 0)) if (metrics and metrics.get("sharpe") is not None) else 0.0
    returns = float(metrics.get("returns", 0)) if (metrics and metrics.get("returns") is not None) else 0.0
    
    # Priority: If the alpha is losing money / has low Sharpe, flip the reversion sign first
    if (sharpe < 1.0 or "LOW_SHARPE" in failed_checks) and returns < 0:
        print("💡 Feedback-driven mutation: Negative Returns / Low Sharpe. Flipping reversion direction (-1 *).")
        return flip_alpha_sign(winning_code)
        
    # DIAGNOSTIC ENGINE: Check direction
    direction = get_mutation_direction(metrics)
    action = direction["action"]
    
    if action == "SCRAP_AND_REBUILD":
        print(f"💡 DIAGNOSTIC_ENGINE: High self-correlation (> 0.95). Scrap and rebuild triggered.")
        return generate_alpha_expression(recent_datasets=recent_datasets)
        
    elif action == "TIME_HORIZON_SHIFT":
        print(f"💡 DIAGNOSTIC_ENGINE: Severe structural correlation. Shifting time horizons radically.")
        return mutate_time_horizon_shift(winning_code)
        
    elif action == "ORTHOGONAL_DATA_SWAP":
        print(f"💡 DIAGNOSTIC_ENGINE: Moderate correlation. Swapping to orthogonal dataset category.")
        return mutate_orthogonal_data_swap(winning_code)
        
    elif action == "NON_LINEAR_WRAP":
        print(f"💡 DIAGNOSTIC_ENGINE: Moderate correlation. Applying non-linear wrap to break linearity.")
        return mutate_non_linear_wrap(winning_code)
        
    elif action == "STRUCTURAL_MUTATION":
        print(f"💡 DIAGNOSTIC_ENGINE: High self-correlation. Forcing structural mutation.")
        return mutate_structure(winning_code, recent_datasets)
        
    elif action == "TIER_1_SWAP":
        print(f"💡 DIAGNOSTIC_ENGINE: Sharpe or Fitness < 1.0. Forcing dataset swap to a Tier 1 variable.")
        current_ds = None
        for ds in DATASET_POOL:
            if ds in winning_code:
                current_ds = ds
                break
        if current_ds:
            tier1_avail = [f for f in TIER_1_POOL if f != current_ds and f not in recent_datasets]
            if not tier1_avail:
                tier1_avail = [f for f in TIER_1_POOL if f != current_ds]
            if not tier1_avail:
                tier1_avail = TIER_1_POOL
            new_ds = random.choice(tier1_avail)
            return winning_code.replace(current_ds, new_ds)
        else:
            return mutate_structure(winning_code, recent_datasets)
            
    elif action == "UNIT_WRAP":
        print(f"💡 DIAGNOSTIC_ENGINE: Incompatible unit error. Automatically wrapping raw input in rank() or scale() operator.")
        wrap_op = random.choice(["rank", "scale"])
        return wrap_unwrapped_raw_inputs(winning_code, wrap_op)
        
    if "SELF_CORRELATION" in failed_checks:
        # Why: Self-Correlation Failure. The alpha is too similar to an existing submission.
        # Action: Upgrade to Correlation Escalation Protocol.
        print("💡 Feedback-driven mutation: Self-Correlation failure detected. Applying Correlation Reduction Protocol.")
        corr_action = random.choice(["TIME_HORIZON_SHIFT", "ORTHOGONAL_DATA_SWAP", "NON_LINEAR_WRAP"])
        if corr_action == "TIME_HORIZON_SHIFT":
            return mutate_time_horizon_shift(winning_code)
        elif corr_action == "ORTHOGONAL_DATA_SWAP":
            return mutate_orthogonal_data_swap(winning_code)
        else:
            return mutate_non_linear_wrap(winning_code)
            
    if "CONCENTRATED_WEIGHT" in failed_checks:
        # Why: Weight Concentration Error. Switch primary operator from zscore to rank or swap to high-coverage datasets.
        print("💡 Feedback-driven mutation: Weight Concentration detected. Swapping dataset to high-coverage pool.")
        high_coverage_datasets = [
            "mdl177_2_earningsqualityfactor_wcacc",
            "mdl177_2_deepvaluefactor_ebitdaev",
            "consensus_analyst_rating",
            "distress_risk_measure"
        ]
        available = [ds for ds in high_coverage_datasets if ds not in recent_datasets]
        if not available:
            available = high_coverage_datasets
            
        for ds in DATASET_POOL:
            if ds in winning_code:
                new_ds = random.choice(available)
                return winning_code.replace(ds, new_ds)
        return mutate_dataset(winning_code, recent_datasets)

    if "LOW_SUB_UNIVERSE_SHARPE" in failed_checks:
        # Why: Low sub-universe Sharpe. Upgrade the neutralization level to INDUSTRY or SUBINDUSTRY.
        print("💡 Feedback-driven mutation: Low Sub-Universe Sharpe. Upgrading neutralization level.")
        return mutate_neutralization_group(winning_code)
        
    sharpe = float(metrics.get("sharpe", 0)) if metrics else 0.0
    returns = float(metrics.get("returns", 0)) if metrics else 0.0
    drawdown = float(metrics.get("drawdown", 0)) if metrics else 0.0
    margin = float(metrics.get("margin", 0)) if metrics else 0.0
    turnover = float(metrics.get("turnover", 0)) if metrics else 0.0
    
    # 20% chance that during a standard mutation, it routes to mutate_cross_domain_interaction
    if random.random() < 0.20:
        return mutate_cross_domain_interaction(winning_code)
        
    mutated_code = winning_code
    
    for attempt in range(5):
        r = random.random()
        
        # 40% chance of structural mutation
        if r < 0.40:
            # Why: Structural complexity injection to ensure alpha diversity and prevent cloning.
            print("🧬 Performing structural mutation...")
            mutated_code = mutate_structure(winning_code, recent_datasets)
            
        # 1. High Turnover: increase decay window or smoothing lookback to stabilize trading
        elif turnover > 0.40 or "LOW_TURNOVER" in failed_checks or "HIGH_TURNOVER" in failed_checks:
            # Why: Turnover > 0.40. Increase decay window to smooth out transactions and hold positions longer.
            print("💡 Feedback-driven mutation: High/Low Turnover check. Increasing decay/smoothing window.")
            mutated_code = increase_decay_window(winning_code)
            if mutated_code == winning_code:
                mutated_code = increase_lookback_window(winning_code)
                
        # 2. Terrible Drawdown: increase lookback smoothing window to smooth out extreme price actions
        elif abs(drawdown) > 0.15:
            # Why: Drawdown is too high. Increase smoothing lookback window to reduce downside risk.
            print("💡 Feedback-driven mutation: High Drawdown detected. Increasing smoothing window to reduce risk.")
            mutated_code = increase_lookback_window(winning_code)
            
        # 3. Low Margin: modify group neutralization level to seek higher trading efficiency
        elif margin < 0.0005:  # < 5 bps
            # Why: Low transaction margin. Mutate neutralization group to seek higher trading efficiency.
            print("💡 Feedback-driven mutation: Low Margin detected. Mutating neutralization level.")
            mutated_code = mutate_neutralization_group(winning_code)
            
        # 4. Low Sharpe: Increase ts_decay_linear window or mutate dataset to filter out noise
        elif sharpe < 1.0 or "LOW_SHARPE" in failed_checks:
            print("💡 Feedback-driven mutation: Low Sharpe. Increasing decay window to filter noise.")
            mutated_code = increase_decay_window(winning_code)
            if mutated_code == winning_code:
                mutated_code = mutate_dataset(winning_code, recent_datasets)
                
        # Fallback to other mutations if targeted mutation was a no-op
        if mutated_code == winning_code:
            r2 = random.random()
            if r2 < 0.25:
                mutated_code = mutate_time_horizons(winning_code)
            elif r2 < 0.50:
                mutated_code = mutate_dataset(winning_code, recent_datasets)
            elif r2 < 0.75:
                mutated_code = mutate_neutralization_group(winning_code)
            else:
                mutated_code = flip_alpha_sign(winning_code)
                
        if mutated_code != winning_code:
            return mutated_code
            
    # Force a dataset swap as ultimate fallback
    return mutate_dataset(winning_code, recent_datasets)

# ==============================================================================
# DATA PARSING & API UTILITIES
# ==============================================================================

def migrate_csv_file():
    """
    Migrates simulation_results_delay0.csv to include the FailedChecks column if not present.
    """
    csv_file = "simulation_results_delay0.csv"
    if not os.path.exists(csv_file):
        return
    try:
        with open(csv_file, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if not rows:
            return
        header = rows[0]
        if "FailedChecks" in header:
            return
            
        print("Migrating simulation_results_delay0.csv to include FailedChecks column...")
        if "Code" in header:
            code_idx = header.index("Code")
            header.insert(code_idx, "FailedChecks")
            for row in rows[1:]:
                if len(row) > code_idx:
                    row.insert(code_idx, "")
                else:
                    row.append("")
        else:
            header.append("FailedChecks")
            for row in rows[1:]:
                row.append("")
                
        with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        print("Migration complete!")
    except Exception as e:
        print(f"Error during CSV migration: {e}")

def get_historical_alphas():
    """
    Reads simulation_results_delay0.csv and returns a list of dictionaries with alpha details.
    """
    csv_file = "simulation_results_delay0.csv"
    if not os.path.exists(csv_file):
        return []
        
    alphas = []
    try:
        with open(csv_file, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                status = row.get("Status")
                code = row.get("Code")
                if not code:
                    continue
                
                # Parse metrics back to decimal scale for analytical decision making
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
                
                margin_val = to_float(row.get("Margin(bps)")) / 10000.0
                turnover_val = to_fraction(row.get("Turnover(%)"))
                
                failed_checks_str = row.get("FailedChecks")
                failed_checks = failed_checks_str.split(";") if failed_checks_str else []
                
                metrics = {
                    "sharpe": to_float(row.get("Sharpe")),
                    "fitness": to_float(row.get("Fitness")),
                    "returns": to_fraction(row.get("Returns(%)")),
                    "drawdown": to_fraction(row.get("Drawdown(%)")),
                    "margin": margin_val,
                    "turnover": turnover_val,
                    "failed_checks": failed_checks
                }
                
                alphas.append({
                    "code": code,
                    "status": status,
                    "metrics": metrics
                })
    except Exception as e:
        print(f"Error reading CSV logs: {e}")
        
    return alphas

def get_recent_successful_datasets(alphas):
    """
    Extracts the datasets used in the last 10 successful alphas (Status == "SUCCESS").
    """
    recent_datasets = []
    for a in reversed(alphas):
        if a.get("status") == "SUCCESS":
            code = a.get("code", "")
            for ds in DATASET_POOL:
                if ds in code:
                    recent_datasets.append(ds)
                    break
            if len(recent_datasets) >= 10:
                break
    return list(set(recent_datasets))

def get_recent_successful_alphas(alphas):
    """
    Extracts the last 15 successful alphas with Sharpe > 1.2 and Fitness > 1.0.
    """
    successful_alphas = []
    for a in reversed(alphas):
        if a.get("status") == "SUCCESS":
            metrics = a.get("metrics", {})
            sharpe = metrics.get("sharpe", 0.0)
            fitness = metrics.get("fitness", 0.0)
            if sharpe > 1.2 and fitness > 1.0:
                code = a.get("code", "")
                if code and code not in successful_alphas:
                    successful_alphas.append(code)
                if len(successful_alphas) >= 15:
                    break
    return successful_alphas

def extract_metrics(data, session, headers):
    """
    Extracts metrics (sharpe, fitness, returns, drawdown, margin, turnover) from simulation
    data. Falls back to querying the /alphas/{id} endpoint if metrics are not direct.
    """
    # Try 1: check 'is' dict directly
    if "is" in data and isinstance(data["is"], dict):
        is_dict = data["is"]
        if "sharpe" in is_dict:
            return is_dict
            
    # Try 2: check 'results' dict/list
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
                    
    # Try 3: check 'alpha' sub-dict
    if "alpha" in data and isinstance(data["alpha"], dict):
        alpha_dict = data["alpha"]
        if "is" in alpha_dict and isinstance(alpha_dict["is"], dict):
            return alpha_dict["is"]
            
    # Try 4: Query alpha detail URL from 'alpha' string ID
    alpha_id = data.get("alpha")
    if alpha_id and isinstance(alpha_id, str):
        print(f"Fetching alpha details for {alpha_id} from /alphas endpoint...")
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
                print(f"Transient error fetching alpha details: {e}")
                time.sleep(2)
                
    return None

def simulate_alpha(expression, session, headers, settings, dry_run=False):
    """
    Sends simulation POST request, polls for results, and handles rate-limits.
    Supports custom simulation settings configured via command-line arguments.
    """
    universe = settings.get("universe", "TOP3000")
    decay = settings.get("decay", 2)
    if decay == -1:
        decay = random.choice([0, 2, 4, 8])
        
    if dry_run:
        # Mock simulation response for testing
        print(f"[DRY-RUN] Simulating code on universe={universe}, decay={decay}")
        time.sleep(1)
        mock_success = random.random() < 0.7
        if mock_success:
            sharpe = random.uniform(0.5, 2.2)
            fitness = random.uniform(0.5, 2.2)
            returns = random.uniform(-0.10, 0.35)
            drawdown = random.uniform(-0.30, -0.01)
            margin = random.uniform(0.0001, 0.0035)
            turnover = random.uniform(0.05, 0.85)
            metrics = {
                "sharpe": sharpe,
                "fitness": fitness,
                "returns": returns,
                "drawdown": drawdown,
                "margin": margin,
                "turnover": turnover
            }
            return {
                "status": "SUCCESS",
                "metrics": metrics,
                "failed_checks": [],
                "universe": universe,
                "decay": decay
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
            "delay": settings.get("delay", 0),
            "decay": decay,
            "neutralization": settings.get("neutralization", "NONE"),
            "truncation": settings.get("truncation", 0.08),
            "pasteurization": settings.get("pasteurization", "ON"),
            "nanHandling": settings.get("nanHandling", "OFF"),
            "language": settings.get("language", "FASTEXPR"),
            "unitHandling": settings.get("unitHandling", "VERIFY"),
            "visualization": False
        },
        "regular": expression
    }
    
    # 1. Submission POST request with Exponential Backoff for 429
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
            
    # Extract polling URL
    status_url = response.headers.get("Location")
    if not status_url:
        print("Error: Location header missing from response headers.")
        return {
            "status": "NO_LOCATION_HEADER",
            "error": "Location header missing",
            "universe": universe,
            "decay": decay
        }
        
    if not status_url.startswith("http"):
        status_url = "https://api.worldquantbrain.com" + status_url
        
    print(f"Polling simulation status from: {status_url}")
    
    # 2. Polling loop
    poll_count = 0
    none_status_count = 0
    current_phase = 1
    poll_interval = 2
    while poll_count < 300:
        # Determine the phase and polling interval dynamically based on poll_count
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
                print("Rate limited (429) during polling. Sleeping for 60 seconds...")
                time.sleep(60)
                continue
                
            try:
                data = poll_resp.json()
            except json.JSONDecodeError as jde:
                print(f"JSONDecodeError during polling: {jde}. Retrying in 3s...")
                time.sleep(3)
                poll_count += 1
                continue
                
            status = data.get("status")
            if status is None:
                none_status_count += 1
                print(f"Poll {poll_count + 1}/300 - Status: None (count: {none_status_count})")
                if none_status_count > 25:
                    print("⚠️ Status: None for > 25 polls. Waiting 30s before fresh status check...")
                    time.sleep(30)
                    none_status_count = 0
            else:
                none_status_count = 0
                print(f"Poll {poll_count + 1}/300 - Status: {status}")
            
            if status in ["COMPLETE", "COMPLETED"]:
                # Fetch full alpha details to get metrics and checks
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
                            print(f"Error fetching alpha details: {e}")
                            time.sleep(2)
                
                if not metrics:
                    metrics = extract_metrics(data, session, headers)
                    
                if metrics:
                    return {
                        "status": "SUCCESS",
                        "metrics": metrics,
                        "failed_checks": failed_checks,
                        "universe": universe,
                        "decay": decay
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
            print(f"Connection error during polling: {e}. Retrying in 3s...")
            time.sleep(3)
            poll_count += 1
            
    return {
        "status": "TIMEOUT",
        "error": "Exceeded maximum polling steps (300)",
        "universe": universe,
        "decay": decay
    }

def log_attempt(status, metrics, failed_checks, universe, decay, code, settings=None):
    """
    Logs alpha settings and output performance values to simulation_results_delay0.csv.
    """
    csv_file = "simulation_results_delay0.csv"
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
        
        # Format Returns (%)
        if r_val is not None:
            r_float = float(r_val)
            if abs(r_float) <= 1.0:
                returns_pct = f"{r_float * 100.0:.4f}"
            else:
                returns_pct = f"{r_float:.4f}"
                
        # Format Drawdown (%)
        if d_val is not None:
            d_float = float(d_val)
            if abs(d_float) <= 1.0:
                drawdown_pct = f"{d_float * 100.0:.4f}"
            else:
                drawdown_pct = f"{d_float:.4f}"
                
        # Format Margin (bps)
        if m_val is not None:
            margin_bps = f"{float(m_val) * 10000.0:.4f}"
            
        # Format Turnover (%)
        if t_val is not None:
            t_float = float(t_val)
            if abs(t_float) <= 1.0:
                turnover_pct = f"{t_float * 100.0:.4f}"
            else:
                turnover_pct = f"{t_float:.4f}"
            
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
            neutral_val = settings.get("neutralization", "NONE") if settings else "NONE"
            
            writer.writerow([
                status, sharpe, fitness, returns_pct, drawdown_pct,
                margin_bps, turnover_pct, universe, delay_val, decay, neutral_val, checks_str, code
            ])
        print(f"Logged to CSV: Status={status}, Sharpe={sharpe}, Fitness={fitness}, Turnover(%)={turnover_pct}, FailedChecks={checks_str}")
    except Exception as e:
        print(f"Failed to log to CSV: {e}")

# ==============================================================================
# MAIN COORDINATION LOOP
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="WorldQuant BRAIN Feedback Alpha Generator")
    parser.add_index = False
    parser.add_argument("--cookie", type=str, help="Override auth cookie string")
    parser.add_argument("--dry-run", action="store_true", help="Run offline dry-run mode with simulated metrics")
    parser.add_argument("--iterations", type=int, default=0, help="Limit number of loops to run (0 for infinite)")
    parser.add_argument("--engine", type=str, choices=["fundamental", "formulaic"], default="fundamental",
                        help="Alpha Generation Engine (fundamental or formulaic)")
    
    # Custom simulation settings arguments
    parser.add_argument("--universe", type=str, default="TOP3000", help="Universe (e.g. TOP3000, TOP1000, TOP200)")
    parser.add_argument("--delay", type=int, default=0, help="Simulation Delay (1 or 2)")
    parser.add_argument("--decay", type=int, default=-1, help="Decay factor (0 to 30, -1 for random)")
    parser.add_argument("--neutralization", type=str, default="NONE", help="Neutralization level (NONE, MARKET, INDUSTRY, SECTOR, SUBINDUSTRY)")
    parser.add_argument("--truncation", type=float, default=0.08, help="Truncation limit (0.01 to 0.10)")
    parser.add_argument("--pasteurization", type=str, choices=["ON", "OFF"], default="ON", help="Pasteurization status")
    parser.add_argument("--nan-handling", type=str, choices=["ON", "OFF"], default="OFF", dest="nan_handling", help="NaN handling status")
    parser.add_argument("--unit-handling", type=str, choices=["VERIFY", "COMPLY"], default="VERIFY", dest="unit_handling", help="Unit handling status")
    parser.add_argument("--region", type=str, default="USA", help="Region (e.g. USA, EUR, AP)")
    parser.add_argument("--instrument-type", type=str, default="EQUITY", dest="instrument_type", help="Instrument type (EQUITY)")
    args = parser.parse_args()
    
    print("=" * 60)
    print(f" WORLDQUANT BRAIN ALPHA FACTORY - {args.engine.upper()} ENGINE")
    print("=" * 60)
    
    session = requests.Session()
    
    cookie_str = args.cookie
    if not cookie_str or cookie_str == "PASTE_YOUR_COOKIE_HERE":
        if COOKIE and COOKIE != "PASTE_YOUR_COOKIE_HERE":
            cookie_str = COOKIE
        else:
            cookie_str = ""
            
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
        
    # Authenticate and test connection
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
                print("Make sure your JWT token 't' is not expired.")
        except Exception as e:
            print(f"⚠️ Connection error during authentication test: {e}")
    else:
        print("⚠️ RUNNING IN OFFLINE DRY-RUN MODE (MOCK API SIMULATIONS)")
        
    # Run CSV column migration first
    migrate_csv_file()
    
    sim_settings = {
        "universe": args.universe,
        "delay": args.delay,
        "decay": args.decay,
        "neutralization": args.neutralization,
        "truncation": args.truncation,
        "pasteurization": args.pasteurization,
        "nanHandling": args.nan_handling,
        "unitHandling": args.unit_handling,
        "region": args.region,
        "instrumentType": args.instrument_type,
        "language": "FASTEXPR"
    }

    # Initialize GradientEngine and pretrain it
    optimizer.initialize_pools()
    alphas = get_historical_alphas()
    pretrain_gradient_engine(optimizer, alphas)
    optimizer.print_top_weights()

    last_result = None
    repair_attempts = 0
    loop_count = 0
    previous_sharpe = 0.0
    while True:
        loop_count += 1
        if args.iterations > 0 and loop_count > args.iterations:
            print(f"Reached requested limit of {args.iterations} iterations. Exiting.")
            break
            
        print(f"\n--- Alpha Factory Cycle #{loop_count} ---")
        
        # 1. Get past alphas from logs
        alphas = get_historical_alphas()
        all_winners = [a for a in alphas if a["status"] == "SUCCESS" and a["metrics"]["sharpe"] > 1.2 and a["metrics"]["fitness"] > 1.0]
        
        # Filter winners based on the engine to avoid mixing domains during mutation
        if args.engine == "formulaic":
            def is_valid_formulaic_parent(code):
                if any(ds in code for ds in DATASET_POOL):
                    return False
                if "?" in code:
                    return False
                forbidden = ["ts_max", "ts_min", "ts_argmax", "ts_argmin", "indneutralize", "correlation", "covariance", "stddev"]
                if any(p in code for p in forbidden):
                    return False
                if re.search(r'\bdelay\b', code) or re.search(r'\bdelta\b', code) or re.search(r'\bsum\b', code) or re.search(r'\bmax\b', code) or re.search(r'\bmin\b', code):
                    return False
                return True
            winners = [a for a in all_winners if is_valid_formulaic_parent(a["code"])]
        else:
            winners = [a for a in all_winners if any(ds in a["code"] for ds in DATASET_POOL)]
            
        print(f"Parsed {len(alphas)} historical alphas, found {len(winners)} eligible {args.engine} winners (Sharpe > 1.2 and Fitness > 1.0).")
        
        # Get recent datasets rotation list
        recent_datasets = get_recent_successful_datasets(alphas)
        history_buffer = get_recent_successful_alphas(alphas)
        if args.engine == "fundamental":
            print(f"🔄 Dataset rotation forbidden list (last 10 successful): {recent_datasets}")
            print(f"📋 HISTORY_BUFFER (last 15 successful expressions): {history_buffer}")
            
        # Randomize simulation settings within high-probability ranges to maximize yield of elite alphas
        cycle_universe = random.choice(["TOP3000", "TOP1000"])
        cycle_decay = random.choice([2, 3, 5, 8, 10])
        cycle_neutralization = random.choice(["INDUSTRY", "SUBINDUSTRY"])
        cycle_delay = 0
        
        sim_settings = {
            "universe": cycle_universe,
            "delay": cycle_delay,
            "decay": cycle_decay,
            "neutralization": cycle_neutralization,
            "truncation": args.truncation,
            "pasteurization": args.pasteurization,
            "nanHandling": args.nan_handling,
            "unitHandling": args.unit_handling,
            "region": args.region,
            "instrumentType": args.instrument_type,
            "language": "FASTEXPR"
        }
        print(f"⚙️ Simulation settings: Universe={cycle_universe}, Delay={cycle_delay}, Decay={cycle_decay}, Neutralization={cycle_neutralization}")
        
        # Check if the last cycle had a diagnostic issue that needs immediate repair/optimization
        use_last_result_for_repair = False
        if last_result and last_result.get("repair_attempts", 0) < 3:
            last_metrics = last_result.get("metrics")
            direction = get_mutation_direction(last_metrics)
            if direction["action"] != "STANDARD":
                use_last_result_for_repair = True
                parent_code = last_result["code"]
                parent_metrics = last_metrics
                repair_attempts = last_result.get("repair_attempts", 0) + 1
                
                goal = direction["goal"]
                metric = direction["metric"]
                action = direction["action"]
                
                print(f"🔧 DIAGNOSTIC ENGINE: Last alpha had check/metric issues. Initiating repair mutation (Attempt {repair_attempts}/3)...")
                print(f"Diagnostics - Action: {action} | Goal: {goal} | Metric: {metric}")

        # 2. Decide: generate random or mutate past winner based on selected engine
        is_mutation = False
        if not use_last_result_for_repair:
            goal = "Improve Sharpe"
            metric = "None"
            action = "Standard Generation" if args.engine == "fundamental" else "Formulaic Generation"
            
            if winners and random.random() < 0.5:
                is_mutation = True
                parent_alpha = random.choice(winners)
                parent_code = parent_alpha["code"]
                parent_metrics = parent_alpha["metrics"]
                
                if args.engine == "formulaic":
                    code = mutate_formulaic_alpha(parent_code, parent_metrics)
                    print(f"🧬 [FORMULAIC MUTATION] Mutating parent:\nCode: {parent_code}\nChild: {code}")
                    action = "Formulaic Mutation"
                else:
                    # Run diagnostic engine to determine optimization targets
                    direction = get_mutation_direction(parent_metrics)
                    goal = direction["goal"]
                    metric = direction["metric"]
                    action = direction["action"]
                    
                    code = mutate_alpha_feedback(parent_code, parent_metrics, recent_datasets)
                    print(f"🧬 [FUNDAMENTAL MUTATION] Mutating parent:\nCode: {parent_code}")
                    print(f"Parent Metrics: Sharpe: {parent_metrics['sharpe']:.4f}, Drawdown: {parent_metrics['drawdown']*100:.2f}%, Turnover: {parent_metrics['turnover']*100:.2f}%")
                    print(f"Child Code    : {code}")
            else:
                if args.engine == "formulaic":
                    code = generate_formulaic_expression()
                    print(f"✨ [FORMULAIC GENERATION] New random alpha expression:\nCode: {code}")
                else:
                    code = generate_alpha_expression(recent_datasets, history_buffer, cycle_universe)
                    print(f"✨ [FUNDAMENTAL GENERATION] New random alpha expression:\nCode: {code}")
        else:
            is_mutation = True
            if args.engine == "formulaic":
                code = mutate_formulaic_alpha(parent_code, parent_metrics)
                print(f"🧬 [FORMULAIC REPAIR] Mutating parent:\nCode: {parent_code}\nChild: {code}")
            else:
                code = mutate_alpha_feedback(parent_code, parent_metrics, recent_datasets)
                print(f"🧬 [FUNDAMENTAL REPAIR] Mutating parent:\nCode: {parent_code}\nChild: {code}")
                
        # 2.5 Anti-Cloning check (mutated or generated code)
        if args.engine == "fundamental":
            attempts = 0
            while code in history_buffer and attempts < 10:
                print(f"⚠️ Expression already in HISTORY_BUFFER: {code}. Forcing structural re-mutation...")
                if random.random() < 0.5:
                    code = mutate_structure(code, recent_datasets)
                    action = "STRUCTURAL_MUTATION"
                else:
                    code = mutate_dataset(code, recent_datasets)
                    action = "TIER_1_SWAP"
                attempts += 1
                
        # Enforce surgical constraints on the code before simulation
        code = enforce_group_neutralize_rank(code)
        code = cap_decay_windows(code)

        # Print META metadata debug line for all generations/mutations
        print_meta_data_line(code, cycle_universe, goal=goal, metric=metric, action=action)
            
        # 3. Simulate
        result = simulate_alpha(code, session, headers, sim_settings, dry_run=args.dry_run)
        
        status = result["status"]
        metrics = result.get("metrics")
        failed_checks = result.get("failed_checks", [])
        universe = result.get("universe")
        decay = result.get("decay")
        
        # Cross-Correlation Check
        is_correlated, sim_score, correlated_code = is_cross_correlated(code, history_buffer)
        if status == "SUCCESS" and is_correlated:
            print(f"⚠️ REJECTED: Candidate shares {sim_score:.2%} components with existing alpha in history: {correlated_code}")
            status = "FAILED"
            if "SELF_CORRELATION" not in failed_checks:
                failed_checks.append("SELF_CORRELATION")
        
        # 4. Log results
        log_attempt(status, metrics, failed_checks, universe, decay, code, settings=sim_settings)
        
        # Policy Gradient Update: Reward/Penalize components based on Sharpe
        if status == "SUCCESS" and metrics:
            current_sharpe = float(metrics.get("sharpe", 0.0) or 0.0)
            optimizer.calculate_gradient_step(alpha_string=code, new_sharpe=current_sharpe, old_sharpe=previous_sharpe)
            optimizer.print_top_weights()
            previous_sharpe = current_sharpe
        else:
            optimizer.calculate_gradient_step(alpha_string=code, new_sharpe=-1.0, old_sharpe=previous_sharpe)
        
        # Increment usage count for datasets in the tracker if simulated successfully
        if status == "SUCCESS":
            comps = get_alpha_components(code)
            for comp in comps:
                if comp in DATASET_POOL:
                    DATASET_USAGE_TRACKER[comp] = DATASET_USAGE_TRACKER.get(comp, 0) + 1
        
        # If simulation was not successful or metrics are missing, construct minimal metrics for diagnostic repair
        if status != "SUCCESS" or not metrics:
            metrics = {
                "sharpe": 0.0,
                "fitness": 0.0,
                "failed_checks": failed_checks,
                "error": result.get("error", "")
            }
            
        # Store result of this cycle for next cycle's diagnostic repair check
        last_result = {
            "code": code,
            "metrics": metrics,
            "repair_attempts": repair_attempts if use_last_result_for_repair else 0
        }
        
        # 5. Check if elite criteria met (Sharpe > 1.5, Fitness > 1.5, Returns > 20%)
        if status == "SUCCESS" and metrics:
            s_val = metrics.get("sharpe")
            f_val = metrics.get("fitness")
            r_val = metrics.get("returns")
            
            if s_val is not None and f_val is not None and r_val is not None:
                s_float = float(s_val)
                f_float = float(f_val)
                r_float = float(r_val)
                
                r_frac = r_float if abs(r_float) <= 1.0 else r_float / 100.0
                
                if s_float > 1.5 and f_float > 1.5 and r_frac > 0.20 and not failed_checks:
                    print(f"🔥 ELITE ALPHA FOUND! Sharpe: {s_float:.4f}, Fitness: {f_float:.4f}, Returns: {r_frac*100.0:.2f}%")
                    try:
                        with open("elite_alphas.txt", mode="a", encoding="utf-8") as elite_f:
                            elite_f.write(f"Code: {code}\n")
                            elite_f.write(f"Sharpe: {s_float:.4f}, Fitness: {f_float:.4f}, Returns: {r_frac*100.0:.2f}%, Universe: {universe}, Decay: {decay}\n")
                            elite_f.write("-" * 50 + "\n")
                    except Exception as e:
                        print(f"Failed to append to elite_alphas.txt: {e}")
                        
                    # Generate 5A, 5B, 5C variants
                    variants = mutate_structure(code, generate_variants=True)
                    print(f"🧬 Generated 3 neutralization variants for the Elite alpha:")
                    print(f"  Variant A (Industry): {variants[0]}")
                    print(f"  Variant B (Industry + Cap Bucket): {variants[1]}")
                    print(f"  Variant C (Volume Bucket): {variants[2]}")
                    
                    variant_names = ["Variant A (Industry)", "Variant B (Industry + Cap Bucket)", "Variant C (Volume Bucket)"]
                    for var_name, var_code in zip(variant_names, variants):
                        print(f"\n[VARIANT ENGINE] Processing {var_name}...")
                        
                        # Cross-correlation check against history buffer
                        v_correlated, v_sim, v_corr_code = is_cross_correlated(var_code, history_buffer)
                        if v_correlated:
                            print(f"  ⚠️ {var_name} REJECTED (Correlated {v_sim:.2%} with: {v_corr_code})")
                            log_attempt("FAILED", None, ["SELF_CORRELATION"], universe, decay, var_code, settings=sim_settings)
                            continue
                            
                        # Simulate variant
                        # Force neutralization to "NONE" for the variant since it has it hardcoded
                        v_settings = sim_settings.copy()
                        v_settings["neutralization"] = "NONE"
                        
                        print(f"  🚀 Simulating {var_name}...")
                        v_result = simulate_alpha(var_code, session, headers, v_settings, dry_run=args.dry_run)
                        
                        v_status = v_result["status"]
                        v_metrics = v_result.get("metrics")
                        v_failed_checks = v_result.get("failed_checks", [])
                        v_univ = v_result.get("universe")
                        v_dec = v_result.get("decay")
                        
                        # Double check correlation just in case
                        v_corr_after, v_sim_after, v_corr_code_after = is_cross_correlated(var_code, history_buffer)
                        if v_status == "SUCCESS" and v_corr_after:
                            print(f"  ⚠️ {var_name} REJECTED after sim (Correlated {v_sim_after:.2%} with: {v_corr_code_after})")
                            v_status = "FAILED"
                            if "SELF_CORRELATION" not in v_failed_checks:
                                v_failed_checks.append("SELF_CORRELATION")
                                
                        log_attempt(v_status, v_metrics, v_failed_checks, v_univ, v_dec, var_code, settings=v_settings)
                        
                        if v_status == "SUCCESS" and v_metrics:
                            vs_val = v_metrics.get("sharpe")
                            vf_val = v_metrics.get("fitness")
                            vr_val = v_metrics.get("returns")
                            
                            if vs_val is not None and vf_val is not None and vr_val is not None:
                                vs_float = float(vs_val)
                                vf_float = float(vf_val)
                                vr_float = float(vr_val)
                                vr_frac = vr_float if abs(vr_float) <= 1.0 else vr_float / 100.0
                                
                                # Add successful variant to history buffer to prevent subsequent variants from matching it
                                history_buffer.append(var_code)
                                
                                # Check if variant itself is elite and log it
                                if vs_float > 1.5 and vf_float > 1.5 and vr_frac > 0.20 and not v_failed_checks:
                                    print(f"  🔥 Elite Variant Found! Sharpe: {vs_float:.4f}, Fitness: {vf_float:.4f}, Returns: {vr_frac*100.0:.2f}%")
                                    try:
                                        with open("elite_alphas.txt", mode="a", encoding="utf-8") as elite_f:
                                            elite_f.write(f"Code ({var_name}): {var_code}\n")
                                            elite_f.write(f"Sharpe: {vs_float:.4f}, Fitness: {vf_float:.4f}, Returns: {vr_frac*100.0:.2f}%, Universe: {v_univ}, Decay: {v_dec}\n")
                                            elite_f.write("-" * 50 + "\n")
                                    except Exception as e:
                                        print(f"Failed to append variant to elite_alphas.txt: {e}")
                        
        time.sleep(2)

if __name__ == "__main__":
    main()
    