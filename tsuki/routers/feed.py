import os

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from tsuki.database import *
from tsuki.models import User
from tsuki.oauth import get_current_user

feed = APIRouter(prefix="/feed")
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(parent_dir, "templates"))
limit = 10


@feed.get("/", response_class=HTMLResponse)
async def get_user_feed(
    request: Request, user: User = Depends(get_current_user), more: bool = False
):
    global limit
    if not user:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "401 Unauthorized",
                "message": "User not logged in.",
            },
        )
    if more:
        limit += 5
    else:
        limit = 10
    posts = await read_feed_posts(user.username, limit)
    return templates.TemplateResponse("feed.html", {"request": request, "posts": posts})
