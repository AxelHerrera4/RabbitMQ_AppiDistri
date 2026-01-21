from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from .database import Base

class ProductStock(Base):
    __tablename__ = "products_stock"

    product_id = Column(String, primary_key=True, index=True) # UUID como String
    available_stock = Column(Integer, default=0)
    reserved_stock = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())