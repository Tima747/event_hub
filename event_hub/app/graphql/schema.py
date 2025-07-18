import strawberry
import json
from typing import List, AsyncGenerator
from datetime import datetime
import asyncio
from app.db.mongo import get_last_events
from app.db.redis import r
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class Event:
    id: str
    user_id: str = strawberry.field(name="userId")
    event_type: str = strawberry.field(name="eventType")
    amount: float
    timestamp: datetime

@strawberry.type
class AggregatedMetric:
    total_amount: float
    event_count: int
    time_window: str

@strawberry.type
class Query:
    @strawberry.field
    async def last_events(self, limit: int = 5) -> List[Event]:
        events = await get_last_events(limit)
        return [Event(
            id=str(e.get("_id", "")),
            user_id=e["user_id"],
            event_type=e["event_type"],
            amount=e["amount"],
            timestamp=e["timestamp"]
        ) for e in events]
    
    @strawberry.field
    async def aggregated_metrics(self, minutes: int = 1) -> AggregatedMetric:
        try:
            # Получаем агрегированные метрики из Redis
            metrics_data = await r.get("aggregated_metrics")
            if metrics_data:
                metrics = json.loads(metrics_data)
                total_amount = sum(m["total_amount"] for m in metrics.values())
                total_count = sum(m["count"] for m in metrics.values())
                
                return AggregatedMetric(
                    total_amount=total_amount,
                    event_count=total_count,
                    time_window=f"last_{minutes}_minutes"
                )
        except Exception as e:
            print(f"Error getting aggregated metrics: {e}")
        
        # Fallback если метрики недоступны
        return AggregatedMetric(
            total_amount=0.0,
            event_count=0,
            time_window=f"last_{minutes}_minutes"
        )

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def event_stream(self) -> AsyncGenerator[Event, None]:
        last_id = "0"
        while True:
            try:
                messages = await r.xread({"events": last_id}, count=1, block=1000)
                
                for stream, stream_messages in messages:
                    for message_id, fields in stream_messages:
                        last_id = message_id
                        
                        # Создаем Event объект из Redis данных
                        event = Event(
                            id=fields.get("event_id", ""),
                            user_id=fields.get("user_id", ""),
                            event_type=fields.get("event_type", ""),
                            amount=float(fields.get("amount", 0)),
                            timestamp=datetime.fromisoformat(fields.get("timestamp", ""))
                        )
                        yield event
                
                await asyncio.sleep(0.1)  # Небольшая пауза
                
            except Exception as e:
                print(f"Subscription error: {e}")
                await asyncio.sleep(1)

schema = strawberry.Schema(query=Query, subscription=Subscription)
graphql_app = GraphQLRouter(schema)