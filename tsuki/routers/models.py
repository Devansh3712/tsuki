from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    email: EmailStr
    username: str
    password: str
    verified: bool = False
    created_at: datetime = datetime.now()


class Post(BaseModel):
    body: str
    id: str = uuid4().hex
    created_at: datetime = datetime.now()


class PostResponse(BaseModel):
    username: str
    id: str
    body: str
    created_at: datetime = datetime.now()
