"""
Pricing — ราคาคงที่ ไม่มี surcharge ไม่มีโปรโมชั่น
"""


def calculate_unit_price(base_price: float, stock: int, threshold: int) -> float:
    """ราคาต่อชิ้น = ราคาปกติเสมอ"""
    return base_price


def calculate_total(unit_price: float, quantity: int) -> float:
    return round(unit_price * quantity, 2)


def apply_bulk_discount(total: float, quantity: int) -> tuple[float, float]:
    """ไม่มีส่วนลด"""
    return total, 0.0


def get_price_summary(base_price: float, stock: int, threshold: int, quantity: int) -> dict:
    total = round(base_price * quantity, 2)
    return {
        "base_price": base_price,
        "unit_price": base_price,
        "quantity": quantity,
        "subtotal": total,
        "discount": 0.0,
        "total": total,
        "surcharge_active": False,
    }
