import uuid

from db.pg_connection import Base
from schemas.enums import ProcessingStatus
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Chat(Base):
    __tablename__ = "chats"

    # id = Column(Integer, primary_key=True, index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=func.now())
    url = Column(String, nullable=False)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.not_processed)
    messages = relationship("Message", back_populates="chat")


class Message(Base):
    __tablename__ = "messages"

    # id = Column(Integer, primary_key=True, index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id"), nullable=False)
    message = Column(String)
    created_at = Column(DateTime, default=func.now())
    chat = relationship("Chat", back_populates="messages")
