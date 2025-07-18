from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.db.redis import r
from app.db.mongo import save_event
from app.models.event import Event
import logging
from typing import Dict, Any

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/events")
async def receive_event(event: Event):
    try:
        event_dict = event.dict(by_alias=True)
        
        # Очистка данных
        event_dict = {k: v for k, v in event_dict.items() 
                     if v is not None and k != '_id'}
        
        # Валидация timestamp
        if isinstance(event_dict.get('timestamp'), str):
            ts = event_dict['timestamp']
            # Фикс формата (удаление лишних цифр)
            if '.' in ts:
                ts = ts.split('.')[0] + 'Z'
            elif len(ts.split(':')[-1]) > 6:
                ts = ts[:19] + 'Z'
            try:
                event_dict['timestamp'] = datetime.fromisoformat(ts.replace('Z', ''))
            except ValueError:
                event_dict['timestamp'] = datetime.now()

        # Сохранение в MongoDB
        try:
            result = await save_event(event_dict)
            if not result.inserted_id:
                raise Exception("MongoDB insert failed")
            
            event_id = str(result.inserted_id)
            logger.info(f"Event saved with ID: {event_id}")
            
            # Публикация в Redis (временно отключено для тестирования)
            # TODO: Исправить Redis Streams интеграцию
            logger.info("Redis publishing temporarily disabled for testing")
            
            return {"status": "success", "id": event_id}
            
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to save event")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))