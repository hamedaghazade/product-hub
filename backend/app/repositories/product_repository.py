import logging
import math
from typing import Optional, Sequence, Tuple
from sqlalchemy import Select, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BarcodeAlreadyExistsError, ProductNotFoundError
from app.models.product import Product
from app.schemas.product import PaginatedResponse, ProductCreate, ProductFilterParams, ProductResponse, ProductUpdate

logger = logging.getLogger(__name__)


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, product_in: ProductCreate) -> Product:
        product = Product(
            title=product_in.title,
            cost_price=product_in.cost_price,
            consumer_price=product_in.consumer_price,
            units_per_pack=product_in.units_per_pack,
            barcode_value=product_in.barcode_value,
        )
        self.session.add(product)
        try:
            await self.session.commit()
            await self.session.refresh(product)
            return product
        except IntegrityError as exc:
            await self.session.rollback()
            if "ix_products_barcode_value" in str(exc.orig) or "products_barcode_value_key" in str(exc.orig):
                logger.warning("Duplicate barcode insertion attempt: %s", product_in.barcode_value)
                raise BarcodeAlreadyExistsError(barcode=product_in.barcode_value) from exc
            logger.error("Database integrity error on product creation: %s", exc)
            raise

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        stmt = select(Product).where(Product.id == product_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_barcode(self, barcode_value: str) -> Optional[Product]:
        stmt = select(Product).where(Product.barcode_value == barcode_value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    def _apply_filters(self, query: Select, filters: ProductFilterParams) -> Select:
        if filters.search:
            search_pattern = f"%{filters.search.strip()}%"
            query = query.where(
                or_(
                    Product.title.ilike(search_pattern),
                    Product.barcode_value.ilike(search_pattern),
                )
            )

        if filters.barcode:
            query = query.where(Product.barcode_value == filters.barcode.strip())

        if filters.min_cost_price is not None:
            query = query.where(Product.cost_price >= filters.min_cost_price)

        if filters.max_cost_price is not None:
            query = query.where(Product.cost_price <= filters.max_cost_price)

        if filters.min_consumer_price is not None:
            query = query.where(Product.consumer_price >= filters.min_consumer_price)

        if filters.max_consumer_price is not None:
            query = query.where(Product.consumer_price <= filters.max_consumer_price)

        return query

    async def get_paginated(
        self, filters: ProductFilterParams
    ) -> PaginatedResponse[ProductResponse]:
        base_query = select(Product)
        filtered_query = self._apply_filters(base_query, filters)

        # محاسبه تعداد کل رکوردها
        count_query = select(func.count()).select_from(filtered_query.subquery())
        total_count_result = await self.session.execute(count_query)
        total_count: int = total_count_result.scalar_one()

        # محاسبه صفحه‌بندی
        offset = (filters.page - 1) * filters.page_size
        paginated_query = (
            filtered_query.order_by(Product.created_at.desc())
            .offset(offset)
            .limit(filters.page_size)
        )

        result = await self.session.execute(paginated_query)
        products: Sequence[Product] = result.scalars().all()

        total_pages = math.ceil(total_count / filters.page_size) if total_count > 0 else 0

        return PaginatedResponse(
            items=[ProductResponse.model_validate(p) for p in products],
            total=total_count,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=total_pages,
        )

    async def update(self, product_id: int, product_in: ProductUpdate) -> Product:
        product = await self.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id=product_id)

        update_data = product_in.model_dump(exclude_unset=True)
        if not update_data:
            return product

        for field, value in update_data.items():
            setattr(product, field, value)

        try:
            await self.session.commit()
            await self.session.refresh(product)
            return product
        except IntegrityError as exc:
            await self.session.rollback()
            if "barcode_value" in update_data and (
                "ix_products_barcode_value" in str(exc.orig) or "products_barcode_value_key" in str(exc.orig)
            ):
                raise BarcodeAlreadyExistsError(barcode=str(update_data["barcode_value"])) from exc
            raise

    async def delete(self, product_id: int) -> bool:
        product = await self.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id=product_id)

        await self.session.delete(product)
        await self.session.commit()
        return True