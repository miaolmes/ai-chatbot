import os
import time
from urllib.parse import unquote
import uuid

from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from pydantic import BaseModel

from chatbot.config import get_settings

router = APIRouter(
    prefix="/v1/files",
    tags=["files"],
)


class FileResponse(BaseModel):
    id: str
    object: str
    bytes: int
    created_at: int
    filename: str
    purpose: str


@router.post("/upload", response_model=FileResponse, operation_id="uploadFile")
async def upload_file(
        chat_id: str = Form(..., description="The chatId the uploaded file."),
        file: UploadFile = File(..., description="The file to be uploaded.")
):
    try:
        # Simulate saving the file and getting its size
        content = await file.read()
        file_size = len(content)
        # Simulate creation timestamp
        created_at = int(time.time())

        # Save the file to a storage service
        settings = get_settings()
        os.makedirs(f"{settings.chatbot_doc_store}/{chat_id}")
        with open(f"{settings.chatbot_doc_store}/{chat_id}/{file.filename}", "wb") as f:
            f.write(content)

        # Return the response
        return FileResponse(
            id=f"{chat_id}/{file.filename}",
            object="file",
            bytes=file_size,
            created_at=created_at,
            filename=file.filename,
            purpose="chat"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", operation_id="getFile")
async def get_file(id: str):
    try:
        settings = get_settings()
        decoded_id = unquote(id)
        file_path = f"{settings.chatbot_doc_store}/{decoded_id}"

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        file_size = os.path.getsize(file_path)

        from fastapi.responses import FileResponse
        return FileResponse(
            path=file_path,
            media_type="application/octet-stream",
            filename=os.path.basename(file_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
