import shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.algorithms.pricing_algorithm import calculate_unit_price
from app.algorithms.stock_algorithm import forecast_days_remaining, get_stock_label, get_stock_status
from app.models import ProductCreate, ProductUpdate
from app.services.product_service import (
    create_product,
    delete_product,
    get_all_products,
    get_product_by_id,
    update_product,
    update_product_image,
)
from app.services.sales_service import get_sales_last_7_days

IMAGES_DIR = Path(__file__).resolve().parent.parent / "static" / "images"
IMAGES_DIR.mkdir(exist_ok=True)
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

router = APIRouter(prefix="/products", tags=["products"])


def _enrich(product: dict) -> dict:
    status = get_stock_status(product["stock"], product["low_stock_threshold"])
    sales_7d = get_sales_last_7_days(product["id"])
    forecast = forecast_days_remaining(product["stock"], sales_7d)
    unit_price = calculate_unit_price(product["price"], product["stock"], product["low_stock_threshold"])
    product["status_text"] = status
    product["status_label"] = get_stock_label(status)
    product["unit_price"] = unit_price
    product["price_surcharge"] = unit_price > product["price"]
    product["forecast"] = forecast
    return product


@router.get("")
def list_products():
    return [_enrich(p) for p in get_all_products()]


@router.get("/{product_id}")
def get_product(product_id: int):
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="ไม่พบสินค้า")
    return _enrich(product)


@router.post("")
def add_product(payload: ProductCreate):
    product_id = create_product(payload.model_dump())
    return {"id": product_id, "message": "เพิ่มสินค้าสำเร็จ"}


@router.put("/{product_id}")
def edit_product(product_id: int, payload: ProductUpdate):
    if not get_product_by_id(product_id):
        raise HTTPException(status_code=404, detail="ไม่พบสินค้า")
    update_product(product_id, payload.model_dump())
    return {"message": "แก้ไขสินค้าสำเร็จ"}


@router.delete("/{product_id}")
def remove_product(product_id: int):
    if not get_product_by_id(product_id):
        raise HTTPException(status_code=404, detail="ไม่พบสินค้า")
    delete_product(product_id)
    return {"message": "ลบสินค้าสำเร็จ"}


@router.post("/{product_id}/image")
async def upload_image(product_id: int, file: UploadFile = File(...)):
    """อัปโหลดรูปสินค้า — รองรับ jpg, jpeg, png, gif, webp"""
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="ไม่พบสินค้า")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"ไฟล์ต้องเป็น {', '.join(ALLOWED_EXT)}")

    filename = f"product_{product_id}{suffix}"
    dest = IMAGES_DIR / filename

    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    image_url = f"/static/images/{filename}"
    update_product_image(product_id, image_url)
    return {"message": "อัปโหลดรูปสำเร็จ", "image_url": image_url}
