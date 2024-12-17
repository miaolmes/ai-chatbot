import os.path
from typing import Annotated

from fastapi import FastAPI, APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from chatbot.api import chat, files, user
from chatbot.config import get_settings
from chatbot.db.database import create_db_and_tables
from chatbot.indexing.indexer import Indexer

app = FastAPI(title="AI Chatbot")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

api_router = APIRouter()
api_router.include_router(chat.router)
api_router.include_router(files.router)
api_router.include_router(user.router) 
app.include_router(api_router)

indexer = None

@app.on_event("startup")
def on_startup():
    settings = get_settings()
    os.makedirs(settings.chatbot_doc_store, exist_ok=True)
    os.makedirs(settings.chatbot_vector_store, exist_ok=True)
    os.makedirs(settings.chatbot_db_store, exist_ok=True)
    create_db_and_tables()
    
    # Start the indexer
    global indexer
    indexer = Indexer()
    indexer.start()

@app.on_event("shutdown")
def on_shutdown():
    if indexer:
        indexer.stop()

@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    return {"token": token}

@app.get("/")
async def root() -> dict:
    return {"message": "Hello World"}
