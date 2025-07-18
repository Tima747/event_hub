import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from collections import defaultdict

from app.db.redis import r
from app.db.mongo import collection

logger = logging.getLogger(__name__)

class MetricsConsumer:
    def __init__(self):
        self.metrics = defaultdict(lambda: {"total_amount": 0.0, "count": 0})
        self.last_aggregation = datetime.now()
    
    async def process_event(self, event_data: Dict[str, Any]):
        """Обрабатывает одно событие и обновляет метрики"""
        try:
            event_type = event_data.get("event_type", "unknown")
            amount = float(event_data.get("amount", 0))
            
            # Обновляем метрики
            self.metrics[event_type]["total_amount"] += amount
            self.metrics[event_type]["count"] += 1
            
            logger.info(f"Processed event: {event_type} - {amount}")
            
        except Exception as e:
            logger.error(f"Error processing event: {e}")
    
    async def aggregate_metrics(self):
        """Агрегирует метрики за последнюю минуту"""
        try:
            cutoff_time = datetime.now() - timedelta(minutes=1)
            
            # Получаем события из MongoDB за последнюю минуту
            pipeline = [
                {"$match": {"timestamp": {"$gte": cutoff_time}}},
                {"$group": {
                    "_id": "$event_type",
                    "total_amount": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }}
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            # Формируем агрегированные метрики
            aggregated = {}
            for result in results:
                event_type = result["_id"]
                aggregated[event_type] = {
                    "total_amount": result["total_amount"],
                    "count": result["count"],
                    "timestamp": datetime.now().isoformat()
                }
            
            # Сохраняем в Redis для GraphQL
            await r.set("aggregated_metrics", json.dumps(aggregated))
            
            logger.info(f"Aggregated metrics: {aggregated}")
            
        except Exception as e:
            logger.error(f"Error aggregating metrics: {e}")
    
    async def run(self):
        """Основной цикл consumer'а"""
        last_id = "0"
        
        while True:
            try:
                # Читаем события из Redis Stream
                messages = await r.xread({"events": last_id}, count=10, block=1000)
                
                for stream, stream_messages in messages:
                    for message_id, fields in stream_messages:
                        last_id = message_id
                        await self.process_event(fields)
                
                # Агрегируем метрики каждую минуту
                if datetime.now() - self.last_aggregation >= timedelta(minutes=1):
                    await self.aggregate_metrics()
                    self.last_aggregation = datetime.now()
                
            except Exception as e:
                logger.error(f"Consumer error: {e}")
                await asyncio.sleep(1)

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    consumer = MetricsConsumer()
    logger.info("Starting metrics consumer...")
    await consumer.run()

if __name__ == "__main__":
    asyncio.run(main()) 