from sqlalchemy import Column, Integer, String, BigInteger, Numeric, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    cost_price = Column(Numeric(15, 2), nullable=False)
    units_per_pack = Column(Integer, nullable=False, default=1)
    barcode_value = Column(String(32), unique=True, index=True, nullable=False)
    consumer_price = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())