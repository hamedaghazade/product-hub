from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List

from app.core.database import get_db
from app.core.security import verify_telegram_init_data
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductSummaryStats

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/summary", response_model=ProductSummaryStats)
async def get_summary_stats(
    db: AsyncSession = Depends(get_db),
    auth: dict = Depends(verify_telegram_init_data)
):
    total_count = await db.scalar(select(func.count(Product.id))) or 0
    total_val = await db.scalar(select(func.sum(Product.cost_price * Product.units_per_pack))) or 0.0
    
    # محاسبه میانگین سود
    result = await db.execute(select(Product))
    products = result.scalars().all()
    avg_margin = sum(p.profit_margin_percent for p in products) / len(products) if products else 0.0

    return {
        "total_products": total_count,
        "total_inventory_value": total_val,
        "avg_profit_margin": round(avg_margin, 2)
    }

@router.get("", response_model=List[ProductResponse])
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(Product).order_by(desc(Product.id))
    if search:
        query = query.where(Product.title.ilike(f"%{search}%") | Product.barcode_value.ilike(f"%{search}%"))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate, 
    db: AsyncSession = Depends(get_db),
    auth: dict = Depends(verify_telegram_init_data)
):
    # بررسی یکتایی بارکد
    existing = await db.scalar(select(Product).where(Product.barcode_value == product_in.barcode_value))
    if existing:
        raise HTTPException(status_code=400, detail="کالایی با این عدد بارکد از قبل ثبت شده است.")

    new_prod = Product(**product_in.model_dump())
    db.add(new_prod)
    await db.commit()
    await db.refresh(new_prod)
    return new_prod

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    prod = await db.get(Product, product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="محصول یافت نشد.")
    await db.delete(prod)
    await db.commit()