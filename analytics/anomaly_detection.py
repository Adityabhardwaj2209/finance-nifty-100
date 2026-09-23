"""Local, unsupervised screening of unusual company financials.

This model compares each company's latest complete fiscal year with historical
company-year observations. It makes no investment or fraud prediction.
"""
from functools import lru_cache
from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import RobustScaler

DB_PATH = Path(__file__).resolve().parent.parent / "nifty100_warehouse.db"
FEATURES = {
    "net_profit_margin_pct": "Net profit margin",
    "opm_percentage": "Operating margin",
    "debt_to_equity": "Debt to equity",
    "free_cash_flow_margin_pct": "Free cash flow to sales",
}


@lru_cache(maxsize=2)
def _fit(db_path, modified_ns):
    with sqlite3.connect(db_path) as conn:
        data = pd.read_sql_query("""
            SELECT p.company_id AS symbol, p.fiscal_year, p.sales,
                   p.net_profit_margin_pct, p.opm_percentage,
                   b.debt_to_equity, f.free_cash_flow
            FROM fact_profit_loss p
            LEFT JOIN fact_balance_sheet b
              ON b.company_id = p.company_id AND b.fiscal_year = p.fiscal_year
              AND COALESCE(b.is_ttm, 0) = 0
            LEFT JOIN fact_cash_flow f
              ON f.company_id = p.company_id AND f.fiscal_year = p.fiscal_year
              AND COALESCE(f.is_ttm, 0) = 0
            WHERE COALESCE(p.is_ttm, 0) = 0 AND p.fiscal_year IS NOT NULL
        """, conn)
    data = data.drop_duplicates(["symbol", "fiscal_year"])
    data["free_cash_flow_margin_pct"] = np.where(
        data["sales"].abs() > 0,
        100 * data["free_cash_flow"] / data["sales"], np.nan)
    for feature in FEATURES:
        data[feature] = pd.to_numeric(data[feature], errors="coerce")
        data[feature] = data[feature].replace([np.inf, -np.inf], np.nan)
        # Prevent a single malformed ratio from dominating the fitted model.
        data[feature] = data[feature].clip(-300, 300)
    data = data[data[list(FEATURES)].notna().sum(axis=1) >= 3].copy()
    if len(data) < 30:
        raise ValueError("At least 30 financial records are required")
    features = list(FEATURES)
    transform = make_pipeline(SimpleImputer(strategy="median"), RobustScaler())
    matrix = transform.fit_transform(data[features])
    model = IsolationForest(n_estimators=150, contamination=0.10,
                            random_state=42, n_jobs=1).fit(matrix)
    data["anomaly_score"] = model.decision_function(matrix)
    data["flagged"] = model.predict(matrix) == -1
    return data, transform.named_steps["robustscaler"], len(data)


def company_anomaly(symbol, db_path=DB_PATH):
    path = Path(db_path)
    data, scaler, count = _fit(str(path), path.stat().st_mtime_ns)
    company = data[data.symbol == symbol].sort_values("fiscal_year")
    if company.empty:
        return None
    row = company.iloc[-1]
    deviations = []
    for feature, label in FEATURES.items():
        value = row[feature]
        if pd.notna(value):
            index = list(FEATURES).index(feature)
            distance = abs((value - scaler.center_[index]) / scaler.scale_[index])
            deviations.append((distance, label, float(value)))
    deviations.sort(reverse=True)
    return {
        "symbol": symbol,
        "fiscal_year": int(row.fiscal_year),
        "flagged": bool(row.flagged),
        "anomaly_score": round(float(row.anomaly_score), 4),
        "observations": count,
        "top_deviations": [
            {"metric": label, "value": round(value, 2)}
            for _, label, value in deviations[:2]
        ],
        "method": "Isolation Forest on four financial ratios, trained locally on historical company-year records",
        "disclaimer": "An unusual record is a prompt for review, not evidence of fraud or an investment recommendation.",
    }
