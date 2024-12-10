import os.path

from fastapi import FastAPI, APIRouter

from chatbot.api import chat, files
from chatbot.config import get_settings

app = FastAPI(title="AI Chatbot")

api_router = APIRouter()
api_router.include_router(chat.router)
api_router.include_router(files.router)
app.include_router(api_router)

settings = get_settings()
if not os.path.exists(settings.chatbot_data_dir):
    os.makedirs(settings.chatbot_doc_store)


@app.get("/")
async def root() -> dict:
    return {"message": "Hello World"}
