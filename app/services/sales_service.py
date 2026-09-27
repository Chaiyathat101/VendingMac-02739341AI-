from app.database import get_connection


def record_sale(
    product_id: int,
    quantity: int,
    unit_price: float,
    total_price: float,
    payment_method: str,
    amount_paid: float,
):
    conn = get_connection()
    try:
        change = round(amount_paid - total_price, 2)
        conn.execute(
            """
            INSERT INTO sales (product_id, quantity, unit_price, total_price, payment_method, amount_paid, change_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (product_id, quantity, unit_price, total_price, payment_method, amount_paid, change),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def get_sales_history(limit: int = 20):
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT s.*, p.name AS product_name, p.category
            FROM sales s
            JOIN products p ON p.id = s.product_id
            ORDER BY s.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_total_revenue():
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(total_price), 0) AS total FROM sales"
        ).fetchone()
        return float(row["total"]) if row else 0.0
    finally:
        conn.close()


def get_sales_last_7_days(product_id: int) -> int:
    """จำนวนที่ขายได้ใน 7 วันล่าสุด — ใช้กับ stock forecast"""
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT COALESCE(SUM(quantity), 0) AS total
            FROM sales
            WHERE product_id = ?
              AND sold_at >= datetime('now', '-7 days')
            """,
            (product_id,),
        ).fetchone()
        return int(row["total"]) if row else 0
    finally:
        conn.close()
