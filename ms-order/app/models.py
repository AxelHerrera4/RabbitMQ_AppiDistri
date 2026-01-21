import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String, primary_key=True, index=True) # UUID
    customer_id = Column(String, index=True)
    status = Column(String, default="PENDING") # PENDING, CONFIRMED, CANCELLED
    reason = Column(String, nullable=True)     # Razón de rechazo si aplica
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con items
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.order_id"))
    product_id = Column(String)
    quantity = Column(Integer)

    order = relationship("Order", back_populates="items")