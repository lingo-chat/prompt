import sys
sys.path.append("./")
from . import models, schemas

from sqlalchemy.orm import Session

def backup_chat_history(db: Session, chat_history: schemas.chat_history_backup):
    chat_history = models.ChatHistoryBackup(
        chat_room_id=chat_history.chat_room_id,
        user_id=chat_history.user_id,
        chat_history=chat_history.chat_history
    )
    db.add(chat_history)
    db.commit()
    db.refresh(chat_history)
    
    return chat_history