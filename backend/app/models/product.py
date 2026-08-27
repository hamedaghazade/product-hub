from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    cost_price = Column(Float, nullable=False, default=0.0)
    units_per_pack = Column(Integer, nullable=False, default=1)
    barcode_value = Column(String(64), nullable=False, unique=True, index=True)
    consumer_price = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    @property
    def profit_margin_percent(self) -> float:
        if self.cost_price > 0:
            return round(((self.consumer_price - self.cost_price) / self.cost_price) * 100, 2)
        return 0.0