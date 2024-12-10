from fastapi import APIRouter

router = APIRouter(
    prefix="/v1/files",
    tags=["chat"],
)
