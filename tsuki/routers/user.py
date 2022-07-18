import os

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext

from tsuki.database import *
from tsuki.oauth import *
from tsuki.routers.models import User


user = APIRouter(prefix="/user", tags=["Users"])
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(parent_dir, "templates"))
password_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


@user.get("/", response_class=HTMLResponse)
async def get_user(request: Request, user: User = Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "401 Unauthorized",
                "message": "User not logged in.",
            },
        )
    user_data = user.dict()
    del user_data["password"]
    posts = await read_recent_posts(user.username)
    followers = await read_followers(user.username)
    following = await read_following(user.username)
    user_data["posts"] = len(posts)
    user_data["followers"] = len(followers)
    user_data["following"] = len(following)
    return templates.TemplateResponse(
        "user.html",
        {
            "request": request,
            "user_data": user_data,
            "settings": True,
            "posts": posts,
        },
    )


@user.get("/{username}", response_class=HTMLResponse)
async def get_user_by_name(
    username: str, request: Request, user: User = Depends(get_current_user)
):
    if user and username == user.username:
        return await get_user(request, user)
    _user = await read_user(username)
    if not _user:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "404 Not Found.",
                "message": "User not found.",
            },
        )
    user_data = _user.dict()
    del user_data["email"]
    del user_data["password"]
    posts = await read_recent_posts(username)
    followers = await read_followers(username)
    following = await read_following(username)
    user_data["posts"] = len(posts)
    user_data["followers"] = len(followers)
    user_data["following"] = len(following)
    _follows = await follows(user.username, username) if user else None
    return templates.TemplateResponse(
        "user.html",
        {
            "request": request,
            "user_data": user_data,
            "settings": False,
            "posts": posts,
            "follows": _follows,
        },
    )


@user.get("/settings/update-password", response_class=HTMLResponse)
async def update_user_password_html(
    request: Request, user: User = Depends(get_current_user)
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
    return templates.TemplateResponse(
        "update.html", {"request": request, "type": "password"}
    )


@user.post("/settings/update-password", response_class=HTMLResponse)
async def update_user_password(
    request: Request, user: User = Depends(get_current_user)
):
    form = await request.form()
    if password_ctx.verify(form["password"], user.password):
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "403 Forbidden",
                "message": "New password cannot be the same as the original.",
            },
        )
    password = password_ctx.hash(form["password"])
    await update_user(user.username, {"password": password})
    return templates.TemplateResponse(
        "response.html",
        {"request": request, "message": "Password updated successfully."},
    )


@user.get("/settings/update-username", response_class=HTMLResponse)
async def update_username_html(
    request: Request, user: User = Depends(get_current_user)
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
    return templates.TemplateResponse(
        "update.html", {"request": request, "type": "username"}
    )


@user.post("/settings/update-username", response_class=HTMLResponse)
async def update_username(request: Request, user: User = Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "401 Unauthorized",
                "message": "User not logged in.",
            },
        )
    form = await request.form()
    if user.username == form["username"]:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "403 Forbidden",
                "message": "New username cannot be the same as the original.",
            },
        )
    exists = await read_user(form["username"])
    if exists:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "403 Forbidden",
                "message": "Username not available or already taken.",
            },
        )
    await update_user(user.username, {"username": form["username"]})
    access_token = create_access_token(form["username"])
    request.session["Authorization"] = access_token
    return templates.TemplateResponse(
        "response.html",
        {"request": request, "message": "Username updated successfully."},
    )


@user.get("/settings/delete", response_class=HTMLResponse)
async def delete_user_html(request: Request, user: User = Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "401 Unauthorized",
                "message": "User not logged in.",
            },
        )
    return templates.TemplateResponse("delete.html", {"request": request})


@user.post("/settings/delete", response_class=HTMLResponse)
async def delete_user_(request: Request, user: User = Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "401 Unauthorized",
                "message": "User not logged in.",
            },
        )
    form = await request.form()
    if not password_ctx.verify(form["password"], user.password):
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "403 Forbidden",
                "message": "Incorrect password.",
            },
        )
    await delete_user(user.username)
    del request.session["Authorization"]
    return templates.TemplateResponse(
        "response.html",
        {
            "request": request,
            "message": "Account deleted successfully. Thankyou for using Tsuki :)",
        },
    )


@user.post("/{username}/toggle-follow")
async def toggle_follow_(
    username: str, request: Request, user: User = Depends(get_current_user)
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
    await toggle_follow(user.username, username)
    return await get_user_by_name(username, request, user)
