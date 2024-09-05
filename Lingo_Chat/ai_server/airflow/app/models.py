from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy import create_engine, BigInteger, Float, TIMESTAMP

from sqlalchemy.orm import relationship

from .database import Base


class ChatHistoryBackup(Base):
    __tablename__ = "chat_history_backup"
    
    chat_room_id = Column(BigInteger, primary_key=True, index=True)
    
    user_id = Column(String)
    chat_history = Column(String)
