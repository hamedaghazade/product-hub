from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.product import Product
from app.services.excel_service import ExcelExportService
from app.services.pdf_service import PDFExportService

router = APIRouter(prefix="/export", tags=["Export"])

@router.get("/excel")
async def export_excel(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).order_by(Product.id.desc()))
    products = result.scalars().all()
    products_data = [
        {
            "title": p.title,
            "cost_price": float(p.cost_price),
            "units_per_pack": p.units_per_pack,
            "barcode_value": p.barcode_value,
            "consumer_price": float(p.consumer_price)
        }
        for p in products
    ]
    stream = ExcelExportService.create_products_sheet(products_data)
    return Response(
        content=stream.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=products.xlsx"}
    )

@router.get("/pdf")
async def export_pdf(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).order_by(Product.id.desc()))
    products = result.scalars().all()
    products_data = [
        {
            "title": p.title,
            "cost_price": float(p.cost_price),
            "units_per_pack": p.units_per_pack,
            "barcode_value": p.barcode_value,
            "consumer_price": float(p.consumer_price)
        }
        for p in products
    ]
    stream = PDFExportService.generate_products_catalog(products_data)
    return Response(
        content=stream.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=catalog.pdf"}
    )