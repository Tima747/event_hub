from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Event(BaseModel):
    user_id: str
    event_type: str
    amount: float
    timestamp: datetime
    id: Optional[str] = Field(None, alias="_id")

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }