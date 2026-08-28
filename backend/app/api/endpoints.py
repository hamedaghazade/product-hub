from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel, Field
from typing import List
import io
from app.services.excel_service import ExcelExportService
from app.services.pdf_service import PDFExportService

router = APIRouter(prefix="/products", tags=["Products"])

class ProductCreateDTO(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    cost_price: float = Field(..., gt=0)
    units_per_pack: int = Field(..., gt=0)
    barcode_value: str = Field(..., min_length=8, max_length=32)
    consumer_price: float = Field(..., gt=0)

@router.post("/export/excel")
async def export_excel_endpoint(products: List[ProductCreateDTO]):
    try:
        products_dict = [p.model_dump() for p in products]
        stream: io.BytesIO = ExcelExportService.create_products_sheet(products_dict)
        
        return Response(
            content=stream.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=products.xlsx"}
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/export/pdf")
async def export_pdf_endpoint(products: List[ProductCreateDTO]):
    try:
        products_dict = [p.model_dump() for p in products]
        stream: io.BytesIO = PDFExportService.generate_products_catalog(products_dict)
        
        return Response(
            content=stream.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=catalog.pdf"}
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))