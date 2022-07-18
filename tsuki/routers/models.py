from datetime import datetime

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    email: EmailStr
    username: str
    password: str
    verified: bool
    created_at: datetime


class Post(BaseModel):
    body: str
    id: str
    created_at: datetime


class PostResponse(BaseModel):
    username: str
    id: str
    body: str
    created_at: datetime
