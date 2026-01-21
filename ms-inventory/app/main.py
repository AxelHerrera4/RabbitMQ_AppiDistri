import uuid
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, database, schemas, rabbitmq

# Crear tablas en BD al iniciar
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Inventory Service")

# Iniciar el consumidor de RabbitMQ al arrancar la app
@app.on_event("startup")
def startup_event():
    rabbitmq.start_consumer_thread()

# Endpoint 1: Consultar stock (Requerimiento PDF [cite: 131])
@app.get("/api/v1/products/{productId}/stock", response_model=schemas.ProductStockResponse)
def get_product_stock(productId: str, db: Session = Depends(database.get_db)):
    product = db.query(models.ProductStock).filter(models.ProductStock.product_id == productId).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "productId": uuid.UUID(product.product_id),
        "name": product.name,
        "availableStock": product.available_stock,
        "reservedStock": product.reserved_stock,
        "updatedAt": product.updated_at
    }

# Endpoint Extra: Crear productos (Semilla para pruebas)
@app.post("/api/v1/products", response_model=schemas.ProductStockResponse)
def create_product(product_req: schemas.ProductCreateRequest, db: Session = Depends(database.get_db)):
    # Generar UUID automáticamente
    new_product_id = str(uuid.uuid4())
    db_product = models.ProductStock(
        product_id=new_product_id, 
        name=product_req.name, 
        available_stock=product_req.availableStock,
        reserved_stock=0
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return {
        "productId": uuid.UUID(db_product.product_id),
        "name": db_product.name,
        "availableStock": db_product.available_stock,
        "reservedStock": db_product.reserved_stock,
        "updatedAt": db_product.updated_at
    }