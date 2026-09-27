def inventory_status(stock: int, threshold: int) -> str:
    if stock <= 0:
        return "out_of_stock"
    if stock <= threshold:
        return "low_stock"
    return "ok"
