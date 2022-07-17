import os
import pytz
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from tsuki.routers.auth import get_current_user
from tsuki.routers.database import *
from tsuki.routers.models import User, Post


post = APIRouter(prefix="/post", tags=["Posts"])
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(parent_dir, "templates"))


@post.get("/", response_class=HTMLResponse)
async def create_post_html(request: Request, user: User = Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "401 Unauthorized",
                "message": "User not logged in.",
            },
        )
    return templates.TemplateResponse("make_post.html", {"request": request})


@post.post("/", response_class=HTMLResponse)
async def create_post_(request: Request, user: User = Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "401 Unauthorized",
                "message": "User not logged in.",
            },
        )
    form = dict(await request.form())
    form["id"] = uuid4().hex
    form["created_at"] = datetime.now(pytz.timezone("Asia/Kolkata"))
    post_data = Post(**form)
    result = await create_post(user.username, post_data)
    if not result:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "400 Bad Request",
                "message": "Unable to create the post, please try again later.",
            },
        )
    return await get_post(post_data.id, request)


@post.get("/{_id}", response_class=HTMLResponse)
async def get_post(_id: str, request: Request):
    post = await read_post(_id)
    if not post:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "404 Not Found",
                "message": "Post not found or doesn't exist.",
            },
        )
    return templates.TemplateResponse(
        "get_post.html",
        {
            "request": request,
            "user": post.username,
            "body": post.body,
            "timestamp": post.created_at,
        },
    )
