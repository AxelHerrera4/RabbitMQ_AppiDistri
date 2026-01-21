from pydantic import BaseModel, UUID4
from typing import List, Optional
from datetime import datetime
from uuid import UUID

# Estructura de items dentro de la orden
class OrderItem(BaseModel):
    productId: UUID4
    quantity: int

# Request para crear producto
class ProductCreateRequest(BaseModel):
    name: str
    availableStock: int

# Evento entrante: OrderCreated [cite: 248]
class OrderCreatedEvent(BaseModel):
    eventType: str
    orderId: UUID4
    correlationId: UUID4
    items: List[OrderItem]

# Respuesta para la API REST [cite: 135]
class ProductStockResponse(BaseModel):
    productId: UUID4
    name: str
    availableStock: int
    reservedStock: int
    updatedAt: datetime

    class Config:
        orm_mode = True