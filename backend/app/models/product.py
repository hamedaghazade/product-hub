from decimal import Decimal
from sqlalchemy import BigInteger, CheckConstraint, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="نام کالا با پشتیبانی کامل از UTF-8 و فونت فارسی",
    )
    cost_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=14, scale=2),
        nullable=False,
        comment="قیمت خرید یا قیمت پایه",
    )
    consumer_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=14, scale=2),
        nullable=False,
        comment="قیمت مصرف کننده نهایی",
    )
    units_per_pack: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="تعداد موجود در هر بسته",
    )
    barcode_value: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="کد بارکد استاندارد EAN-13 یا Code-128",
    )

    __table_args__ = (
        CheckConstraint("units_per_pack > 0", name="chk_products_units_per_pack_positive"),
        CheckConstraint("cost_price >= 0", name="chk_products_cost_price_non_negative"),
        CheckConstraint("consumer_price >= 0", name="chk_products_consumer_price_non_negative"),
        Index("ix_products_title_barcode", "title", "barcode_value"),
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, title='{self.title}', barcode='{self.barcode_value}')>"