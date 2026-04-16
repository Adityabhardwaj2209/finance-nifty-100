"""
Phase 2: Analytics & ML Scoring Engine.
Calculates financial health scores for companies based on warehouse data.
"""
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "nifty100_warehouse.db"

# Engine setup
engine = create_engine(f"sqlite:///{DB_PATH}")

def get_label(score):
    if score >= 80: return "EXCELLENT"
    if score >= 60: return "GOOD"
    if score >= 40: return "AVERAGE"
    if score >= 20: return "WEAK"
    return "POOR"

def score_metric(val, benchmarks, ascending=True):
    """
    Score a value from 0-100 based on benchmarks.
    benchmarks: (min_threshold, max_threshold)
    ascending: True if higher value is better (e.g., ROE), False if lower is better (e.g., D/E).
    """
    if pd.isna(val): return 50 # Neutral for missing
    
    min_b, max_b = benchmarks
    if ascending:
        if val >= max_b: return 100
        if val <= min_b: return 0
        return ((val - min_b) / (max_b - min_b)) * 100
    else:
        if val <= min_b: return 100
        if val >= max_b: return 0
        return ((max_b - val) / (max_b - min_b)) * 100

def run_scoring():
    print("=" * 65)
    print("  ANALYTICS -- Financial Health Scoring Engine")
    print("=" * 65)

    # 1. Fetch data for latest fiscal year per company
    with engine.connect() as conn:
        pl = pd.read_sql("SELECT * FROM fact_profit_loss", conn)
        bs = pd.read_sql("SELECT * FROM fact_balance_sheet", conn)
        cf = pd.read_sql("SELECT * FROM fact_cash_flow", conn)
        ga = pd.read_sql("SELECT * FROM fact_analysis", conn)

    # Get latest data per symbol
    latest_year = pl.groupby('company_id')['fiscal_year'].max().reset_index()
    pl = pl.merge(latest_year, on=['company_id', 'fiscal_year'])
    bs = bs.merge(latest_year, on=['company_id', 'fiscal_year'])
    cf = cf.merge(latest_year, on=['company_id', 'fiscal_year'])

    symbols = pl['company_id'].unique()
    scores_list = []

    for sym in symbols:
        # Extract company data
        c_pl = pl[pl['company_id'] == sym].iloc[0]
        c_bs = bs[bs['company_id'] == sym].iloc[0] if sym in bs['company_id'].values else None
        c_cf = cf[cf['company_id'] == sym].iloc[0] if sym in cf['company_id'].values else None
        c_ga = ga[ga['symbol'] == sym] if sym in ga['symbol'].values else None

        # --- Component Scoring ---
        
        # 1. Profitability (30%)
        s_roe = score_metric(c_pl.get('roe_pct', 0), (5, 20))
        s_opm = score_metric(c_pl.get('opm_pct', 0), (5, 25))
        s_npm = score_metric(c_pl.get('net_profit_margin_pct', 0), (3, 15))
        profit_score = (s_roe + s_opm + s_npm) / 3

        # 2. Growth (20%)
        # Filter for 3Y or 5Y growth if available
        s_sales_g = 50
        s_profit_g = 50
        if c_ga is not None:
            sales_g = c_ga[c_ga['metric'] == 'compounded_sales_growth']['value_pct'].mean()
            profit_g = c_ga[c_ga['metric'] == 'compounded_profit_growth']['value_pct'].mean()
            s_sales_g = score_metric(sales_g, (5, 20))
            s_profit_g = score_metric(profit_g, (5, 20))
        growth_score = (s_sales_g + s_profit_g) / 2

        # 3. Leverage (20%)
        s_de = 100
        s_ic = 100
        if c_bs is not None:
            s_de = score_metric(c_bs.get('debt_to_equity', 0), (0.2, 1.5), ascending=False)
            s_ic = score_metric(c_pl.get('interest_coverage', 10), (1.5, 8))
        leverage_score = (s_de + s_ic) / 2

        # 4. Cashflow (30%)
        s_fcf = 100 if c_cf is not None and c_cf.get('free_cash_flow', 0) > 0 else 0
        cashflow_score = s_fcf # Keep it simple for now

        # --- Aggregate ---
        overall_score = (profit_score * 0.3) + (growth_score * 0.2) + (leverage_score * 0.2) + (cashflow_score * 0.3)
        
        scores_list.append({
            'symbol': sym,
            'computed_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'overall_score': round(overall_score, 2),
            'profitability_score': round(profit_score, 2),
            'growth_score': round(growth_score, 2),
            'leverage_score': round(leverage_score, 2),
            'cashflow_score': round(cashflow_score, 2),
            'health_label': get_label(overall_score)
        })

    # Save to fact_ml_scores
    df_scores = pd.DataFrame(scores_list)
    df_scores.insert(0, 'id', range(1, len(df_scores) + 1))
    df_scores.to_sql('fact_ml_scores', engine, if_exists='replace', index=False)
    
    print(f"  [OK] Computed health scores for {len(symbols)} companies.")
    print(f"  [OK] Ratings Distribution: {df_scores['health_label'].value_counts().to_dict()}")
    print("=" * 65)

if __name__ == "__main__":
    run_scoring()
