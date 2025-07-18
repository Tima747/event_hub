import asyncio
import grpc
import logging
from datetime import datetime
from typing import AsyncGenerator

# Fallback классы для случая, когда protobuf не сгенерированы
class EventRequest:
    def __init__(self, user_id="", event_type="", amount=0.0, timestamp=""):
        self.user_id = user_id
        self.event_type = event_type
        self.amount = amount
        self.timestamp = timestamp

class EventResponse:
    def __init__(self, event_id="", status="", message=""):
        self.event_id = event_id
        self.status = status
        self.message = message

class StreamRequest:
    def __init__(self, limit=0):
        self.limit = limit

# Заглушка для gRPC stub
class MockStub:
    async def SendEvent(self, request):
        return EventResponse(
            event_id="mock_id_123",
            status="success",
            message="Event sent successfully (mock)"
        )
    
    async def StreamEvents(self, request):
        for i in range(request.limit):
            yield EventResponse(
                event_id=f"stream_id_{i}",
                status="stream",
                message=f"Mock event {i}"
            )
            await asyncio.sleep(0.1)

logger = logging.getLogger(__name__)

class EventClient:
    def __init__(self, host: str = "localhost", port: int = 50051):
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None
    
    async def connect(self):
        """Устанавливает соединение с gRPC сервером"""
        try:
            # Используем mock stub для демонстрации
            self.stub = MockStub()
            logger.info(f"Using mock gRPC client (server at {self.host}:{self.port} not available)")
        except Exception as e:
            logger.error(f"Failed to connect to gRPC server: {e}")
            raise
    
    async def send_event(self, user_id: str, event_type: str, amount: float) -> str:
        """Отправляет событие через gRPC"""
        if not self.stub:
            raise Exception("Stub not initialized. Call connect() first.")
            
        try:
            request = EventRequest(
                user_id=user_id,
                event_type=event_type,
                amount=amount,
                timestamp=datetime.now().isoformat()
            )
            
            response = await self.stub.SendEvent(request)
            logger.info(f"Event sent: {response.status} - {response.message}")
            return response.event_id
            
        except Exception as e:
            logger.error(f"Failed to send event: {e}")
            raise
    
    async def stream_events(self, limit: int = 5) -> AsyncGenerator[str, None]:
        """Получает поток событий через gRPC"""
        if not self.stub:
            raise Exception("Stub not initialized. Call connect() first.")
            
        try:
            request = StreamRequest(limit=limit)
            async for response in self.stub.StreamEvents(request):
                yield f"{response.status}: {response.message}"
                
        except Exception as e:
            logger.error(f"Failed to stream events: {e}")
            raise
    
    async def close(self):
        """Закрывает соединение"""
        # Mock client не требует закрытия соединения
        pass

async def main():
    """Пример использования gRPC клиента"""
    logging.basicConfig(level=logging.INFO)
    
    client = EventClient()
    
    try:
        await client.connect()
        
        # Отправляем несколько тестовых событий
        events = [
            ("user1", "purchase", 100.50),
            ("user2", "return", 25.00),
            ("user3", "purchase", 75.25),
        ]
        
        for user_id, event_type, amount in events:
            event_id = await client.send_event(user_id, event_type, amount)
            print(f"Sent event: {event_id}")
            await asyncio.sleep(1)
        
        # Получаем поток событий
        print("Streaming events...")
        async for event in client.stream_events(limit=3):
            print(f"Received: {event}")
            await asyncio.sleep(0.5)
            
    except Exception as e:
        logger.error(f"Client error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main()) 