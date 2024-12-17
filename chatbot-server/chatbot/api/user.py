from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlmodel import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from chatbot.db.database import DbSession
from chatbot.db.user import create_user, get_user_by_email, delete_user, update_user
from chatbot.db.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/v1/users",
    tags=["users"],
)

class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr

    class Config:
        from_attributes = True


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user_endpoint(user: UserCreateRequest, db: DbSession, token: str = Depends(oauth2_scheme)):
    existing_user = get_user_by_email(db, user.email)
    if (existing_user):
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = create_user(db, user.email, user.password)
    return UserResponse.from_orm(new_user)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_endpoint(user_id: UUID, db: DbSession, token: str = Depends(oauth2_scheme)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)

@router.delete("/{user_id}", status_code=204)
async def delete_user_endpoint(user_id: UUID, db: DbSession, token: str = Depends(oauth2_scheme)):
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

@router.put("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(user_id: UUID, user: UserCreateRequest, db: DbSession, token: str = Depends(oauth2_scheme)):
    updated_user = update_user(db, user_id, email=user.email, password=user.password)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(updated_user)

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}