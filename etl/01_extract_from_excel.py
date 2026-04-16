"""
ETL Script 1: Extract data from Excel files into clean CSVs.
Source: 7 Excel files exported from MariaDB (Nifty 100 dataset).
Output: data/raw/*.csv  (one CSV per table)
"""
import os
import sys
import pandas as pd
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
EXCEL_DIR = BASE_DIR                       # xlsx files sit in project root
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# ── Mapping: xlsx filename → csv output name ──────────────────────────
TABLE_MAP = {
    "companies.xlsx":      "companies.csv",
    "analysis.xlsx":       "analysis.csv",
    "balancesheet.xlsx":   "balancesheet.csv",
    "profitandloss.xlsx":  "profitandloss.csv",
    "cashflow.xlsx":       "cashflow.csv",
    "prosandcons.xlsx":    "prosandcons.csv",
    "documents.xlsx":      "documents.csv",
}


def extract_excel(xlsx_path: Path, csv_name: str) -> pd.DataFrame:
    """
    Read an Excel file whose first row is a header/title row
    and second row contains the real column names.
    Returns the cleaned DataFrame.
    """
    # Read everything; row 0 is the decorative title, row 1 is column names
    raw = pd.read_excel(xlsx_path, header=None)

    if len(raw) < 2:
        return pd.DataFrame()

    # Row index 1 holds the real column names
    columns = [str(c).strip() if pd.notna(c) else f"Unnamed_{i}" for i, c in enumerate(raw.iloc[1])]
    
    # Handle duplicate column names by appending a suffix
    counts = {}
    new_cols = []
    for col in columns:
        if col in counts:
            counts[col] += 1
            new_cols.append(f"{col}_{counts[col]}")
        else:
            counts[col] = 0
            new_cols.append(col)
    
    df = raw.iloc[2:].copy()
    df.columns = new_cols
    df.reset_index(drop=True, inplace=True)

    # ── Basic cleaning ─────────────────────────────────────────────────
    # Replace literal string "NULL" / "null" / "Null" with NaN
    df.replace(["NULL", "Null", "null", ""], pd.NA, inplace=True)

    # Strip whitespace from string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace("nan", pd.NA)
        df[col] = df[col].replace("<NA>", pd.NA)

    # Save
    out_path = RAW_DIR / csv_name
    df.to_csv(out_path, index=False)
    return df


def main():
    print("=" * 65)
    print("  ETL STEP 1 -- Extract Excel -> Raw CSVs")
    print("=" * 65)

    for xlsx_name, csv_name in TABLE_MAP.items():
        xlsx_path = EXCEL_DIR / xlsx_name
        if not xlsx_path.exists():
            print(f"  [SKIP] {xlsx_name} not found at {xlsx_path}")
            continue

        df = extract_excel(xlsx_path, csv_name)
        print(f"  [OK] {xlsx_name:25s} -> {csv_name:25s}  rows={len(df):>5}  cols={list(df.columns)}")

    print("\n  All raw CSVs saved to:", RAW_DIR)
    print("=" * 65)


if __name__ == "__main__":
    main()
