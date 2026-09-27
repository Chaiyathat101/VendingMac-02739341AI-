from fastapi import APIRouter, HTTPException

from app.algorithms.pricing_algorithm import get_price_summary
from app.models import SaleRequest
from app.services.product_service import get_product_by_id, reduce_stock
from app.services.sales_service import get_sales_history, get_total_revenue, record_sale

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("")
def sales_history():
    return get_sales_history(limit=50)


@router.get("/revenue")
def revenue():
    return {"total_revenue": get_total_revenue()}


MAX_ITEMS_PER_ORDER = 3

@router.post("")
def sell_product(payload: SaleRequest):
    product = get_product_by_id(payload.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="ไม่พบสินค้า")

    if payload.quantity > MAX_ITEMS_PER_ORDER:
        raise HTTPException(status_code=400, detail=f"เลือกได้สูงสุด {MAX_ITEMS_PER_ORDER} ชิ้นต่อรอบ")

    if product["status"] != "active":
        raise HTTPException(status_code=400, detail="สินค้าไม่พร้อมขาย")

    if product["stock"] < payload.quantity:
        raise HTTPException(status_code=400, detail="สินค้าไม่เพียงพอ")

    pricing = get_price_summary(
        base_price=product["price"],
        stock=product["stock"],
        threshold=product["low_stock_threshold"],
        quantity=payload.quantity,
    )

    total_price = pricing["total"]

    if payload.amount_paid < total_price:
        raise HTTPException(
            status_code=400,
            detail=f"เงินไม่พอ ต้องจ่าย {total_price} บาท",
        )

    change = round(payload.amount_paid - total_price, 2)

    success = reduce_stock(payload.product_id, payload.quantity)
    if not success:
        raise HTTPException(status_code=400, detail="ไม่สามารถอัปเดต stock ได้")

    record_sale(
        product_id=payload.product_id,
        quantity=payload.quantity,
        unit_price=pricing["unit_price"],
        total_price=total_price,
        payment_method=payload.payment_method,
        amount_paid=payload.amount_paid,
    )

    return {
        "message": "ซื้อสำเร็จ! ขอบคุณค่ะ",
        "product_name": product["name"],
        "quantity": payload.quantity,
        "unit_price": pricing["unit_price"],
        "subtotal": pricing["subtotal"],
        "discount": pricing["discount"],
        "total_price": total_price,
        "amount_paid": payload.amount_paid,
        "change": change,
        "surcharge_active": pricing["surcharge_active"],
    }
