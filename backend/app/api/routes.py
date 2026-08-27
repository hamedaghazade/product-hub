from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from app.services.barcode_service import BarcodeService, BarcodeConfig, BarcodeFormat

router = APIRouter()

@router.get("/barcode/generate")
async def get_barcode_image(
    title: str = Query(..., description="نام کالا (فارسی/انگلیسی)"),
    code: str = Query(..., description="کد عددی بارکد"),
    format_type: BarcodeFormat = Query(BarcodeFormat.EAN13, description="استاندارد بارکد"),
    font_size: int = Query(22, ge=10, le=50, description="اندازه فونت عنوان"),
    height: int = Query(120, ge=40, le=300, description="ارتفاع خطوط بارکد"),
    margin: int = Query(20, ge=5, le=80, description="حاشیه تصویر")
):
    try:
        config = BarcodeConfig(
            title=title,
            code_value=code,
            format_type=format_type,
            title_font_size=font_size,
            barcode_height_px=height,
            margin=margin
        )
        image_stream = BarcodeService.generate_barcode_image(config)
        return StreamingResponse(image_stream, media_type="image/png")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"خطا در ایجاد بارکد: {str(exc)}")