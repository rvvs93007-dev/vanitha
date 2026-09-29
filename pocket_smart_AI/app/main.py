from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.db import init_db
from app.routes.auth import router as auth_router
from app.routes.history import router as history_router
from app.routes.planners import router as planner_router
from app.services.auth import decode_access_token, get_user_by_id


BASE_DIR = Path(__file__).resolve().parent

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "PocketSmart AI - budget-aware "
        "recommendation assistant."
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount(
    "/static",
    StaticFiles(
        directory=BASE_DIR / "static"
    ),
    name="static",
)


templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


@app.on_event("startup")
async def startup():
    init_db()


def get_template_context(
    request: Request,
):
    token = request.cookies.get(
        "pocketsmart_token"
    )

    user = None

    if token:
        user_id = decode_access_token(token)

        if user_id:
            user = get_user_by_id(
                user_id
            )

    return {
        "request": request,
        "user": user,
        "app_name": settings.app_name,
    }


@app.get(
    "/",
    response_class=HTMLResponse,
)
async def home(
    request: Request,
):
    return templates.TemplateResponse(
        "index.html",
        get_template_context(request),
    )


@app.get(
    "/register",
    response_class=HTMLResponse,
)
async def register_page(
    request: Request,
):
    return templates.TemplateResponse(
        "register.html",
        get_template_context(request),
    )


@app.get(
    "/login",
    response_class=HTMLResponse,
)
async def login_page(
    request: Request,
):
    return templates.TemplateResponse(
        "login.html",
        get_template_context(request),
    )


@app.get(
    "/dashboard",
    response_class=HTMLResponse,
)
async def dashboard(
    request: Request,
):
    return templates.TemplateResponse(
        "dashboard.html",
        get_template_context(request),
    )


@app.get(
    "/history",
    response_class=HTMLResponse,
)
async def history_page(
    request: Request,
):
    return templates.TemplateResponse(
        "history.html",
        get_template_context(request),
    )


@app.get(
    "/planner/home",
    response_class=HTMLResponse,
)
async def home_planner(
    request: Request,
):
    return templates.TemplateResponse(
        "home_planner.html",
        get_template_context(request),
    )


@app.get(
    "/planner/party",
    response_class=HTMLResponse,
)
async def party_planner(
    request: Request,
):
    return templates.TemplateResponse(
        "party_planner.html",
        get_template_context(request),
    )


@app.get(
    "/planner/jewelry",
    response_class=HTMLResponse,
)
async def jewelry_planner(
    request: Request,
):
    return templates.TemplateResponse(
        "jewelry_planner.html",
        get_template_context(request),
    )


@app.get(
    "/testimonials",
    response_class=HTMLResponse,
)
async def testimonials(
    request: Request,
):
    return templates.TemplateResponse(
        "testimonials.html",
        get_template_context(request),
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "application": settings.app_name,
    }


@app.get("/startup")
async def startup_status():
    return {
        "status": "ready",
        "environment": settings.app_env,
        "gemini_configured": bool(
            settings.gemini_api_key
        ),
        "model": settings.gemini_model,
    }


app.include_router(auth_router)
app.include_router(planner_router)
app.include_router(history_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )