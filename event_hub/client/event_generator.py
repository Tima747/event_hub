import asyncio
import aiohttp
import random
import logging
from datetime import datetime
from typing import List, Tuple

logger = logging.getLogger(__name__)

class EventGenerator:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_event(self, user_id: str, event_type: str, amount: float) -> dict:
        """Отправляет событие через REST API"""
        if not self.session:
            return {"error": "Session not initialized. Use async with EventGenerator() as generator:"}
            
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
    
    async def generate_random_events(self, count: int = 10) -> List[dict]:
        """Генерирует случайные события"""
        event_types = ["purchase", "return", "refund", "exchange"]
        user_ids = [f"user_{i}" for i in range(1, 11)]
        
        results = []
        for i in range(count):
            user_id = random.choice(user_ids)
            event_type = random.choice(event_types)
            amount = round(random.uniform(10.0, 500.0), 2)
            
            result = await self.send_event(user_id, event_type, amount)
            results.append(result)
            
            # Небольшая пауза между событиями
            await asyncio.sleep(random.uniform(0.5, 2.0))
        
        return results
    
    async def generate_purchase_events(self, count: int = 5) -> List[dict]:
        """Генерирует события покупок"""
        results = []
        for i in range(count):
            user_id = f"customer_{i+1}"
            amount = round(random.uniform(50.0, 300.0), 2)
            
            result = await self.send_event(user_id, "purchase", amount)
            results.append(result)
            await asyncio.sleep(1)
        
        return results
    
    async def generate_return_events(self, count: int = 3) -> List[dict]:
        """Генерирует события возвратов"""
        results = []
        for i in range(count):
            user_id = f"customer_{i+1}"
            amount = round(random.uniform(20.0, 150.0), 2)
            
            result = await self.send_event(user_id, "return", amount)
            results.append(result)
            await asyncio.sleep(1)
        
        return results

async def main():
    """Основная функция для тестирования генератора"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    async with EventGenerator() as generator:
        logger.info("Starting event generation...")
        
        # Генерируем случайные события
        logger.info("Generating random events...")
        random_results = await generator.generate_random_events(5)
        
        # Генерируем покупки
        logger.info("Generating purchase events...")
        purchase_results = await generator.generate_purchase_events(3)
        
        # Генерируем возвраты
        logger.info("Generating return events...")
        return_results = await generator.generate_return_events(2)
        
        # Выводим статистику
        total_events = len(random_results) + len(purchase_results) + len(return_results)
        successful_events = sum(1 for r in random_results + purchase_results + return_results if "id" in r)
        
        logger.info(f"Generation completed: {successful_events}/{total_events} events sent successfully")

if __name__ == "__main__":
    asyncio.run(main()) 