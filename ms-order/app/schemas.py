from pydantic import BaseModel, UUID4
from typing import List, Optional
from datetime import datetime
from uuid import UUID

# --- Esquemas de Entrada (Request) ---
class OrderItemBase(BaseModel):
    productId: UUID4
    quantity: int

class ShippingAddress(BaseModel):
    country: Optional[str] = "EC"
    city: str
    street: str
    postalCode: str

class OrderCreateRequest(BaseModel):
    customerId: UUID4
    items: List[OrderItemBase]
    shippingAddress: ShippingAddress
    paymentReference: str

# --- Esquemas de Salida (Response) ---
class OrderResponse(BaseModel):
    orderId: UUID4
    customerId: UUID4
    status: str
    reason: Optional[str] = None
    items: List[OrderItemBase]
    updatedAt: Optional[datetime] = None

    class Config:
        orm_mode = True

# --- Esquemas de Eventos RabbitMQ ---
class OrderCreatedEvent(BaseModel):
    eventType: str = "OrderCreated"
    orderId: UUID4
    correlationId: UUID4
    items: List[OrderItemBase]