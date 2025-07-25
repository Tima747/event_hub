"""
OpenTelemetry трейсинг для Event Hub
"""

import os
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer
from opentelemetry.instrumentation.pymongo import PyMongoInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from contextlib import contextmanager
from typing import Dict, Any, Optional

# Настройка трейсера
def setup_tracing():
    """Настраивает OpenTelemetry трейсинг"""
    # Создаем провайдер трейсов
    resource = Resource.create({"service.name": "event-hub"})
    provider = TracerProvider(resource=resource)
    
    # Настраиваем экспорт в Jaeger
    jaeger_exporter = JaegerExporter(
        agent_host_name=os.getenv("JAEGER_HOST", "localhost"),
        agent_port=int(os.getenv("JAEGER_PORT", "6831")),
    )
    
    # Добавляем процессор для батчинга
    processor = BatchSpanProcessor(jaeger_exporter)
    provider.add_span_processor(processor)
    
    # Устанавливаем провайдер как глобальный
    trace.set_tracer_provider(provider)
    
    return provider

def get_tracer(name: str = "event-hub"):
    """Получает трейсер"""
    return trace.get_tracer(name)

@contextmanager
def trace_operation(operation_name: str, attributes: Optional[Dict[str, Any]] = None):
    """Контекстный менеджер для трейсинга операций"""
    tracer = get_tracer()
    with tracer.start_as_current_span(operation_name, attributes=attributes or {}) as span:
        try:
            yield span
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise

def trace_persist_event(event_id: str, event_type: str, source: str):
    """Трейсит операцию сохранения события"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(
                "persist_event",
                attributes={
                    "event.id": event_id,
                    "event.type": event_type,
                    "event.source": source,
                    "operation": "persist"
                }
            ) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    raise
        return wrapper
    return decorator

def trace_http_request(method: str, path: str, status_code: int, duration: float):
    """Трейсит HTTP запрос"""
    tracer = get_tracer()
    with tracer.start_as_current_span(
        "http_request",
        attributes={
            "http.method": method,
            "http.path": path,
            "http.status_code": status_code,
            "http.duration": duration
        }
    ) as span:
        if status_code >= 400:
            span.set_status(trace.Status(trace.StatusCode.ERROR))
        else:
            span.set_status(trace.Status(trace.StatusCode.OK))

def trace_grpc_request(method: str, status_code: int, duration: float):
    """Трейсит gRPC запрос"""
    tracer = get_tracer()
    with tracer.start_as_current_span(
        "grpc_request",
        attributes={
            "grpc.method": method,
            "grpc.status_code": status_code,
            "grpc.duration": duration
        }
    ) as span:
        if status_code != 0:  # 0 = OK в gRPC
            span.set_status(trace.Status(trace.StatusCode.ERROR))
        else:
            span.set_status(trace.Status(trace.StatusCode.OK))

def trace_mongo_operation(operation: str, collection: str, duration: float):
    """Трейсит операцию MongoDB"""
    tracer = get_tracer()
    with tracer.start_as_current_span(
        "mongo_operation",
        attributes={
            "db.operation": operation,
            "db.collection": collection,
            "db.duration": duration
        }
    ) as span:
        span.set_status(trace.Status(trace.StatusCode.OK))

def trace_queue_operation(operation: str, queue_name: str, message_count: int = None):
    """Трейсит операцию с очередью"""
    tracer = get_tracer()
    attributes = {
        "queue.operation": operation,
        "queue.name": queue_name
    }
    if message_count is not None:
        attributes["queue.message_count"] = message_count
    
    with tracer.start_as_current_span("queue_operation", attributes=attributes) as span:
        span.set_status(trace.Status(trace.StatusCode.OK))

# Инструментирование FastAPI
def instrument_fastapi(app):
    """Инструментирует FastAPI приложение"""
    FastAPIInstrumentor.instrument_app(app)

# Инструментирование gRPC
def instrument_grpc():
    """Инструментирует gRPC сервер"""
    GrpcInstrumentorServer().instrument()

# Инструментирование MongoDB
def instrument_mongo():
    """Инструментирует MongoDB клиент"""
    PyMongoInstrumentor().instrument()

# Инструментирование Redis
def instrument_redis():
    """Инструментирует Redis клиент"""
    RedisInstrumentor().instrument() 