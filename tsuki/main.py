import os

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from tsuki.config import secrets
from tsuki.database import initdb
from tsuki.models import User
from tsuki.routers.auth import auth
from tsuki.routers.explore import explore
from tsuki.routers.feed import feed
from tsuki.routers.post import post
from tsuki.routers.search import search
from tsuki.routers.user import get_current_user, user

app = FastAPI(docs_url=None, redoc_url=None)
app.add_middleware(SessionMiddleware, secret_key=secrets.SECRET_KEY)
app.mount(
    "/static", StaticFiles(directory=os.path.join("tsuki", "static")), name="static"
)
app.include_router(auth)
app.include_router(explore)
app.include_router(feed)
app.include_router(post)
app.include_router(search)
app.include_router(user)
templates = Jinja2Templates(directory=os.path.join("tsuki", "templates"))


@app.on_event("startup")
async def startup():
    await initdb()


@app.exception_handler(status.HTTP_400_BAD_REQUEST)
async def page_not_found(request: Request, exception: Exception):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error": "400 Bad Request",
            "message": "The server was unable to process the request, try again later.",
        },
    )


@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def page_not_found(request: Request, exception: Exception):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error": "404 Not Found",
            "message": "The requested endpoint was not found.",
        },
    )


@app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
async def internal_server_error(request: Request, exception: Exception):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error": "500 Internal Server Error",
            "message": "An unexpected error occured, try again later.",
        },
    )


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse(
        "auth.html", {"request": request, "type": "signup"}
    )


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse(
        "auth.html", {"request": request, "type": "login"}
    )


@app.get("/logout", response_class=HTMLResponse)
async def logout(request: Request, user: User = Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "401 Unauthorized",
                "message": "User not logged in.",
            },
        )
    del request.session["Authorization"]
    return templates.TemplateResponse(
        "response.html", {"request": request, "message": "Logged out successfully."}
    )
