import os

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from tsuki.database import *
from tsuki.oauth import get_current_user
from tsuki.routers.models import User


search = APIRouter(prefix="/search", tags=["Search"])
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(parent_dir, "templates"))


@search.get("/", response_class=HTMLResponse)
async def search_user_html(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})


@search.post("/", response_class=HTMLResponse)
async def search_user(request: Request, user: User = Depends(get_current_user)):
    form = await request.form()
    # Set a search cookie for use in toggle follow function
    if form.get("search"):
        request.session["search"] = form["search"]
    users = await read_users(request.session["search"])
    if not users:
        return templates.TemplateResponse("search.html", {"request": request})
    for index, _user in enumerate(users):
        user_data = _user.dict()
        del user_data["email"]
        del user_data["password"]
        posts = await read_recent_posts(user_data["username"])
        followers = await read_followers(user_data["username"])
        following = await read_following(user_data["username"])
        user_data["posts"] = len(posts)
        user_data["followers"] = len(followers)
        user_data["following"] = len(following)
        user_data["follows"] = (
            await follows(user.username, user_data["username"]) if user else None
        )
        users[index] = user_data
    return templates.TemplateResponse(
        "search.html", {"request": request, "users": users}
    )


# A different endpoint so that when the follow/unfollow button
# is clicked, user stays on the search page
@search.post("/{username}/toggle-follow")
async def toggle_search_follow(
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
    return await search_user(request, user)
