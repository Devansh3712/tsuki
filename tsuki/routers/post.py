import os
from datetime import datetime
from uuid import uuid4

import pytz
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from tsuki.database import *
from tsuki.oauth import get_current_user
from tsuki.routers.models import Comment, CommentResponse, Post, User

post = APIRouter(prefix="/post")
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(parent_dir, "templates"))
limit = 5


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
    if not user.verified:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "403 Forbidden",
                "message": "Verify your account to make posts.",
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
    return await get_post(post_data.id, request, user)


@post.get("/{_id}", response_class=HTMLResponse)
async def get_post(
    _id: str,
    request: Request,
    user: User = Depends(get_current_user),
    more: bool = False,
):
    global limit
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
    if more:
        limit += 5
    else:
        limit = 5
    comments = await read_comments(_id, limit)
    if user is not None:
        for index in range(len(comments)):
            comments[index] = CommentResponse(**comments[index].dict())
            if comments[index].username == user.username:
                comments[index].self_ = True
    return templates.TemplateResponse(
        "get_post.html",
        {
            "request": request,
            "post": post,
            "_self": True if user and (user.username == post.username) else False,
            "voted": await voted(user.username, _id) if user else None,
            "voters": await read_votes(_id),
            "comments": comments,
        },
    )


@post.get("/{_id}/delete")
async def delete_post_(
    _id: str, request: Request, user: User = Depends(get_current_user)
):
    if not user:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "401 Unauthorized",
                "message": "User not logged in.",
            },
        )
    post = await read_post(_id)
    if post.username != user.username:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "401 Unauthorized",
                "message": "Cannot perform this task.",
            },
        )
    await delete_post(_id)
    return templates.TemplateResponse(
        "response.html", {"request": request, "message": "Post deleted."}
    )


@post.get("/{_id}/toggle-vote")
async def toggle_vote_(
    _id: str, request: Request, user: User = Depends(get_current_user)
):
    if not user:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "401 Unauthorized",
                "message": "User not logged in.",
            },
        )
    await toggle_vote(user.username, _id)
    return await get_post(_id, request, user)


@post.post("/{_id}/comment")
async def create_comment_(
    _id: str, request: Request, user: User = Depends(get_current_user)
):
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
    form["username"] = user.username
    form["created_at"] = datetime.now()
    form["post_id"] = _id
    form["id"] = uuid4().hex
    comment = Comment(**form)
    result = await create_comment(comment)
    if not result:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "400 Bad Request",
                "message": "Unable to add the comment, please try again later.",
            },
        )
    return await get_post(_id, request, user)


@post.get("/{_id}/comment/delete")
async def delete_comment_(
    _id: str, comm_id: str, request: Request, user: User = Depends(get_current_user)
):
    if not user:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "401 Unauthorized",
                "message": "User not logged in.",
            },
        )
    await delete_comment(comm_id)
    return await get_post(_id, request, user)
