import sqlite3
import time
import pandas as pd
import adbc_driver_sqlite.dbapi

DB_PATH = "benchmark.db"

def benchmark_sqlite3_row():
    start_time = time.time()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test_data")
    rows = cursor.fetchall()
    # Convert row-based data to columnar Pandas DataFrame
    df = pd.DataFrame(rows, columns=["id", "val_int", "val_float", "val_str"])
    duration = time.time() - start_time
    conn.close()
    return duration

def benchmark_adbc_columnar():
    start_time = time.time()
    with adbc_driver_sqlite.dbapi.connect(f"file:{DB_PATH}") as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM test_data")
            # Fetch directly as an Arrow Table
            table = cur.fetch_arrow_table()
            # Zero-copy or minimal-copy conversion to Pandas
            df = table.to_pandas()
    duration = time.time() - start_time
    return duration