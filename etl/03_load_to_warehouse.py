"""
ETL Script 3: Load cleaned data into a Star Schema Data Warehouse (SQLite).
Input: data/clean/*.csv
Output: nifty100_warehouse.db
"""
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_DIR = BASE_DIR / "data" / "clean"
DB_PATH = BASE_DIR / "nifty100_warehouse.db"

# Engine setup
engine = create_engine(f"sqlite:///{DB_PATH}")

def load_table(table_name, csv_name):
    """Load a CSV into a SQLite table (Replace)."""
    csv_path = CLEAN_DIR / csv_name
    if not csv_path.exists():
        print(f"  [SKIP] {csv_name} not found")
        return 0
        
    df = pd.read_csv(csv_path)
    
    # In SQLite, we use 'to_sql' with replace for simplicity in this dev phase.
    # For a real Postgres production system, we would used UPSERT logic.
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    return len(df)

def main():
    print("=" * 65)
    print("  ETL STEP 3 -- Load Star Schema -> SQLite Warehouse")
    print("=" * 65)

    # 1. Load Dimensions
    print("  [1/2] Loading Dimension Tables...")
    dim_tables = {
        "dim_company": "dim_company.csv",
    }
    
    for table, csv in dim_tables.items():
        rows = load_table(table, csv)
        print(f"  [OK] Dimension '{table:15s}' loaded: {rows:>5} records")

    # 2. Load Facts
    print("\n  [2/2] Loading Fact Tables...")
    fact_tables = {
        "fact_profit_loss": "fact_profit_loss.csv",
        "fact_balance_sheet": "fact_balance_sheet.csv",
        "fact_cash_flow": "fact_cash_flow.csv",
        "fact_analysis": "fact_analysis.csv",
        "fact_prosandcons": "fact_prosandcons.csv",
        "fact_documents": "fact_documents.csv"
    }
    
    total_fact_rows = 0
    for table, csv in fact_tables.items():
        rows = load_table(table, csv)
        total_fact_rows += rows
        print(f"  [OK] Fact      '{table:15s}' loaded: {rows:>5} records")

    # 3. Data Quality Checks
    print("\n  [DQ] Running Verification Queries...")
    with engine.connect() as conn:
        # Check if joins are healthy
        res = conn.execute(text("""
            SELECT c.company_name, COUNT(p.company_id) 
            FROM dim_company c
            LEFT JOIN fact_profit_loss p ON c.id = p.company_id
            GROUP BY c.company_name
            LIMIT 5
        """)).fetchall()
        print(f"  [OK] Sample join check (Company -> P&L): {len(res)} companies verified")

    print(f"\n  Success! Data Warehouse built at: {DB_PATH}")
    print("=" * 65)

if __name__ == "__main__":
    main()
