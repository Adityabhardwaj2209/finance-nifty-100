import sqlite3

def check_db():
    conn = sqlite3.connect('nifty100_warehouse.db')
    cursor = conn.cursor()
    
    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables in DB: {tables}")
    
    for table in tables:
        print(f"\nSchema for {table}:")
        cursor.execute(f"PRAGMA table_info({table})")
        cols = cursor.fetchall()
        for col in cols:
            print(f"  {col}")
            
    conn.close()

if __name__ == "__main__":
    check_db()
