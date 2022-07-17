import os

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from tsuki.routers.auth import get_current_user
from tsuki.routers.database import *
from tsuki.routers.models import User, Post


feed = APIRouter(prefix="/feed", tags=["Feed"])
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(parent_dir, "templates"))


@feed.get("/")
async def get_user_feed(request: Request, user: User = Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "401 Unauthorized",
                "message": "User not logged in.",
            },
        )
    posts = await read_feed_posts(user.username)
    return templates.TemplateResponse("feed.html", {"request": request, "posts": posts})
