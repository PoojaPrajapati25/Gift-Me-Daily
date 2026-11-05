
import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("database/giftmedaily.db")

# Create cursor
cursor = conn.cursor()

# Create prediction history table
cursor.execute("""
CREATE TABLE IF NOT EXISTS prediction_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    product_name TEXT,
    product_value REAL,
    destination_pin TEXT,
    weight REAL,
    shipping_cost REAL,
    delivery_days REAL,
    prediction_date TEXT
)
""")


# Save changes
conn.commit()

conn.close()

print("Database created/updated successfully!")
