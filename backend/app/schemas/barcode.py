from pydantic import BaseModel, Field, ConfigDict

class BarcodeConfig(BaseModel):
    font_path: str = Field(
        default="",
        description="مسیر فایل فونت TTF فارسی (در صورت خالی بودن فونت پیش‌فرض لود می‌شود)"
    )
    title_font_size: int = Field(default=22, ge=10, le=60, description="سایز فونت نام کالا (px)")
    code_font_size: int = Field(default=20, ge=10, le=50, description="سایز فونت ارقام بارکد (px)")
    barcode_height_mm: float = Field(default=18.0, ge=8.0, le=60.0, description="ارتفاع میله‌های بارکد به میلی‌متر")
    module_width_mm: float = Field(default=0.35, ge=0.15, le=1.0, description="ضخامت هر میله بارکد")
    padding_x: int = Field(default=20, ge=5, le=100, description="فاصله افقی حاشیه (px)")
    padding_y: int = Field(default=15, ge=5, le=100, description="فاصله عمودی حاشیه (px)")
    bg_color: str = Field(default="#FFFFFF", description="رنگ پس‌زمینه")
    text_color: str = Field(default="#000000", description="رنگ متن و میله‌ها")

    model_config = ConfigDict(from_attributes=True)