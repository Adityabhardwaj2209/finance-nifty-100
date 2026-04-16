import sqlite3
import os

db_path = 'nifty100_warehouse.db'
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    print("Tables found in DB:")
    for t in tables:
        table_name = t[0]
        print(f" - {table_name}")
        cur.execute(f"PRAGMA table_info({table_name});")
        cols = cur.fetchall()
        for c in cols:
            print(f"    - {c[1]} ({c[2]})")
    conn.close()
