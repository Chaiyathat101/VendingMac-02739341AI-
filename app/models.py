from typing import Optional

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    low_stock_threshold: int = Field(default=5, ge=0)
    status: str = Field(default="active")
    image_url: Optional[str] = None
    category: str = Field(default="general")


class ProductUpdate(ProductCreate):
    pass


class SaleRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1)
    payment_method: str = Field(default="cash")
    amount_paid: float = Field(..., ge=0)


class AdminLoginRequest(BaseModel):
    username: str
    password: str
