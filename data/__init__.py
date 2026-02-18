import os, sqlite3, pandas as pd

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DATA_DIR, "crm.db")
DDL = [
    "CREATE TABLE IF NOT EXISTS accounts (account TEXT PRIMARY KEY, sector TEXT, year_established INTEGER, revenue REAL, employees INTEGER, office_location TEXT, subsidiary_of TEXT)",
    "CREATE TABLE IF NOT EXISTS products (product TEXT PRIMARY KEY, series TEXT, sales_price REAL)",
    "CREATE TABLE IF NOT EXISTS sales_teams (sales_agent TEXT PRIMARY KEY, manager TEXT, regional_office TEXT)",
    "CREATE TABLE IF NOT EXISTS sales_pipeline (opportunity_id TEXT PRIMARY KEY, sales_agent TEXT, product TEXT, account TEXT, deal_stage TEXT, engage_date TEXT, close_date TEXT, close_value REAL)"
]

def init_db():
    c = sqlite3.connect(DB_PATH)
    for ddl in DDL: c.execute(ddl)
    c.commit()
    c.close()

def load_data():
    c = sqlite3.connect(DB_PATH)
    for name, key in [("accounts.csv", "account"), ("products.csv", "product"), ("sales_teams.csv", "sales_agent"), ("sales_pipeline.csv", "opportunity_id")]:
        p = os.path.join(DATA_DIR, name)
        if not os.path.isfile(p): continue
        df = pd.read_csv(p).drop_duplicates(subset=[key])
        for col in ["close_value", "revenue", "sales_price", "employees", "year_established"]:
            if col in df.columns: df[col] = pd.to_numeric(df[col], errors="coerce")
        for col in ["engage_date", "close_date"]:
            if col in df.columns: df[col] = df[col].astype(str)
        df.to_sql(name.replace(".csv", ""), c, if_exists="append", index=False)
    c.close()

def verify():
    c = sqlite3.connect(DB_PATH)
    cur = c.cursor()
    for t in ("sales_pipeline", "accounts", "products", "sales_teams"):
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"{t}: {cur.fetchone()[0]}")
    print("\nSample:")
    for r in cur.execute("SELECT * FROM sales_pipeline LIMIT 5").fetchall(): print(r)
    c.close()

__all__ = ["DB_PATH", "DATA_DIR", "init_db", "load_data", "verify"]
