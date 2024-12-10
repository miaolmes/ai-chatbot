from typing import Annotated, Generator

from fastapi import Depends
from sqlmodel import create_engine, Session, SQLModel

from chatbot.config import get_settings

settings = get_settings()

sqlite_file_name = "chatbot.db"
sqlite_url = f"sqlite:///{settings.chatbot_db_store}/{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    # IMPORTANT: Import all models here, so that they are registered with metadata
    from chatbot.db.models import Chat, Message
    SQLModel.metadata.create_all(engine)


DbSession = Annotated[Session, Depends(get_session)]
