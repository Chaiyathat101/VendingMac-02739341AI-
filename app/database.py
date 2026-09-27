import sqlite3
from pathlib import Path

from app.config import DB_PATH


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                low_stock_threshold INTEGER NOT NULL DEFAULT 5,
                status TEXT NOT NULL DEFAULT 'active',
                image_url TEXT,
                category TEXT NOT NULL DEFAULT 'general',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                payment_method TEXT NOT NULL,
                amount_paid REAL NOT NULL,
                change_amount REAL NOT NULL,
                sold_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'admin'
            )
            """
        )

        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('machine_name', 'ตู้เครื่องเขียนอัตโนมัติ')")
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('currency', 'บาท')")

        # seed สินค้าเครื่องเขียน (name, price, stock, threshold, category, image_url=emoji)
        stationery = [
            ("ปากกาลูกลื่น (ดำ)",         5.0,  50, 10, "ปากกา",   "🖊️"),
            ("ปากกาลูกลื่น (แดง)",        5.0,  40, 10, "ปากกา",   "🖊️"),
            ("ปากกาลูกลื่น (น้ำเงิน)",    5.0,  45, 10, "ปากกา",   "🖊️"),
            ("ดินสอ 2B",                   8.0,  30,  8, "ดินสอ",   "✏️"),
            ("ดินสอ HB",                   6.0,  35,  8, "ดินสอ",   "✏️"),
            ("ยางลบ",                      5.0,  25,  5, "อุปกรณ์","🧹"),
            ("ไม้บรรทัด 30 ซม.",          15.0,  20,  5, "อุปกรณ์","📏"),
            ("กรรไกร",                    25.0,  15,  3, "อุปกรณ์","✂️"),
            ("เทปกาว",                    20.0,  20,  5, "อุปกรณ์","📎"),
            ("กระดาษโน้ต (100 แผ่น)",    18.0,  25,  5, "กระดาษ",  "📝"),
            ("สมุด A5",                   35.0,  20,  5, "กระดาษ",  "📓"),
            ("สมุด A4",                   45.0,  15,  3, "กระดาษ",  "📔"),
            ("ปากกาเน้นข้อความ (เหลือง)",12.0,  30,  8, "ปากกา",   "🖍️"),
            ("ปากกาเน้นข้อความ (ชมพู)",  12.0,  25,  8, "ปากกา",   "🖍️"),
            ("คลิปดำ ขนาดเล็ก (แพ็ค)",  10.0,  30,  5, "อุปกรณ์","🔗"),
        ]
        for name, price, stock, threshold, category, emoji in stationery:
            conn.execute(
                """
                INSERT OR IGNORE INTO products (name, price, stock, low_stock_threshold, status, category, image_url)
                SELECT ?, ?, ?, ?, 'active', ?, ?
                WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = ?)
                """,
                (name, price, stock, threshold, category, emoji, name),
            )

        conn.commit()
    finally:
        conn.close()
