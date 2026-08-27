from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.product import Product
from app.services.excel_service import ExcelExportService
from app.services.pdf_service import PDFExportService
from app.services.barcode_service import BarcodeService, BarcodeConfig, BarcodeFormat

router = APIRouter(prefix="/export", tags=["Exports & Barcodes"])

@router.get("/excel")
async def export_excel(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).order_by(Product.id))
    products = result.scalars().all()
    if not products:
        raise HTTPException(status_code=400, detail="هیچ کالایی برای صدور اکسل یافت نشد.")
    
    stream = ExcelExportService.generate_products_workbook(products)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=products_catalog.xlsx"}
    )

@router.get("/pdf")
async def export_pdf(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).order_by(Product.id))
    products = result.scalars().all()
    if not products:
        raise HTTPException(status_code=400, detail="هیچ کالایی برای صدور PDF یافت نشد.")

    stream = PDFExportService.generate_products_pdf(products)
    return StreamingResponse(
        stream,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=products_catalog.pdf"}
    )

@router.get("/barcode")
async def get_barcode_stream(
    title: str = Query(...),
    code: str = Query(...),
    format_type: BarcodeFormat = Query(BarcodeFormat.EAN13),
    height: int = Query(120),
    margin: int = Query(20)
):
    cfg = BarcodeConfig(
        title=title,
        code_value=code,
        format_type=format_type,
        barcode_height_px=height,
        margin=margin
    )
    stream = BarcodeService.generate_barcode_image(cfg)
    return StreamingResponse(stream, media_type="image/png")