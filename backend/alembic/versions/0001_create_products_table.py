"""create products table

Revision ID: 0001_create_products
Revises: 
Create Date: 2026-08-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_create_products"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False, comment="نام کالا با پشتیبانی کامل از UTF-8 و فونت فارسی"),
        sa.Column("cost_price", sa.Numeric(precision=14, scale=2), nullable=False, comment="قیمت خرید یا قیمت پایه"),
        sa.Column("consumer_price", sa.Numeric(precision=14, scale=2), nullable=False, comment="قیمت مصرف کننده نهایی"),
        sa.Column("units_per_pack", sa.Integer(), nullable=False, comment="تعداد موجود در هر بسته"),
        sa.Column("barcode_value", sa.String(length=64), nullable=False, comment="کد بارکد استاندارد EAN-13 یا Code-128"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("units_per_pack > 0", name="chk_products_units_per_pack_positive"),
        sa.CheckConstraint("cost_price >= 0", name="chk_products_cost_price_non_negative"),
        sa.CheckConstraint("consumer_price >= 0", name="chk_products_consumer_price_non_negative"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)
    op.create_index(op.f("ix_products_title"), "products", ["title"], unique=False)
    op.create_index(op.f("ix_products_barcode_value"), "products", ["barcode_value"], unique=True)
    op.create_index(op.f("ix_products_created_at"), "products", ["created_at"], unique=False)
    op.create_index("ix_products_title_barcode", "products", ["title", "barcode_value"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_products_title_barcode", table_name="products")
    op.drop_index(op.f("ix_products_created_at"), table_name="products")
    op.drop_index(op.f("ix_products_barcode_value"), table_name="products")
    op.drop_index(op.f("ix_products_title"), table_name="products")
    op.drop_index(op.f("ix_products_id"), table_name="products")
    op.drop_table("products")