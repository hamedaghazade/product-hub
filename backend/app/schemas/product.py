from datetime import datetime
from decimal import Decimal
from typing import Generic, Optional, Sequence, TypeVar
from pydantic import BaseModel, ConfigDict, Field, field_validator

T = TypeVar("T")


class ProductBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255, description="نام محصول")
    cost_price: Decimal = Field(..., ge=0, decimal_places=2, description="قیمت خرید")
    consumer_price: Decimal = Field(..., ge=0, decimal_places=2, description="قیمت مصرف‌کننده")
    units_per_pack: int = Field(default=1, gt=0, description="تعداد در بسته")
    barcode_value: str = Field(..., min_length=3, max_length=64, description="مقدار بارکد")

    @field_validator("barcode_value")
    @classmethod
    def validate_barcode(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("مقدار بارکد نمی‌تواند خالی باشد.")
        return cleaned

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("نام کالا الزامی است.")
        return cleaned


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    cost_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    consumer_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    units_per_pack: Optional[int] = Field(None, gt=0)
    barcode_value: Optional[str] = Field(None, min_length=3, max_length=64)


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductFilterParams(BaseModel):
    search: Optional[str] = Field(None, description="جستجو در عنوان و بارکد")
    min_cost_price: Optional[Decimal] = Field(None, ge=0)
    max_cost_price: Optional[Decimal] = Field(None, ge=0)
    min_consumer_price: Optional[Decimal] = Field(None, ge=0)
    max_consumer_price: Optional[Decimal] = Field(None, ge=0)
    barcode: Optional[str] = Field(None)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    page_size: int
    total_pages: int