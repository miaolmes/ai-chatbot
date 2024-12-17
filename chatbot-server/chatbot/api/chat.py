from typing import List, Optional, Union
from uuid import UUID

from fastapi import HTTPException, Depends, APIRouter, Request
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from chatbot.config import get_settings
from fastapi.security import OAuth2PasswordBearer

from chatbot.db.database import DbSession
from chatbot.model.openai import get_client
from chatbot.db.crud import (
    get_chat_by_id,
    delete_chat_by_id,
    get_chat_history,
    create_chat,
    create_chat_message,
    get_chat_messages
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/v1/chat",
    tags=["chat"],
)


class Chat(BaseModel):
    id: UUID = Field(..., description="The unique identifier of the chat.")
    title: str = Field(..., description="The title of the chat.")

    class Config:
        from_attributes = True


class Message(BaseModel):
    id: Optional[UUID] = None
    role: str = Field(..., description="The role of the message sender (e.g., 'user', 'assistant', or 'system').")
    content: str = Field(..., description="The content of the message.")

    class Config:
        from_attributes = True


class ChatCompletionRequest(BaseModel):
    model: str = Field(..., description="The model to use for generating completions (e.g., 'gpt-3.5-turbo').")
    messages: List[Message] = Field(
        ..., description="A list of messages describing the conversation history.")
    max_tokens: Optional[int] = Field(
        None, description="The maximum number of tokens to generate in the response.")
    temperature: Optional[float] = Field(
        1.0, ge=0, le=2,
        description="Sampling temperature. Higher values make output more random; lower values make it more deterministic."
    )
    top_p: Optional[float] = Field(
        1.0, ge=0, le=1,
        description="Nucleus sampling probability. The model considers results of tokens with top_p probability mass."
    )
    stream: Optional[bool] = Field(
        False, description="Whether to return a stream of data for the response. Defaults to False."
    )
    stop: Optional[Union[str, List[str]]] = Field(
        None, description="Optional stop sequences where the model will stop generating further tokens."
    )
    presence_penalty: Optional[float] = Field(
        0.0, ge=-2, le=2, description="Penalty for new tokens based on whether they appear in the text so far."
    )
    frequency_penalty: Optional[float] = Field(
        0.0, ge=-2, le=2, description="Penalty for new tokens based on their frequency in the text so far."
    )
    user: Optional[str] = Field(
        None, description="Unique identifier for the end-user. This helps OpenAI monitor and detect abuse."
    )


async def retrieve_relevant_documents(query: str, k: int = 3) -> str:
    settings = get_settings()
    embeddings = OpenAIEmbeddings(
        openai_api_base=settings.openai_api_base,
        openai_api_key=settings.openai_api_key
    )
    vectorstore = Chroma(
        collection_name='documents',
        persist_directory=settings.chatbot_vector_store,
        embedding_function=embeddings
    )
    docs = vectorstore.similarity_search(query, k=k)
    return "\n\n".join([doc.page_content for doc in docs])


@router.post("/completions", operation_id="createChatCompletion")
async def create_chat_completion(
        request: ChatCompletionRequest,
        client: AsyncOpenAI = Depends(get_client),
        token: str = Depends(oauth2_scheme)
):
    try:
        # Get the user's last message
        user_message = next((msg for msg in reversed(request.messages) if msg.role == "user"), None)
        if user_message:
            # Retrieve relevant documents
            context = await retrieve_relevant_documents(user_message.content)
            
            # Add system message with context
            system_message = Message(
                role="system",
                content=f"Below is some relevant context that may help answer the user's question:\n\n{context}"
            )
            request.messages.insert(0, system_message)

        # If streaming response is requested
        if request.stream:
            async def generate():
                # Exclude 'stream' from the model dump
                request_data = request.model_dump(exclude={"stream"})
                print(request_data)
                stream = await client.chat.completions.create(
                    **request_data,
                    stream=True
                )
                async for chunk in stream:
                    yield f"data: {chunk.model_dump_json()}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                generate(),
                media_type="text/event-stream"
            )

        # Non-streaming response
        request_data = request.model_dump(exclude={"stream"})
        print(request_data)
        completion = await client.chat.completions.create(
            **request_data
        )
        return completion

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{chat_id}", status_code=200, operation_id="getChat")
async def get_chat(request: Request, chat_id: str, db: DbSession, token: str = Depends(oauth2_scheme)) -> Chat:
    chat = get_chat_by_id(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return Chat.model_validate(chat)


@router.delete("/{chat_id}", status_code=204, operation_id="deleteChat")
async def delete_chat(request: Request, chat_id: str, db: DbSession, token: str = Depends(oauth2_scheme)):
    deleted = delete_chat_by_id(db, chat_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Chat not found")


@router.get("/", status_code=200, operation_id="getChats")
async def get_chats(request: Request, db: DbSession, token: str = Depends(oauth2_scheme)) -> List[Chat]:
    chats = get_chat_history(db)
    return [Chat.model_validate(chat) for chat in chats]


@router.post("/{chat_id}/messages", status_code=201, operation_id="createMessage")
async def create_message(request: Request, chat_id: str, message: Message, db: DbSession, token: str = Depends(oauth2_scheme)):
    # create chat if not exists
    chat = get_chat_by_id(db, chat_id)
    print(chat)
    if not chat:
        create_chat(session=db, chat_id=chat_id, title=message.content)

    db_message = create_chat_message(
        db,
        chat_id,
        message.role,
        message.content
    )
    if not db_message:
        raise HTTPException(status_code=404, detail="Chat not found")
    return Message.model_validate(db_message)


@router.get("/{chat_id}/messages", status_code=200, operation_id="getMessages")
async def get_messages(chat_id: str, db: DbSession, token: str = Depends(oauth2_scheme)) -> List[Message]:
    messages = get_chat_messages(db, chat_id)
    return [Message.model_validate(message) for message in messages]
