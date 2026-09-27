from app.database import get_connection


def get_all_products():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM products ORDER BY category, name ASC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_product_by_id(product_id: int):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_product(data: dict):
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO products (name, price, stock, low_stock_threshold, status, image_url, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["name"],
                data["price"],
                data["stock"],
                data.get("low_stock_threshold", 5),
                data.get("status", "active"),
                data.get("image_url"),
                data.get("category", "general"),
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_product(product_id: int, data: dict):
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE products
            SET name = ?, price = ?, stock = ?, low_stock_threshold = ?,
                status = ?, image_url = ?, category = ?
            WHERE id = ?
            """,
            (
                data["name"],
                data["price"],
                data["stock"],
                data.get("low_stock_threshold", 5),
                data.get("status", "active"),
                data.get("image_url"),
                data.get("category", "general"),
                product_id,
            ),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def delete_product(product_id: int):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        return True
    finally:
        conn.close()


def reduce_stock(product_id: int, quantity: int):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?",
            (quantity, product_id, quantity),
        )
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()


def update_product_image(product_id: int, image_url: str):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE products SET image_url = ? WHERE id = ?",
            (image_url, product_id),
        )
        conn.commit()
        return True
    finally:
        conn.close()
