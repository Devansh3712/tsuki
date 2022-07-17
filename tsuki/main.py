import os
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from tsuki.config import secrets
from tsuki.routers.auth import auth
from tsuki.routers.database import initdb
from tsuki.routers.feed import feed
from tsuki.routers.models import User
from tsuki.routers.post import post
from tsuki.routers.user import user, get_current_user

app = FastAPI(title="Tsuki")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=secrets.SECRET_KEY)
app.mount(
    "/static", StaticFiles(directory=os.path.join("tsuki", "static")), name="static"
)
app.include_router(auth)
app.include_router(feed)
app.include_router(post)
app.include_router(user)
templates = Jinja2Templates(directory=os.path.join("tsuki", "templates"))


@app.on_event("startup")
async def startup():
    await initdb()


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
