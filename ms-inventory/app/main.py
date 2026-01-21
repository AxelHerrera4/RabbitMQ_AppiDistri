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
        "productId": product.product_id,
        "availableStock": product.available_stock,
        "reservedStock": product.reserved_stock,
        "updatedAt": product.updated_at
    }

# Endpoint Extra: Crear productos (Semilla para pruebas)
@app.post("/api/v1/products")
def create_product(productId: str, stock: int, db: Session = Depends(database.get_db)):
    db_product = models.ProductStock(product_id=productId, available_stock=stock)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product