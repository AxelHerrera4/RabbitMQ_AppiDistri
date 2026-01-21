# RabbitMQ_AppiDistri

Proyecto de aplicaciones distribuidas utilizando microservicios y RabbitMQ.

## Descripción

Este proyecto contiene dos microservicios principales:

- **ms-inventory**: Gestión de inventario.
- **ms-order**: Gestión de órdenes.

La comunicación entre servicios se realiza mediante RabbitMQ.

## Requisitos

- Docker y Docker Compose
- Python 3.8+
- RabbitMQ

## Instalación rápida con Docker

Levanta todos los servicios y dependencias con Docker Compose:

```bash
docker compose up -d --build
```

## Instalación manual

### ms-inventory

```bash
cd ms-inventory
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8081
```

### ms-order

```bash
cd ms-order
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

## Rutas

RabbitMQ (UI): http://localhost:15672
ms-order: http://localhost:8080
ms-inventory: http://localhost:8081
