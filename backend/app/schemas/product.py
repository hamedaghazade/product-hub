from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class ProductBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255, description="نام محصول به فارسی یا انگلیسی")
    cost_price: float = Field(..., ge=0, description="قیمت خرید کالا")
    units_per_pack: int = Field(1, gt=0, description="تعداد در هر بسته")
    barcode_value: str = Field(..., min_length=6, max_length=50, description="کد عددی بارکد")
    consumer_price: float = Field(..., ge=0, description="قیمت مصرف‌کننده")

    @field_validator("barcode_value")
    @classmethod
    def validate_barcode(cls, val: str) -> str:
        cleaned = val.strip()
        if not re.match(r"^[A-Za-z0-9\-]+$", cleaned):
            raise ValueError("کد بارکد فقط شامل حروف، ارقام و خط تیره مجاز است.")
        return cleaned

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    cost_price: Optional[float] = Field(None, ge=0)
    units_per_pack: Optional[int] = Field(None, gt=0)
    barcode_value: Optional[str] = Field(None, min_length=6, max_length=50)
    consumer_price: Optional[float] = Field(None, ge=0)

class ProductResponse(ProductBase):
    id: int
    profit_margin_percent: float
    created_at: datetime

    class Config:
        from_attributes = True

class ProductSummaryStats(BaseModel):
    total_products: int
    total_inventory_value: float
    avg_profit_margin: float