import os, pandas as pd
from .config import DATA_DIR, ENABLE_DUCKDB
import duckdb

def write_parquet(df: pd.DataFrame, name: str):
    path = os.path.join(DATA_DIR, "parquet", f"{name}.parquet")
    df.to_parquet(path, index=False)
    return path

def append_parquet(df: pd.DataFrame, name: str):
    path = os.path.join(DATA_DIR, "parquet", f"{name}.parquet")
    if os.path.exists(path):
        prev = pd.read_parquet(path)
        df = pd.concat([prev, df]).drop_duplicates(subset=["event_id"])
    df.to_parquet(path, index=False)
    return path

def upsert_duckdb(df: pd.DataFrame, table: str):
    if not ENABLE_DUCKDB: return
    dbpath = os.path.join(DATA_DIR, "db", "labels.duckdb")
    os.makedirs(os.path.dirname(dbpath), exist_ok=True)
    con = duckdb.connect(dbpath)
    try:
        con.execute(f"CREATE TABLE IF NOT EXISTS {table} AS SELECT * FROM df LIMIT 0")
    except Exception:
        pass
    con.register("df", df)
    cols = ", ".join(df.columns)
    con.execute(f"INSERT INTO {table} SELECT {cols} FROM df")
    con.close()
