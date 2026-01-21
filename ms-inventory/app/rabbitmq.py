import json
import pika
import threading
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import ProductStock, Base
from .schemas import OrderCreatedEvent

# Configuración RabbitMQ (Credenciales de tu docker-compose)
RABBIT_HOST = 'localhost'
RABBIT_USER = 'rabbit_user'
RABBIT_PASS = 'rabbit_pass'

def get_connection():
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    return pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials))

def publish_event(event_data: dict):
    """Publica eventos StockReserved o StockRejected"""
    connection = get_connection()
    channel = connection.channel()
    # Usamos un exchange tipo topic
    channel.exchange_declare(exchange='ecommerce_exchange', exchange_type='topic', durable=True)
    
    routing_key = 'inventory.response'
    channel.basic_publish(
        exchange='ecommerce_exchange',
        routing_key=routing_key,
        body=json.dumps(event_data)
    )
    print(f" [x] Enviado {event_data['eventType']} para Orden {event_data['orderId']}")
    connection.close()

def process_order_event(body):
    """Lógica de negocio: Verificar stock y reservar"""
    data = json.loads(body)
    event = OrderCreatedEvent(**data)
    
    db: Session = SessionLocal()
    try:
        # Verificar stock para TODOS los items
        can_fulfill = True
        reason = ""
        
        # Primero solo verificamos
        for item in event.items:
            product = db.query(ProductStock).filter(ProductStock.product_id == item.productId).first()
            if not product or product.available_stock < item.quantity:
                can_fulfill = False
                reason = f"Insufficient stock for product {item.productId}"
                break
        
        if can_fulfill:
            # Transacción: Reservar stock
            reserved_items = []
            for item in event.items:
                product = db.query(ProductStock).filter(ProductStock.product_id == item.productId).first()
                product.available_stock -= item.quantity
                product.reserved_stock += item.quantity
                reserved_items.append({"productId": item.productId, "quantity": item.quantity})
            
            db.commit()
            
            # Crear evento StockReserved [cite: 263]
            response_event = {
                "eventType": "StockReserved",
                "orderId": event.orderId,
                "correlationId": event.correlationId,
                "reservedItems": reserved_items,
                "reservedAt": str(datetime.now())
            }
        else:
            # Crear evento StockRejected [cite: 292]
            response_event = {
                "eventType": "StockRejected",
                "orderId": event.orderId,
                "correlationId": event.correlationId,
                "reason": reason,
                "rejectedAt": str(datetime.now())
            }

        publish_event(response_event)

    except Exception as e:
        print(f"Error procesando orden: {e}")
        db.rollback()
    finally:
        db.close()

def consume_messages():
    """Loop infinito escuchando RabbitMQ"""
    try:
        connection = get_connection()
        channel = connection.channel()
        channel.exchange_declare(exchange='ecommerce_exchange', exchange_type='topic', durable=True)
        
        # Cola para escuchar órdenes creadas
        queue_name = 'inventory_service_queue'
        channel.queue_declare(queue=queue_name, durable=True)
        # Binding: Escuchar eventos de creación de órdenes
        channel.queue_bind(exchange='ecommerce_exchange', queue=queue_name, routing_key='order.created')

        def callback(ch, method, properties, body):
            print(f" [x] Recibido: {body}")
            process_order_event(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue_name, on_message_callback=callback)

        print(' [*] Esperando mensajes en RabbitMQ. To exit press CTRL+C')
        channel.start_consuming()
    except Exception as e:
        print(f"Error en conexión RabbitMQ: {e}")

# Ejecutar consumidor en un hilo separado
def start_consumer_thread():
    t = threading.Thread(target=consume_messages)
    t.daemon = True
    t.start()