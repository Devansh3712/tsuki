from datetime import datetime

from fastapi import Request
from jose import jwt

from tsuki.config import secrets
from tsuki.database import *
from tsuki.routers.models import User


def create_access_token(username: str):
    token = jwt.encode(
        {"user": username, "iat": datetime.now(), "iss": secrets.ISSUER},
        secrets.SECRET_KEY,
        algorithm="HS256",
    )
    return token


async def get_current_user(request: Request) -> User | None:
    try:
        token: str = request.session["Authorization"]
        payload = jwt.decode(token, secrets.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("user")
        if not username:
            return None
    except:
        return None
    user = await read_user(username)
    if not user:
        return None
    return user
