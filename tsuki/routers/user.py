import base64
import os

import requests
from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext

from tsuki.database import *
from tsuki.models import User
from tsuki.oauth import *

user = APIRouter(prefix="/user")
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(parent_dir, "templates"))
password_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
limit = 5


@user.get("/", response_class=HTMLResponse)
async def get_user(
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
    user_data = user.dict()
    del user_data["password"]
    if more:
        limit += 5
    else:
        limit = 5
    user_data["posts"] = await read_post_count(user.username)
    return templates.TemplateResponse(
        "user.html",
        {
            "request": request,
            "user_data": user_data,
            "avatar": await read_avatar(user.username),
            "settings": True,
            "posts": await read_recent_posts(user.username, limit),
            "followers": await read_followers(user.username),
            "following": await read_following(user.username),
        },
    )


@user.get("/{username}", response_class=HTMLResponse)
async def get_user_by_name(
    username: str,
    request: Request,
    user: User = Depends(get_current_user),
    more: bool = False,
):
    global limit
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
    if more:
        limit += 5
    else:
        limit = 5
    user_data["posts"] = await read_post_count(username)
    return templates.TemplateResponse(
        "user.html",
        {
            "request": request,
            "user_data": user_data,
            "avatar": await read_avatar(username),
            "settings": False,
            "posts": await read_recent_posts(username, limit),
            # Check if the logged in user follows the searched user
            "follows": await follows(user.username, username) if user else None,
            "followers": await read_followers(username),
            "following": await read_following(username),
        },
    )


@user.get("/settings/update-avatar")
async def update_avatar_html(request: Request, user: User = Depends(get_current_user)):
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
        "update.html", {"request": request, "type": "avatar"}
    )


@user.post("/settings/update-avatar")
async def update_avatar_(
    request: Request,
    user: User = Depends(get_current_user),
    avatar: UploadFile = File(...),
):
    content = await avatar.read()
    encoded = base64.b64encode(content)
    response = requests.post(
        f"https://freeimage.host/api/1/upload?key={secrets.FREEIMAGE_API_KEY}&format=json",
        data={"source": encoded},
    )
    await update_avatar(user.username, response.json()["image"]["url"])
    return templates.TemplateResponse(
        "response.html",
        {"request": request, "message": "Avatar updated successfully."},
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
    result = await update_user(user.username, {"password": password})
    if not result:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "400 Bad Request",
                "message": "Unable to change password, try again later.",
            },
        )
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
    result = await update_user(user.username, {"username": form["username"]})
    if not result:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "400 Bad Request",
                "message": "Unable to change username, try again later.",
            },
        )
    request.session["Authorization"] = create_access_token(form["username"])
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
    result = await delete_user(user.username)
    if not result:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "400 Bad Request",
                "message": "Unable to delete account, try again later.",
            },
        )
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
