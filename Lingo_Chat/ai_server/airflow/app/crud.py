import sys
sys.path.append("./")
from . import models, schemas

from sqlalchemy.orm import Session

def backup_chat_history(db: Session, chat_history: schemas.chat_history_backup):
    """
        전달된 채팅 히스토리를 db 에 저장합니다.
    """
    # 이미 해당 채팅방이 존재한다면 덧붙이기 - 추후 개선
    chat_history = models.ChatHistoryBackup(
        chat_room_id=chat_history.chat_room_id,
        user_id=chat_history.user_id,
        chat_history=chat_history.chat_history
    )
    
        
    db.add(chat_history)
    db.commit()
    db.refresh(chat_history)
    
    return chat_history


def reload_chat_history(db: Session, chat_room_id: int):
    """
        chat_room_id 에 해당하는 채팅 히스토리를 db 에서 조회합니다.
    """
    return db.query(models.ChatHistoryBackup).filter(models.ChatHistoryBackup.chat_room_id == chat_room_id).all()

def delete_chat_history(db: Session, chat_room_id: int):
    """
        chat_room_id 에 해당하는 채팅 히스토리를 db 에서 삭제합니다.
    """
    db.query(models.ChatHistoryBackup).filter(models.ChatHistoryBackup.chat_room_id == chat_room_id).delete()
    db.commit()
    return True