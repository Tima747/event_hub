import motor.motor_asyncio
import os
from datetime import datetime
from typing import Dict, Any

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client["event_hub"]
collection = db["events"]

async def save_event(event_dict: Dict[str, Any]):
    # Очистка и валидация
    if '_id' in event_dict:
        del event_dict['_id']
    
    if not isinstance(event_dict.get('timestamp'), datetime):
        try:
            ts = event_dict['timestamp']
            if isinstance(ts, str):
                if '.' in ts:
                    ts = ts.split('.')[0]
                event_dict['timestamp'] = datetime.fromisoformat(ts.replace('Z', ''))
        except (ValueError, TypeError):
            event_dict['timestamp'] = datetime.now()
    
    return await collection.insert_one(event_dict)

async def get_last_events(limit: int):
    cursor = collection.find().sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)