from typing import List, Optional
import uuid

from sqlmodel import select, Session

from chatbot.db.models import Chat, Message


def create_chat(session: Session, chat_id: str, title: Optional[str] = None) -> Chat:
    chat = Chat(id=uuid.UUID(chat_id), title=title)
    session.add(chat)
    session.commit()
    session.refresh(chat)
    return chat


def get_chat_by_id(session: Session, chat_id: str) -> Optional[Chat]:
    try:
        statement = select(Chat).where(Chat.id == uuid.UUID(chat_id))
        result = session.execute(statement).first()
        return result[0] if result else None
    except ValueError:
        return None


def get_chat_history(session: Session) -> List[Chat]:
    statement = select(Chat)
    results = session.execute(statement).all()
    return [result[0] for result in results]


def delete_chat_by_id(session: Session, chat_id: str) -> None:
    chat = get_chat_by_id(session, chat_id)
    if chat:
        session.delete(chat)
        session.commit()


def create_chat_message(
        session: Session,
        chat_id: str,
        role: str,
        content: str,
) -> Message:
    try:
        message = Message(chatId=uuid.UUID(chat_id), role=role, content=content)
        session.add(message)
        session.commit()
        session.refresh(message)
        return message
    except ValueError:
        raise ValueError("Invalid chat ID")


def get_chat_messages(session: Session, chat_id: str) -> List[Message]:
    try:
        statement = select(Message).where(Message.chatId == uuid.UUID(chat_id)).order_by(Message.createdAt)
        results = session.execute(statement).all()
        return [result[0] for result in results]
    except ValueError:
        return []
