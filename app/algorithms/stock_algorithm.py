"""
Smart Stock Algorithm
- ตรวจสถานะ stock
- คำนวณอัตราการขายเฉลี่ยต่อวัน
- พยากรณ์ว่าสินค้าจะหมดใน N วัน
"""
from datetime import datetime, timedelta


def can_sell(stock: int, quantity: int) -> bool:
    return stock >= quantity


def get_stock_status(stock: int, threshold: int) -> str:
    if stock <= 0:
        return "out_of_stock"
    if stock <= threshold:
        return "low_stock"
    return "ok"


def get_stock_label(status: str) -> str:
    labels = {
        "ok": "ปกติ",
        "low_stock": "ใกล้หมด",
        "out_of_stock": "หมด",
    }
    return labels.get(status, status)


def forecast_days_remaining(stock: int, sales_last_7_days: int) -> dict:
    """
    พยากรณ์ว่าสินค้าจะหมดในกี่วัน
    Args:
        stock: จำนวน stock ปัจจุบัน
        sales_last_7_days: จำนวนที่ขายได้ใน 7 วันล่าสุด
    Returns:
        dict พร้อม avg_daily, days_remaining, restock_recommended
    """
    if sales_last_7_days <= 0:
        return {
            "avg_daily_sales": 0.0,
            "days_remaining": None,  # ไม่มีข้อมูลพอ
            "restock_recommended": False,
            "message": "ยังไม่มีข้อมูลการขาย",
        }

    avg_daily = round(sales_last_7_days / 7, 2)

    if avg_daily == 0:
        days_remaining = None
        restock = False
    else:
        days_remaining = int(stock / avg_daily)
        restock = days_remaining <= 7  # แนะนำเติมถ้าจะหมดใน 7 วัน

    return {
        "avg_daily_sales": avg_daily,
        "days_remaining": days_remaining,
        "restock_recommended": restock,
        "message": f"คาดว่าสินค้าจะหมดใน {days_remaining} วัน" if days_remaining is not None else "ขายช้า",
    }
