from pydantic import BaseModel, Field, field_validator
import re

def calculate_ean13_checksum(digits12: str) -> str:
    """محاسبه رقم کنترل برای ۱۲ رقم اول EAN-13"""
    total = 0
    for idx, char in enumerate(digits12):
        num = int(char)
        total += num if idx % 2 == 0 else num * 3
    checksum = (10 - (total % 10)) % 10
    return str(checksum)

class ProductCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200, description="نام محصول به فارسی یا انگلیسی")
    cost_price: float = Field(..., gt=0, description="قیمت خرید")
    consumer_price: float = Field(..., gt=0, description="قیمت مصرف‌کننده")
    units_per_pack: int = Field(1, gt=0, description="تعداد در بسته")
    barcode_value: str = Field(..., description="کد بارکد (EAN-13 یا Code128)")

    @field_validator("barcode_value")
    @classmethod
    def validate_barcode(cls, v: str) -> str:
        clean_value = re.sub(r"\s+", "", v)
        if clean_value.isdigit() and len(clean_value) in (12, 13):
            # اعتبارسنجی استاندارد EAN-13
            if len(clean_value) == 12:
                clean_value += calculate_ean13_checksum(clean_value)
            else:
                expected_checksum = calculate_ean13_checksum(clean_value[:12])
                if clean_value[12] != expected_checksum:
                    raise ValueError(f"رقم کنترلی بارکد EAN-13 اشتباه است. مقدار صحیح باید {expected_checksum} باشد.")
        elif not (3 <= len(clean_value) <= 50):
            raise ValueError("طول کد بارکد استاندارد نیست.")
        return clean_value

    @field_validator("consumer_price")
    @classmethod
    def validate_prices(cls, v: float, info) -> float:
        if "cost_price" in info.data and v < info.data["cost_price"]:
            # اخطار منطقی برای قیمت‌گذاری
            pass
        return v