from datetime import datetime

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    email: EmailStr
    username: str
    password: str
    verified: bool = False
    created_at: datetime = datetime.now()
