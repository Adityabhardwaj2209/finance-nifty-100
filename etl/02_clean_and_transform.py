"""
ETL Script 2: Clean and Transform raw CSVs into a standardized Star Schema format.
Input: data/raw/*.csv, data/sector_mapping.csv
Output: data/clean/*.csv
"""
import os
import pandas as pd
import numpy as np
import re
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "clean"
MAPPING_FILE = BASE_DIR / "data" / "sector_mapping.csv"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

# ── Helper Functions ──────────────────────────────────────────────────

def to_snake_case(name):
    """Standardize column names."""
    s = str(name).strip()
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()
    return re.sub(r'[^a-z0-9_]', '_', s).strip('_')

def parse_year(year_str):
    """
    Standardize various year formats: 'Mar 2024', 'Mar-24', 'TTM'.
    Returns (fiscal_year_int, label_str, is_ttm).
    """
    s = str(year_str).strip()
    if s == 'TTM':
        return 2024, 'TTM', True
    
    # Try 'Mar 2024'
    match_4 = re.search(r'(\d{4})', s)
    if match_4:
        y = int(match_4.group(1))
        return y, s, False
    
    # Try 'Mar-24'
    match_2 = re.search(r'-(\d{2})$', s)
    if match_2:
        yy = int(match_2.group(1))
        y = 2000 + yy if yy < 50 else 1900 + yy
        return y, s, False
    
    return np.nan, s, False

def parse_growth(val_str):
    """
    Parse '10 Years: 17%' -> (period, value_float)
    """
    s = str(val_str).strip()
    match = re.search(r'(\d+)\s*Years?:\s*(-?\d+\.?\d*)%', s, re.IGNORECASE)
    if match:
        return f"{match.group(1)}Y", float(match.group(2))
    
    # Handle TTM in growth
    if "TTM" in s.upper():
        match_ttm = re.search(r'(-?\d+\.?\d*)%', s)
        if match_ttm:
            return "TTM", float(match_ttm.group(1))
            
    return None, np.nan

# ── Processors ────────────────────────────────────────────────────────

def process_companies():
    df = pd.read_csv(RAW_DIR / "companies.csv")
    df.columns = [to_snake_case(c) for c in df.columns]
    
    # Merge with sector mapping
    if MAPPING_FILE.exists():
        mapping = pd.read_csv(MAPPING_FILE)
        df = df.merge(mapping, left_on='id', right_on='symbol', how='left')
        df.drop(columns=['symbol'], inplace=True, errors='ignore')
    
    df.to_csv(CLEAN_DIR / "dim_company.csv", index=False)
    return df

def process_analysis():
    df = pd.read_csv(RAW_DIR / "analysis.csv")
    df.columns = [to_snake_case(c) for c in df.columns]
    
    # Melt the growth columns if they exist (compounded_sales_growth, etc.)
    # The structure in analysis.xlsx was one row per company with different metrics as columns
    rows = []
    growth_cols = ['compounded_sales_growth', 'compounded_profit_growth', 'stock_price_cagr', 'roe']
    
    for _, row in df.iterrows():
        symbol = row['company_id']
        for col in growth_cols:
            if col in df.columns:
                period, val = parse_growth(row[col])
                if period:
                    rows.append({
                        'symbol': symbol,
                        'metric': col,
                        'period': period,
                        'value_pct': val
                    })
    
    df_clean = pd.DataFrame(rows)
    df_clean.to_csv(CLEAN_DIR / "fact_analysis.csv", index=False)

def process_financials():
    # Load raw tables
    bs = pd.read_csv(RAW_DIR / "balancesheet.csv")
    pl = pd.read_csv(RAW_DIR / "profitandloss.csv")
    cf = pd.read_csv(RAW_DIR / "cashflow.csv")
    
    # Standardize columns
    for df in [bs, pl, cf]:
        df.columns = [to_snake_case(c) for c in df.columns]
        # Standardize Year
        year_info = df['year'].apply(parse_year)
        df['fiscal_year'] = [x[0] for x in year_info]
        df['year_label'] = [x[1] for x in year_info]
        df['is_ttm'] = [x[2] for x in year_info]

    # Create CLEAN versions
    # We will compute columns during loading or here? Brief says "during ETL".
    
    # --- Balance Sheet Computations ---
    bs['debt_to_equity'] = bs['borrowings'] / (bs['equity_capital'] + bs['reserves'])
    bs['equity_ratio'] = (bs['equity_capital'] + bs['reserves']) / bs['total_assets']
    # Note: book_value_per_share needs shares_outstanding, usually not in BS.
    # We'll skip it or use a simplified placeholder.
    
    # --- P&L Computations ---
    pl['net_profit_margin_pct'] = (pl['net_profit'] / pl['sales']) * 100
    pl['expense_ratio_pct'] = (pl['expenses'] / pl['sales']) * 100
    pl['interest_coverage'] = pl['operating_profit'] / pl['interest']
    
    # --- Cash Flow Computations ---
    cf['free_cash_flow'] = cf['operating_activity'] + cf['investing_activity']
    
    # Joins for cross-table metrics (e.g., Asset Turnover = Sales / Total Assets)
    # We'll do this in a merged 'fact_financials' or separate facts. 
    # Let's keep them separate as per Star Schema brief but compute what we can.
    
    # Asset turnover (Sales from P&L, Assets from BS)
    # This requires a join on (company_id, fiscal_year)
    merged_pl_bs = pl.merge(bs[['company_id', 'fiscal_year', 'total_assets']], on=['company_id', 'fiscal_year'], how='left')
    pl['asset_turnover'] = merged_pl_bs['sales'] / merged_pl_bs['total_assets']
    pl['return_on_assets'] = (merged_pl_bs['net_profit'] / merged_pl_bs['total_assets']) * 100

    # Save
    bs.to_csv(CLEAN_DIR / "fact_balance_sheet.csv", index=False)
    pl.to_csv(CLEAN_DIR / "fact_profit_loss.csv", index=False)
    cf.to_csv(CLEAN_DIR / "fact_cash_flow.csv", index=False)

def main():
    print("=" * 65)
    print("  ETL STEP 2 -- Standardize & Compute (Star Schema)")
    print("=" * 65)

    print("  [1/3] Processing Dim Company...")
    process_companies()
    
    print("  [2/3] Processing Fact Analysis (Growth Parsing)...")
    process_analysis()
    
    print("  [3/3] Processing Financials (Fact Tables + Computations)...")
    process_financials()
    
    # Other tables
    for other in ["prosandcons", "documents"]:
        csv = RAW_DIR / f"{other}.csv"
        if csv.exists():
            df = pd.read_csv(csv)
            df.columns = [to_snake_case(c) for c in df.columns]
            df.to_csv(CLEAN_DIR / f"fact_{other}.csv", index=False)

    print("\n  Cleaned Star-Schema Fact & Dimension CSVs saved to:", CLEAN_DIR)
    print("=" * 65)

if __name__ == "__main__":
    main()
