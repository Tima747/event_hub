import asyncio
import grpc
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import logging
from typing import AsyncIterator

from app.db.mongo import save_event
from app.db.redis import r
from app.models.event import Event

# Импортируем сгенерированные protobuf классы
try:
    from protos import event_pb2, event_pb2_grpc
except ImportError:
    # Fallback для случая, когда protobuf не сгенерированы
    class EventRequest:
        def __init__(self):
            self.user_id = ""
            self.event_type = ""
            self.amount = 0.0
            self.timestamp = ""
    
    class EventResponse:
        def __init__(self):
            self.event_id = ""
            self.status = ""
            self.message = ""
    
    class StreamRequest:
        def __init__(self):
            self.limit = 0

logger = logging.getLogger(__name__)

class EventServicer:
    async def SendEvent(self, request, context):
        try:
            # Создаем Event объект из gRPC запроса
            event_dict = {
                "user_id": request.user_id,
                "event_type": request.event_type,
                "amount": request.amount,
                "timestamp": datetime.fromisoformat(request.timestamp.replace('Z', '')) if request.timestamp else datetime.now()
            }
            
            # Сохраняем в MongoDB
            result = await save_event(event_dict)
            event_id = str(result.inserted_id)
            
            # Публикуем в Redis
            redis_data = {
                "event_id": event_id,
                "user_id": event_dict["user_id"],
                "event_type": event_dict["event_type"],
                "amount": str(event_dict["amount"]),
                "timestamp": event_dict["timestamp"].isoformat()
            }
            await r.xadd("events", redis_data)
            
            logger.info(f"gRPC Event saved with ID: {event_id}")
            
            return EventResponse(
                event_id=event_id,
                status="success",
                message="Event saved successfully"
            )
            
        except Exception as e:
            logger.error(f"gRPC error: {str(e)}")
            return EventResponse(
                event_id="",
                status="error",
                message=str(e)
            )
    
    async def StreamEvents(self, request, context) -> AsyncIterator[EventResponse]:
        try:
            # Читаем события из Redis Stream
            last_id = "0"
            while True:
                messages = await r.xread({"events": last_id}, count=request.limit, block=1000)
                
                for stream, stream_messages in messages:
                    for message_id, fields in stream_messages:
                        last_id = message_id
                        yield EventResponse(
                            event_id=fields.get("event_id", ""),
                            status="stream",
                            message=f"Event: {fields.get('event_type', '')} - {fields.get('amount', '')}"
                        )
                
                await asyncio.sleep(1)  # Пауза между чтениями
                
        except Exception as e:
            logger.error(f"gRPC stream error: {str(e)}")
            yield EventResponse(
                event_id="",
                status="error",
                message=str(e)
            )

async def serve():
    server = grpc.aio.server(ThreadPoolExecutor(max_workers=10))
    
    # Регистрируем сервис
    try:
        from protos import event_pb2_grpc
        event_pb2_grpc.add_EventServiceServicer_to_server(EventServicer(), server)
    except ImportError:
        # Fallback если protobuf не сгенерированы
        pass
    
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting gRPC server on {listen_addr}")
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve()) 