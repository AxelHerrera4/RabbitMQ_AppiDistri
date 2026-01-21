import json
import pika
import threading
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Order

RABBIT_HOST = 'localhost'
RABBIT_USER = 'rabbit_user'
RABBIT_PASS = 'rabbit_pass'

def get_connection():
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    return pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials))

# --- Productor: Publicar OrderCreated ---
def publish_order_created(order_data: dict):
    try:
        connection = get_connection()
        channel = connection.channel()
        channel.exchange_declare(exchange='ecommerce_exchange', exchange_type='topic', durable=True)
        
        routing_key = 'order.created'
        channel.basic_publish(
            exchange='ecommerce_exchange',
            routing_key=routing_key,
            body=json.dumps(order_data)
        )
        print(f" [x] Evento publicado: OrderCreated para {order_data['orderId']}")
        connection.close()
    except Exception as e:
        print(f"Error publicando mensaje: {e}")

# --- Consumidor: Escuchar respuestas del Inventario ---
def process_inventory_response(body):
    data = json.loads(body)
    event_type = data.get("eventType")
    order_id = data.get("orderId")
    
    print(f" [x] Recibido evento {event_type} para orden {order_id}")
    
    db: Session = SessionLocal()
    try:
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            print("Orden no encontrada")
            return

        if event_type == "StockReserved":
            order.status = "CONFIRMED"
            print(f"Orden {order_id} CONFIRMADA")
        
        elif event_type == "StockRejected":
            order.status = "CANCELLED"
            order.reason = data.get("reason", "Unknown reason")
            print(f"Orden {order_id} CANCELADA. Razón: {order.reason}")
            
        db.commit()
    except Exception as e:
        print(f"Error actualizando orden: {e}")
        db.rollback()
    finally:
        db.close()

def consume_responses():
    try:
        connection = get_connection()
        channel = connection.channel()
        channel.exchange_declare(exchange='ecommerce_exchange', exchange_type='topic', durable=True)
        
        # Cola exclusiva para Order Service
        queue_name = 'order_service_response_queue'
        channel.queue_declare(queue=queue_name, durable=True)
        
        # Escuchar todo lo que venga de inventory.response
        channel.queue_bind(exchange='ecommerce_exchange', queue=queue_name, routing_key='inventory.response')

        def callback(ch, method, properties, body):
            process_inventory_response(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue_name, on_message_callback=callback)
        print(' [*] Order Service escuchando respuestas...')
        channel.start_consuming()
    except Exception as e:
        print(f"Error conexión RabbitMQ: {e}")

def start_consumer_thread():
    t = threading.Thread(target=consume_responses)
    t.daemon = True
    t.start()