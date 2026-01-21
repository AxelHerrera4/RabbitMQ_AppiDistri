# E-Commerce Platform - Event-Driven Microservices

Event-driven microservices architecture for an e-commerce platform using RabbitMQ, GraphQL, and PostgreSQL.

## 🏗️ Architecture Overview

This project implements an event-driven architecture for handling high-volume order processing:

```
┌─────────────────┐         ┌──────────────┐         ┌─────────────────┐
│  Order Service  │────────>│   RabbitMQ   │────────>│ Inventory Svc   │
│  (Parallel Dev) │         │   (Broker)   │         │  (This Repo)    │
└─────────────────┘         └──────────────┘         └─────────────────┘
        │                          │                          │
        │                          │                          │
        └──────────── Publishes OrderCreated ─────────────────┘
                               Events
                                  │
        ┌─────────────────────────┴──────────────────────────┐
        │                                                     │
        ▼                                                     ▼
   StockReserved                                      StockRejected
   (Order Confirmed)                                  (Order Cancelled)
```

## 📦 Services

### Inventory Service (ms-inventory/)

**Status**: ✅ Implemented

Event-driven microservice for managing product inventory:

- **GraphQL API**: Query and manage products
- **Event Consumer**: Processes `OrderCreated` events
- **Event Publisher**: Emits `StockReserved` or `StockRejected` events
- **Database**: PostgreSQL for inventory data
- **Message Queue**: RabbitMQ for async communication

[📖 Full Documentation](ms-inventory/README.md) | [🚀 Quick Start](ms-inventory/QUICKSTART.md)

### Order Service

**Status**: 🚧 In parallel development

Handles order creation and lifecycle management.

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- pip

### Quick Start - Inventory Service

```bash
# Navigate to service
cd ms-inventory

# Start infrastructure (PostgreSQL + RabbitMQ)
docker-compose up -d

# Install dependencies
pip install -r requirements.txt

# Run service
uvicorn main:app --reload --port 8000

# Seed sample data (optional)
python seed_data.py

# Test events (optional)
python test_events.py
```

**Access Points:**
- GraphQL API: http://localhost:8000/graphql
- Health Check: http://localhost:8000/health
- RabbitMQ UI: http://localhost:15672 (rabbit_user / rabbit_pass)

## 🔄 Event Flow

### 1. Order Creation
Order Service publishes `OrderCreated` event to `orders` exchange:
```json
{
  "event": "OrderCreated",
  "order_id": "ORD-12345",
  "items": [
    {"product_id": 1, "quantity": 2}
  ]
}
```

### 2. Inventory Processing
Inventory Service:
- Consumes event from `order.created.inventory` queue
- Validates stock availability
- Reserves or rejects stock

### 3. Response Events

**Success** - Publishes to `inventory` exchange:
```json
{
  "event": "StockReserved",
  "order_id": "ORD-12345",
  "items": [...]
}
```

**Failure** - Publishes to `inventory` exchange:
```json
{
  "event": "StockRejected",
  "order_id": "ORD-12345",
  "reason": "Insufficient stock"
}
```

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| API Framework | FastAPI |
| API Style | GraphQL (Strawberry) |
| Message Broker | RabbitMQ 3 |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy |
| Message Protocol | AMQP (pika) |
| Container | Docker & Docker Compose |

## 📁 Project Structure

```
RabbitMQ_AppiDistri/
├── README.md                    # This file
├── ms-inventory/                # Inventory microservice
│   ├── main.py                 # FastAPI app + GraphQL
│   ├── config.py               # Configuration
│   ├── database.py             # Database setup
│   ├── models.py               # SQLAlchemy models
│   ├── schema.py               # GraphQL schema
│   ├── service.py              # Business logic
│   ├── rabbitmq.py             # RabbitMQ publisher
│   ├── consumer.py             # Event consumer
│   ├── docker-compose.yml      # Infrastructure
│   ├── requirements.txt        # Dependencies
│   ├── seed_data.py           # Sample data script
│   ├── test_events.py         # Event testing script
│   └── README.md               # Service documentation
└── ms-orders/                   # Order service (parallel dev)
```

## 🎯 Key Features

✅ **Event-Driven Architecture**: Asynchronous, non-blocking communication  
✅ **Horizontal Scalability**: Multiple service instances supported  
✅ **Fault Tolerance**: Message acknowledgments and retries  
✅ **Stock Reservation System**: Prevents overselling  
✅ **GraphQL API**: Flexible querying and mutations  
✅ **Docker Compose**: Easy local development  
✅ **Modular Design**: Clear separation of concerns  

## 📊 Use Cases

### Black Friday / High Traffic Scenarios
- Order Service doesn't block waiting for inventory checks
- RabbitMQ buffers requests during traffic spikes
- Multiple inventory instances process orders in parallel
- Failed messages are retried automatically

### Service Independence
- Inventory Service can be down for maintenance
- Orders queue up and process when service returns
- No data loss due to persistent messages

### Scalability
- Add more Order Service instances → More orders/second
- Add more Inventory Service instances → Faster processing
- RabbitMQ distributes work across consumers

## 🧪 Testing

```bash
# Start services
cd ms-inventory
docker-compose up -d
uvicorn main:app --reload --port 8000

# In another terminal: Seed data
python seed_data.py

# Test GraphQL queries
# Visit: http://localhost:8000/graphql

# Simulate order events
python test_events.py

# Check logs for event processing
# Monitor RabbitMQ UI: http://localhost:15672
```

## 📚 Documentation

- [Inventory Service Documentation](ms-inventory/README.md)
- [Quick Start Guide](ms-inventory/QUICKSTART.md)
- [GraphQL Schema](ms-inventory/schema.py)
- [Event Flow](ms-inventory/README.md#event-flow)

## 🤝 Integration with Order Service

The Inventory Service is ready to integrate with the Order Service:

1. **Shared Configuration**: Both services must use same exchange/queue names
2. **Event Contract**: Order Service must publish `OrderCreated` events in expected format
3. **Response Handling**: Order Service should consume from `inventory` exchange
4. **Routing Keys**: 
   - Order Service publishes to: `order.created`
   - Inventory Service publishes to: `stock.reserved` or `stock.rejected`

## 🚀 Deployment

### Development
```bash
docker-compose up -d
uvicorn main:app --reload
```

### Production Considerations
- Use environment-specific `.env` files
- Enable SSL/TLS for RabbitMQ and PostgreSQL
- Implement authentication for GraphQL API
- Set up monitoring (Prometheus, Grafana)
- Configure log aggregation (ELK Stack)
- Use Kubernetes for orchestration
- Implement circuit breakers and rate limiting

## 📝 License

University Project - Distributed Applications Course  
Universidad, Séptimo Semestre

## 👥 Contributors

Developed as part of P3 - RabbitMQ distributed applications project.
