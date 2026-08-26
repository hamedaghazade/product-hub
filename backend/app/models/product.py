from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ProductDB(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    cost_price = Column(Float, nullable=False)
    units_per_pack = Column(Integer, nullable=False, default=1)
    barcode_value = Column(String(64), unique=True, index=True, nullable=False)
    consumer_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProductCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    cost_price: float = Field(..., ge=0)
    units_per_pack: int = Field(..., gt=0)
    barcode_value: str = Field(..., min_length=4, max_length=32)
    consumer_price: float = Field(..., ge=0)

    @field_validator("barcode_value")
    @classmethod
    def validate_barcode(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned.isdigit():
            raise ValueError("کد بارکد باید صرفاً شامل ارقام عددی باشد.")
        return cleaned

class ProductOut(ProductCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True\n