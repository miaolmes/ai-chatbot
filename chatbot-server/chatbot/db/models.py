from typing import Optional, List
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class Chat(SQLModel, table=True):
    __tablename__ = 'chat'

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    title: str

    messages: List["Message"] = Relationship(back_populates="chat")


class Message(SQLModel, table=True):
    __tablename__ = 'message'

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    chatId: UUID = Field(foreign_key="chat.id", nullable=False)
    role: str
    content: str  # SQLite不直接支持JSON，建议使用str存储JSON字符串
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    chat: Chat = Relationship(back_populates="messages")
