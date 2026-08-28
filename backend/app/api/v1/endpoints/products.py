from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_in: ProductCreate, db: AsyncSession = Depends(get_db)):
    query = select(Product).where(Product.barcode_value == product_in.barcode_value)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="کالایی با این بارکد قبلاً در سامانه ثبت شده است."
        )

    product = Product(**product_in.model_dump())
    db.add(product)
    await db.flush()
    await db.refresh(product)
    return product

@router.get("/", response_model=List[ProductResponse])
async def list_products(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    query = select(Product).offset(skip).limit(limit).order_by(Product.id.desc())
    result = await db.execute(query)
    return result.scalars().all()