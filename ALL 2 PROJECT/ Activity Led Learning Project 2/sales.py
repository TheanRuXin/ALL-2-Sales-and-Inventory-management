import sqlite3

conn = sqlite3.connect("Trackwise.db")
cursor = conn.cursor()

# ⚠️ Delete the table if it already exists
cursor.execute("DROP TABLE IF EXISTS sales")

# ✅ Recreate it with correct columns
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    item_name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity_sold INTEGER NOT NULL,
    sale_date TEXT NOT NULL,
    total_price REAL NOT NULL
)
""")

conn.commit()
conn.close()
print("✅ 'sales' table created with 'category' column.")
