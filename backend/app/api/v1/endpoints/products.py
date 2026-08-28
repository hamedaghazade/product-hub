from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.exceptions import BarcodeAlreadyExistsError, ProductNotFoundError
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import (
    PaginatedResponse,
    ProductCreate,
    ProductFilterParams,
    ProductResponse,
    ProductUpdate,
)

router = APIRouter()


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ثبت کالای جدید",
    description="ایجاد محصول جدید با بررسی یکتا بودن بارکد و اعتبارسنجی قیمت‌ها",
)
async def create_product(
    payload: ProductCreate,
    session: AsyncSession = Depends(get_async_session),
):
    repo = ProductRepository(session)
    try:
        return await repo.create(payload)
    except BarcodeAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=exc.message,
        )


@router.get(
    "/",
    response_model=PaginatedResponse[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="دریافت لیست کالاها با فیلتر و صفحه‌بندی",
)
async def list_products(
    search: Optional[str] = Query(None, description="جستجو در عنوان یا بارکد"),
    min_cost_price: Optional[Decimal] = Query(None, ge=0),
    max_cost_price: Optional[Decimal] = Query(None, ge=0),
    min_consumer_price: Optional[Decimal] = Query(None, ge=0),
    max_consumer_price: Optional[Decimal] = Query(None, ge=0),
    barcode: Optional[str] = Query(None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session),
):
    filters = ProductFilterParams(
        search=search,
        min_cost_price=min_cost_price,
        max_cost_price=max_cost_price,
        min_consumer_price=min_consumer_price,
        max_consumer_price=max_consumer_price,
        barcode=barcode,
        page=page,
        page_size=page_size,
    )
    repo = ProductRepository(session)
    return await repo.get_paginated(filters)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="دریافت مشخصات یک محصول با شناسه",
)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    repo = ProductRepository(session)
    product = await repo.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"محصولی با شناسه {product_id} یافت نشد.",
        )
    return product


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="ویرایش مشخصات محصول",
)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    repo = ProductRepository(session)
    try:
        return await repo.update(product_id, payload)
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        )
    except BarcodeAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=exc.message,
        )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="حذف محصول",
)
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    repo = ProductRepository(session)
    try:
        await repo.delete(product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        )


@router.get(
    "/{product_id}/barcode.png",
    responses={200: {"content": {"image/png": {}}}},
    summary="دریافت تصویر بارکد کالا",
)
async def get_product_barcode(
    product_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    repo = ProductRepository(session)
    product = await repo.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="محصول مورد نظر یافت نشد.",
        )

    from app.services.barcode_service import BarcodeGenerationError, BarcodeService
    try:
        image_bytes = BarcodeService.generate_barcode_image(
            barcode_value=product.barcode_value,
            title=product.title,
        )
        return Response(content=image_bytes, media_type="image/png")
    except BarcodeGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


@router.get(
    "/export/excel",
    summary="دریافت خروجی اکسل محصولات همراه با بارکدهای Embed شده",
)
async def export_products_excel(session: AsyncSession = Depends(get_async_session)):
    stmt = select(Product).order_by(Product.created_at.desc())
    result = await session.execute(stmt)
    products = result.scalars().all()

    from app.services.excel_service import ExcelExportService
    excel_bytes = ExcelExportService.generate_products_workbook(products)
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=products_catalog.xlsx"},
    )


@router.get(
    "/export/pdf",
    summary="دریافت خروجی کاتالوگ PDF محصولات با پشتیبانی RTL",
)
async def export_products_pdf(session: AsyncSession = Depends(get_async_session)):
    stmt = select(Product).order_by(Product.created_at.desc())
    result = await session.execute(stmt)
    products = result.scalars().all()

    from app.services.pdf_service import PdfExportService
    pdf_bytes = PdfExportService.generate_catalog_pdf(products)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=products_catalog.pdf"},
    )