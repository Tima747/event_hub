"""
Prometheus метрики для Event Hub
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from typing import Dict, Any
import time

# HTTP метрики
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# События
events_ingested_total = Counter(
    'events_ingested_total',
    'Total number of events ingested',
    ['source', 'type']
)

# Очередь
queue_lag = Gauge(
    'queue_lag',
    'Number of messages in queue',
    ['queue_name']
)

# MongoDB операции
mongo_ops_total = Counter(
    'mongo_ops_total',
    'Total number of MongoDB operations',
    ['operation', 'collection']
)

mongo_operation_duration = Histogram(
    'mongo_operation_duration_seconds',
    'MongoDB operation duration in seconds',
    ['operation', 'collection']
)

# gRPC метрики
grpc_requests_total = Counter(
    'grpc_requests_total',
    'Total number of gRPC requests',
    ['method', 'status']
)

grpc_request_duration = Histogram(
    'grpc_request_duration_seconds',
    'gRPC request duration in seconds',
    ['method']
)

# GraphQL метрики
graphql_requests_total = Counter(
    'graphql_requests_total',
    'Total number of GraphQL requests',
    ['operation', 'status']
)

graphql_request_duration = Histogram(
    'graphql_request_duration_seconds',
    'GraphQL request duration in seconds',
    ['operation']
)

# Системные метрики
active_connections = Gauge(
    'active_connections',
    'Number of active connections',
    ['type']
)

def record_http_request(method: str, endpoint: str, status: int, duration: float):
    """Записывает метрики HTTP запроса"""
    http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)

def record_event_ingested(source: str, event_type: str):
    """Записывает метрики ингестированного события"""
    events_ingested_total.labels(source=source, type=event_type).inc()

def update_queue_lag(queue_name: str, lag: int):
    """Обновляет метрики лага очереди"""
    queue_lag.labels(queue_name=queue_name).set(lag)

def record_mongo_operation(operation: str, collection: str, duration: float):
    """Записывает метрики операции MongoDB"""
    mongo_ops_total.labels(operation=operation, collection=collection).inc()
    mongo_operation_duration.labels(operation=operation, collection=collection).observe(duration)

def record_grpc_request(method: str, status: str, duration: float):
    """Записывает метрики gRPC запроса"""
    grpc_requests_total.labels(method=method, status=status).inc()
    grpc_request_duration.labels(method=method).observe(duration)

def record_graphql_request(operation: str, status: str, duration: float):
    """Записывает метрики GraphQL запроса"""
    graphql_requests_total.labels(operation=operation, status=status).inc()
    graphql_request_duration.labels(operation=operation).observe(duration)

def update_active_connections(conn_type: str, count: int):
    """Обновляет метрики активных соединений"""
    active_connections.labels(type=conn_type).set(count)

def get_metrics():
    """Возвращает метрики в формате Prometheus"""
    return generate_latest(), CONTENT_TYPE_LATEST 