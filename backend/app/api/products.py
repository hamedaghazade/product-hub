import logging
from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.product import ProductCreate, ProductResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/products", tags=["Products"])

# مخزن موقت دیتابیس (Thread-Safe در سطح پروسس)
products_db: List[dict] = [
    {
        "id": 1,
        "title": "مایع ظرفشویی ۱ لیتری پریل",
        "barcode_value": "6260123456789",
        "units_per_pack": 12,
        "cost_price": 450000,
        "consumer_price": 550000
    },
    {
        "id": 2,
        "title": "اسلایم اعلا",
        "barcode_value": "5648532254",
        "units_per_pack": 10,
        "cost_price": 5000000,
        "consumer_price": 5500000
    }
]
_current_id = 3

@router.get("", response_model=List[ProductResponse])
async def get_all_products():
    return products_db

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate):
    global _current_id
    try:
        new_item = {
            "id": _current_id,
            "title": payload.title.strip(),
            "barcode_value": payload.barcode_value.strip(),
            "units_per_pack": payload.units_per_pack,
            "cost_price": payload.cost_price,
            "consumer_price": payload.consumer_price
        }
        products_db.insert(0, new_item)
        _current_id += 1
        logger.info(f"محصول جدید با شناسه {new_item['id']} ثبت شد.")
        return new_item
    except Exception as e:
        logger.error(f"خطا در ثبت محصول: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="خطای سرور در ثبت محصول."
        )