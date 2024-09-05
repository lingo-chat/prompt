from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class chat_history_backup(BaseModel):
    chat_room_id: int
    user_id: str
    chat_history: str