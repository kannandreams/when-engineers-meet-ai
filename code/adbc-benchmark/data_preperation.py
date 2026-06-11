import sqlite3
import random
import string
import time

DB_PATH = "benchmark.db"
ROW_COUNT = 1_000_000

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS test_data")

cur.execute("""
CREATE TABLE test_data (
    id INTEGER PRIMARY KEY,
    val_int INTEGER,
    val_float REAL,
    val_str TEXT
)
""")

start = time.time()

batch_size = 10000

for batch_start in range(0, ROW_COUNT, batch_size):
    rows = []

    for i in range(batch_start, batch_start + batch_size):
        rows.append(
            (
                i,
                random.randint(1, 1000000),
                random.random() * 1000,
                ''.join(random.choices(string.ascii_letters, k=20))
            )
        )

    cur.executemany(
        """
        INSERT INTO test_data
        (id, val_int, val_float, val_str)
        VALUES (?, ?, ?, ?)
        """,
        rows
    )

    conn.commit()

    print(f"Inserted {batch_start + batch_size:,} rows")

conn.close()

print(f"Completed in {time.time() - start:.2f}s")