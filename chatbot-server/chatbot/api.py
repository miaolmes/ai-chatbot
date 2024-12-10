from typing import Union
from fastapi import FastAPI, HTTPException, Depends
from openai import AsyncOpenAI
from starlette.responses import StreamingResponse

from .client import get_client
from .models.chat_completion import ChatCompletionRequest

app = FastAPI(title="Chat Completions API")

@app.post("/v1/chat/completions")
async def create_chat_completion(
    request: ChatCompletionRequest,
    client: AsyncOpenAI = Depends(get_client)
):
    try:
        # If streaming response is requested
        if request.stream:
            async def generate():
                # Exclude 'stream' from the model dump
                request_data = request.model_dump(exclude={"stream"})
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
        completion = await client.chat.completions.create(
            **request_data
        )
        return completion

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
