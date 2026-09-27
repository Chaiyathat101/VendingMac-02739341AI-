"""
Migration script — เพิ่ม column ที่ขาด
รัน: python migrate.py
"""
import sqlite3
from app.config import DB_PATH

conn = sqlite3.connect(DB_PATH)

migrations = [
    ("products", "category", "ALTER TABLE products ADD COLUMN category TEXT NOT NULL DEFAULT 'general'"),
    ("sales",    "unit_price", "ALTER TABLE sales ADD COLUMN unit_price REAL NOT NULL DEFAULT 0"),
]

for table, col, sql in migrations:
    try:
        conn.execute(sql)
        conn.commit()
        print(f"✅ {table}.{col} added")
    except sqlite3.OperationalError as e:
        print(f"⏭  {table}.{col}: {e}")

conn.close()
print("Migration done.")
