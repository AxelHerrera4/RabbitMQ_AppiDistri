from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Estructura de items dentro de la orden
class OrderItem(BaseModel):
    productId: str
    quantity: int

# Evento entrante: OrderCreated [cite: 248]
class OrderCreatedEvent(BaseModel):
    eventType: str
    orderId: str
    correlationId: str
    items: List[OrderItem]

# Respuesta para la API REST [cite: 135]
class ProductStockResponse(BaseModel):
    productId: str
    availableStock: int
    reservedStock: int
    updatedAt: datetime

    class Config:
        orm_mode = True