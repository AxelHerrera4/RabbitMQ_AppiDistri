import uuid
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, database, schemas, rabbitmq

# Crear tablas
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Order Service")

@app.on_event("startup")
def startup_event():
    rabbitmq.start_consumer_thread()

# --- Endpoint 1: Crear Pedido (POST) ---
@app.post("/api/v1/orders", status_code=status.HTTP_201_CREATED)
def create_order(order_req: schemas.OrderCreateRequest, db: Session = Depends(database.get_db)):
    # 1. Generar IDs
    new_order_id = str(uuid.uuid4())
    correlation_id = str(uuid.uuid4())
    
    # 2. Guardar en DB con estado PENDING
    db_order = models.Order(
        order_id=new_order_id,
        customer_id=str(order_req.customerId),
        status="PENDING"
    )
    db.add(db_order)
    db.commit() # Commit inicial para tener el ID
    
    # Guardar items
    for item in order_req.items:
        db_item = models.OrderItem(
            order_id=new_order_id,
            product_id=str(item.productId),
            quantity=item.quantity
        )
        db.add(db_item)
    db.commit()

    # 3. Publicar evento OrderCreated a RabbitMQ
    event_data = {
        "eventType": "OrderCreated",
        "orderId": new_order_id,
        "correlationId": correlation_id,
        "items": [{"productId": str(item.productId), "quantity": item.quantity} for item in order_req.items]
    }
    rabbitmq.publish_order_created(event_data)

    # 4. Retornar respuesta inmediata (PDF pag 4)
    return {
        "orderId": new_order_id,
        "status": "PENDING",
        "message": "Order received. Inventory check in progress."
    }

# --- Endpoint 2: Consultar Pedido (GET) ---
@app.get("/api/v1/orders/{orderId}", response_model=schemas.OrderResponse)
def get_order(orderId: str, db: Session = Depends(database.get_db)):
    order = db.query(models.Order).filter(models.Order.order_id == orderId).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Construir respuesta con conversión correcta
    return {
        "orderId": uuid.UUID(order.order_id),
        "customerId": uuid.UUID(order.customer_id),
        "status": order.status,
        "reason": order.reason,
        "items": [
            {
                "productId": uuid.UUID(item.product_id),
                "quantity": item.quantity
            }
            for item in order.items
        ],
        "updatedAt": order.updated_at
    }