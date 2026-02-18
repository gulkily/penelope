import os
from pathlib import Path

from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import auth
from app.api import router as api_router
from app.api_auth import router as auth_router
from app.api_transcript import router as transcript_router
from app.api_transcription import router as transcription_router
from app.db import init_db

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def _parse_csv_env(name: str) -> list[str]:
    raw_value = os.getenv(name, "")
    return [entry.strip() for entry in raw_value.split(",") if entry.strip()]


app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

trusted_hosts = _parse_csv_env("TRUSTED_HOSTS")
if trusted_hosts:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

cors_allow_origins = _parse_csv_env("CORS_ALLOW_ORIGINS")
if cors_allow_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(transcript_router, prefix="/api")
app.include_router(transcription_router, prefix="/api")


def _build_template_context(request: Request, current_page: str) -> dict:
    session_account = getattr(request.state, "session_account", None)
    return {
        "request": request,
        "current_page": current_page,
        "session_account": session_account,
    }


@app.middleware("http")
async def require_auth(request: Request, call_next):
    path = request.url.path
    if request.method == "OPTIONS":
        return await call_next(request)
    request.state.session_account = auth.get_session_account(request)
    if (
        path.startswith("/static/")
        or path == "/favicon.ico"
        or path.startswith("/api/auth")
        or path == "/lobby"
        or path == "/session/reset"
    ):
        return await call_next(request)

    session = request.state.session_account
    if session:
        return await call_next(request)

    if path.startswith("/api/"):
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    return RedirectResponse(url="/session/reset", status_code=302)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        _build_template_context(request, "dashboard"),
    )


@app.get("/lobby", response_class=HTMLResponse)
def lobby(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "lobby.html",
        _build_template_context(request, "lobby"),
    )


@app.get("/ledger", response_class=HTMLResponse)
def ledger(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "ledger.html",
        _build_template_context(request, "ledger"),
    )


@app.get("/session/reset", response_class=HTMLResponse)
def session_reset(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "session_reset.html",
        _build_template_context(request, "session_reset"),
    )


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "favicon.ico")


@app.get("/projects", response_class=HTMLResponse)
def manage_projects(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "manage_projects.html",
        _build_template_context(request, "projects"),
    )


@app.get("/settings", response_class=HTMLResponse)
def settings(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "settings.html",
        _build_template_context(request, "settings"),
    )


@app.get("/settings/magic-links", response_class=HTMLResponse)
def magic_links(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "magic_links.html",
        _build_template_context(request, "settings"),
    )


@app.get("/debug/confetti", response_class=HTMLResponse)
def confetti_debug(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "confetti_debug.html",
        _build_template_context(request, "confetti_debug"),
    )
