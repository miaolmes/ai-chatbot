import os
import time
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


@router.post("/upload", response_model=FileResponse)
async def upload_file(
        purpose: str = Form(..., description="The purpose of the uploaded file."),
        file: UploadFile = File(..., description="The file to be uploaded.")
):
    try:
        # Generate a unique ID for the file
        file_id = f"file-{uuid.uuid4()}"
        # Simulate saving the file and getting its size
        content = await file.read()
        file_size = len(content)
        # Simulate creation timestamp
        created_at = int(time.time())

        # Save the file to a storage service
        settings = get_settings()
        os.makedirs(f"{settings.chatbot_doc_store}/{file_id}")
        with open(f"{settings.chatbot_doc_store}/{file_id}/{file.filename}", "wb") as f:
            f.write(content)

        # Return the response
        return FileResponse(
            id=file_id,
            object="file",
            bytes=file_size,
            created_at=created_at,
            filename=file.filename,
            purpose=purpose
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
