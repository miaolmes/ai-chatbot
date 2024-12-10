from fastapi import FastAPI, APIRouter

from chatbot.api import chat

app = FastAPI(title="AI Chatbot")

api_router = APIRouter()
api_router.include_router(chat.router)
app.include_router(api_router)


@app.get("/")
async def root() -> dict:
    return {"message": "Hello World"}
