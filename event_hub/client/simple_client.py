#!/usr/bin/env python3
"""
Упрощенный клиент для демонстрации Event Hub
Работает без gRPC зависимостей
"""
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class SimpleEventClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_event(self, user_id: str, event_type: str, amount: float) -> Dict[str, Any]:
        """Отправляет событие через REST API"""
        event_data = {
            "user_id": user_id,
            "event_type": event_type,
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            async with self.session.post(f"{self.base_url}/events", json=event_data) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Event sent successfully: {result['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to send event: {response.status} - {error_text}")
                    return {"error": error_text}
        except Exception as e:
            logger.error(f"Error sending event: {e}")
            return {"error": str(e)}
    
    async def get_events(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Получает последние события через GraphQL"""
        query = """
        query {
            lastEvents(limit: %d) {
                id
                userId
                eventType
                amount
                timestamp
            }
        }
        """ % limit
        
        try:
            async with self.session.post(f"{self.base_url}/graphql", json={"query": query}) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", {}).get("lastEvents", [])
                else:
                    logger.error(f"Failed to get events: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting events: {e}")
            return []
    
    async def get_metrics(self, minutes: int = 1) -> Dict[str, Any]:
        """Получает агрегированные метрики"""
        query = """
        query {
            aggregatedMetrics(minutes: %d) {
                totalAmount
                eventCount
                timeWindow
            }
        }
        """ % minutes
        
        try:
            async with self.session.post(f"{self.base_url}/graphql", json={"query": query}) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", {}).get("aggregatedMetrics", {})
                else:
                    logger.error(f"Failed to get metrics: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {}

async def main():
    """Демонстрация работы клиента"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    async with SimpleEventClient() as client:
        logger.info("🚀 Starting Event Hub client demo...")
        
        # Отправляем тестовые события
        events = [
            ("user1", "purchase", 150.75),
            ("user2", "return", 45.50),
            ("user3", "purchase", 89.99),
            ("user4", "refund", 25.00),
        ]
        
        logger.info("📤 Sending test events...")
        for user_id, event_type, amount in events:
            result = await client.send_event(user_id, event_type, amount)
            if "id" in result:
                print(f"✅ Sent: {event_type} - ${amount} (ID: {result['id']})")
            else:
                print(f"❌ Failed: {event_type} - ${amount}")
            await asyncio.sleep(0.5)
        
        # Получаем последние события
        logger.info("📥 Getting recent events...")
        events = await client.get_events(limit=5)
        print(f"📊 Found {len(events)} events:")
        for event in events:
            print(f"   • {event['eventType']} - ${event['amount']} by {event['userId']}")
        
        # Получаем метрики
        logger.info("📈 Getting aggregated metrics...")
        metrics = await client.get_metrics(minutes=1)
        if metrics:
            print(f"📊 Metrics: ${metrics['totalAmount']} total, {metrics['eventCount']} events")
        else:
            print("📊 No metrics available yet")
        
        logger.info("🎉 Demo completed!")

if __name__ == "__main__":
    asyncio.run(main()) 