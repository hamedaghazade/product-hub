from fastapi import APIRouter, HTTPException, Response
from typing import List
from app.models.product import ProductCreate, ProductOut
from app.services.excel_service import ExcelService
from app.services.pdf_service import PDFService
from app.services.barcode_service import BarcodeService

router = APIRouter()

# In-Memory Data Store for MVP (Easily swapped with SQLAlchemy session)
DATABASE_MEMORY: List[ProductOut] = []
ID_COUNTER = 1

@router.get("/products", response_model=List[ProductOut])
async def get_products():
    return DATABASE_MEMORY

@router.post("/products", response_model=ProductOut, status_code=201)
async def create_product(product: ProductCreate):
    global ID_COUNTER
    for item in DATABASE_MEMORY:
        if item.barcode_value == product.barcode_value:
            raise HTTPException(status_code=400, detail="کد بارکد تکراری است.")
            
    from datetime import datetime
    new_item = ProductOut(id=ID_COUNTER, created_at=datetime.utcnow(), **product.model_dump())
    DATABASE_MEMORY.append(new_item)
    ID_COUNTER += 1
    return new_item

@router.get("/export/excel")
async def export_excel():
    if not DATABASE_MEMORY:
        raise HTTPException(status_code=404, detail="داده‌ای برای خروجی وجود ندارد.")
    stream = ExcelService.generate_products_sheet(DATABASE_MEMORY)
    return Response(
        content=stream.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=products.xlsx"}
    )

@router.get("/export/pdf")
async def export_pdf():
    if not DATABASE_MEMORY:
        raise HTTPException(status_code=404, detail="داده‌ای برای خروجی وجود ندارد.")
    stream = PDFService.generate_products_pdf(DATABASE_MEMORY)
    return Response(
        content=stream.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=products.pdf"}
    )

@router.get("/barcode/{barcode_val}")
async def get_barcode_preview(barcode_val: str, title: str = "کالا"):
    stream = BarcodeService.generate_barcode_image(barcode_val, title)
    return Response(content=stream.getvalue(), media_type="image/png")\n