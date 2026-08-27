from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
import io
from app.services.barcode_service import BarcodeService, BarcodeConfig, BarcodeFormat

health_router = APIRouter(prefix="/api/v1", tags=["System Health"])

@health_router.get("/health", status_code=status.HTTP_200_OK)
async def check_system_health():
    # ۱. تست موتور بارکد و رندر در رم
    barcode_status = "ok"
    try:
        test_config = BarcodeConfig(
            title="تست سیستم",
            code_value="626123456789",
            format_type=BarcodeFormat.EAN13
        )
        stream = BarcodeService.generate_barcode_image(test_config)
        if not isinstance(stream, io.BytesIO) or stream.getbuffer().nbytes == 0:
            barcode_status = "empty_stream"
    except Exception as e:
        barcode_status = f"error: {str(e)}"

    is_healthy = barcode_status == "ok"
    
    return JSONResponse(
        status_code=status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "healthy" if is_healthy else "unhealthy",
            "components": {
                "barcode_engine": barcode_status,
                "api_runtime": "python-fastapi"
            }
        }
    )