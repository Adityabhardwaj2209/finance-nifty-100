"""
Helper Script: Generate scriptticker.sql from Excel source data.
Purpose: Simulate the source SQL dump requested in the brief.
"""
import pandas as pd
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
EXCEL_DIR = BASE_DIR
SQL_OUT = BASE_DIR / "scriptticker.sql"

TABLES = {
    "companies.xlsx": "companies",
    "analysis.xlsx": "analysis",
    "balancesheet.xlsx": "balancesheet",
    "profitandloss.xlsx": "profitandloss",
    "cashflow.xlsx": "cashflow",
    "prosandcons.xlsx": "prosandcons",
    "documents.xlsx": "documents"
}

def escape_sql(val):
    if pd.isna(val):
        return "NULL"
    s = str(val).replace("'", "''")
    return f"'{s}'"

def generate_sql():
    sql_lines = []
    
    for xlsx_name, table_name in TABLES.items():
        xlsx_path = EXCEL_DIR / xlsx_name
        if not xlsx_path.exists():
            print(f"  [SKIP] {xlsx_name} not found")
            continue
            
        # Read Excel (skipping the title row)
        df = pd.read_excel(xlsx_path, header=None)
        if len(df) < 2:
            continue
            
        columns = [str(c).strip() for c in df.iloc[1]]
        data = df.iloc[2:]
        
        print(f"  Processing {xlsx_name} -> {table_name} ({len(data)} rows)")
        
        for _, row in data.iterrows():
            vals = [escape_sql(v) for v in row]
            line = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(vals)});"
            sql_lines.append(line)
            
    with open(SQL_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_lines))
        
    print(f"\n  Success! Created {SQL_OUT}")

if __name__ == "__main__":
    generate_sql()
