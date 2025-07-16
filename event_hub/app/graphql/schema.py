import strawberry
from typing import List
from datetime import datetime
from app.db.mongo import get_last_events
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class Event:
    id: str
    user_id: str = strawberry.field(name="userId")
    event_type: str = strawberry.field(name="eventType")
    amount: float
    timestamp: datetime

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

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)