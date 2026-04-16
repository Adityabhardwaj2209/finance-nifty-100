"""
ETL Script 4: AI & ML Scoring Engine.
Computes financial health scores for all companies using star-schema data.
Output: Writes to 'fact_ml_scores' table in nifty100_warehouse.db
"""
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "nifty100_warehouse.db"
engine = create_engine(f"sqlite:///{DB_PATH}")

def calculate_scores():
    print("  [1/4] Fetching data for scoring...")
    
    # Get latest P&L and Balance Sheet figures
    query = """
    SELECT 
        c.id as symbol,
        pl.net_profit_margin_pct,
        pl.return_on_assets,
        bs.debt_to_equity,
        cf.free_cash_flow
    FROM dim_company c
    LEFT JOIN fact_profit_loss pl ON c.id = pl.company_id
    LEFT JOIN fact_balance_sheet bs ON c.id = bs.company_id AND pl.fiscal_year = bs.fiscal_year
    LEFT JOIN fact_cash_flow cf ON c.id = cf.company_id AND pl.fiscal_year = cf.fiscal_year
    WHERE pl.is_ttm = 1 OR pl.fiscal_year = (SELECT MAX(fiscal_year) FROM fact_profit_loss)
    """
    
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    
    if df.empty:
        print("  [ERROR] No data found for scoring. Run steps 1-3 first.")
        return

    print(f"  [2/4] Scoring {len(df)} companies...")

    # Scoring Logic (0-10 scale)
    # ---------------------------
    
    # 1. Profitability (0.3 weight)
    # Target: NPM > 15% is good, ROA > 10% is good
    df['profit_score'] = (
        np.clip(df['net_profit_margin_pct'] / 2, 0, 5) + 
        np.clip(df['return_on_assets'] / 2, 0, 5)
    ).fillna(0)
    
    # 2. Growth (0.3 weight) - Fetch from fact_analysis
    # Since fact_analysis is period-based, we'll average the 5Y and 10Y growths
    query_growth = "SELECT symbol, AVG(value_pct) as avg_growth FROM fact_analysis GROUP BY symbol"
    with engine.connect() as conn:
        df_growth = pd.read_sql(text(query_growth), conn)
    
    df = df.merge(df_growth, on='symbol', how='left')
    df['growth_score'] = np.clip(df['avg_growth'] / 2, 0, 10).fillna(0)
    
    # 3. Leverage (0.2 weight)
    # Target: Debt-to-Equity < 1.0 is healthy. Score = 10 - (D/E * 5)
    df['leverage_score'] = np.clip(10 - (df['debt_to_equity'].fillna(2) * 5), 0, 10)
    
    # 4. Cashflow (0.2 weight)
    # Target: Positive FCF. Score = 10 if FCF > 0, else 0.
    df['cashflow_score'] = df['free_cash_flow'].apply(lambda x: 10 if x > 0 else 0).fillna(0)
    
    # Overall Score (Weighted Average)
    df['overall_score'] = (
        df['profit_score'] * 0.3 + 
        df['growth_score'] * 0.3 + 
        df['leverage_score'] * 0.2 + 
        df['cashflow_score'] * 0.2
    ).round(2)

    # Health Label
    def get_label(score):
        if score >= 8: return "Excellent"
        if score >= 6: return "Stable"
        if score >= 4: return "Average"
        return "Risky"
    
    df['health_label'] = df['overall_score'].apply(get_label)
    df['computed_at'] = datetime.now()
    
    # Add auto-increment ID for Django primary key
    df = df.reset_index().rename(columns={'index': 'id'})
    df['id'] = df['id'] + 1

    # Prepare for output
    cols_to_save = [
        'id', 'symbol', 'overall_score', 'profitability_score', 'growth_score', 
        'leverage_score', 'cashflow_score', 'health_label', 'computed_at'
    ]
    # Map internal names to model names
    df_output = df.rename(columns={'profit_score': 'profitability_score'})[cols_to_save]
    
    print("  [3/4] Saving scores to database...")
    df_output.to_sql('fact_ml_scores', engine, if_exists='replace', index=False)
    
    print(f"  [4/4] Successfully scored {len(df_output)} companies.")
    print("=" * 65)

def main():
    print("=" * 65)
    print("  ETL STEP 4 -- AI Performance Scoring")
    print("=" * 65)
    try:
        calculate_scores()
    except Exception as e:
        print(f"  [ERROR] Scoring failed: {e}")

if __name__ == "__main__":
    main()
