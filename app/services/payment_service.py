def calculate_total(product_price: float, quantity: int) -> float:
    return product_price * quantity


def calculate_change(total_price: float, amount_paid: float) -> float:
    if amount_paid < total_price:
        raise ValueError("เงินไม่พอ")
    return amount_paid - total_price
