import sqlite3
import pandas as pd

conn = sqlite3.connect("database/giftmedaily.db")

df = pd.read_sql_query(
    "SELECT * FROM prediction_history ORDER BY id DESC",
    conn
)

print(df)

conn.close()