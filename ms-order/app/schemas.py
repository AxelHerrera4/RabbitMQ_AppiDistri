from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Esquemas de Entrada (Request) ---
class OrderItemBase(BaseModel):
    productId: str
    quantity: int

class ShippingAddress(BaseModel):
    country: Optional[str] = "EC"
    city: str
    street: str
    postalCode: str

class OrderCreateRequest(BaseModel):
    customerId: str
    items: List[OrderItemBase]
    shippingAddress: ShippingAddress
    paymentReference: str

# --- Esquemas de Salida (Response) ---
class OrderResponse(BaseModel):
    orderId: str
    customerId: str
    status: str
    reason: Optional[str] = None
    items: List[OrderItemBase]
    updatedAt: Optional[datetime] = None

    class Config:
        orm_mode = True

# --- Esquemas de Eventos RabbitMQ ---
class OrderCreatedEvent(BaseModel):
    eventType: str = "OrderCreated"
    orderId: str
    correlationId: str
    items: List[OrderItemBase]