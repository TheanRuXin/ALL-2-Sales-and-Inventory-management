import sqlite3

conn = sqlite3.connect("Trackwise.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS sales")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                item_name TEXT NOT NULL,
                unit_price TEXT NOT NULL,
                quantity_sold INTEGER NOT NULL,
                sale_date TEXT NOT NULL,
                total_price REAL NOT NULL
    )
""")

print("Table 'inventory' recreated with 'product_id' column.")
conn.commit()
conn.close()
