import logging
import os
from pathlib import Path
from urllib.parse import urlencode

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request
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
from app.db import get_db_path, get_missing_import_map_tables, init_db
from app.env_sync import get_missing_env_defaults
from app.feature_flags import NAVBAR_ITEM_DEFINITIONS
from app.feature_flags import get_feature_flags

BASE_DIR = Path(__file__).resolve().parent.parent
logger = logging.getLogger(__name__)


def _notify_env_defaults_status_on_launch() -> None:
    try:
        status = get_missing_env_defaults(
            env_path=BASE_DIR / ".env",
            env_example_path=BASE_DIR / ".env.example",
        )
    except OSError:
        logger.exception("Failed to check missing .env defaults from .env.example.")
        return
    if not status.get("example_found"):
        return
    missing_count = int(status.get("missing_count", 0))
    if missing_count <= 0:
        return
    logger.warning(
        "Detected %s missing .env settings. Run `./pnl env-sync` to append defaults from .env.example.",
        missing_count,
    )


_notify_env_defaults_status_on_launch()
load_dotenv(dotenv_path=BASE_DIR / ".env")


def _parse_csv_env(name: str) -> list[str]:
    raw_value = os.getenv(name, "")
    return [entry.strip() for entry in raw_value.split(",") if entry.strip()]


def _build_navbar_items(enabled_keys: set[str]) -> list[dict]:
    return [item for item in NAVBAR_ITEM_DEFINITIONS if item["key"] in enabled_keys]


def _normalize_session_reset_next(raw_value: str) -> str:
    candidate = (raw_value or "").strip()
    if not candidate or not candidate.startswith("/") or candidate.startswith("//"):
        return "/"
    if candidate == "/lobby" or candidate.startswith("/lobby?"):
        return "/"
    return candidate


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
    session_is_admin = (
        auth.is_admin_account(session_account.account_id) if session_account else False
    )
    feature_flags = get_feature_flags()
    navbar_items = _build_navbar_items(set(feature_flags.navbar_enabled_items))
    return {
        "request": request,
        "current_page": current_page,
        "session_account": session_account,
        "session_is_admin": session_is_admin,
        "navbar_items": navbar_items,
        "lobby_auth_enabled": feature_flags.lobby_auth_enabled,
        "recorder_enabled": feature_flags.recorder_enabled,
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
        or path == "/welcome"
        or path == "/session/reset"
    ):
        return await call_next(request)

    session = request.state.session_account
    if session:
        return await call_next(request)

    if path.startswith("/api/"):
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    target = request.url.path
    if request.url.query:
        target = f"{target}?{request.url.query}"
    target = _normalize_session_reset_next(target)
    if target == "/":
        reset_url = "/session/reset"
    else:
        reset_url = f"/session/reset?{urlencode({'next': target})}"
    return RedirectResponse(url=reset_url, status_code=302)


@app.on_event("startup")
def startup() -> None:
    init_db()
    missing_import_tables = get_missing_import_map_tables()
    if missing_import_tables:
        logger.warning(
            "Import map schema check failed after init_db for db=%s. Missing tables: %s",
            get_db_path(),
            ", ".join(missing_import_tables),
        )


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        _build_template_context(request, "dashboard"),
    )


@app.get("/lobby", response_class=HTMLResponse)
def lobby(request: Request) -> HTMLResponse:
    context = _build_template_context(request, "lobby")
    context["lobby_token_present"] = bool((request.query_params.get("token") or "").strip())
    return templates.TemplateResponse(
        "lobby.html",
        context,
    )


@app.get("/ledger", response_class=HTMLResponse)
def ledger(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "ledger.html",
        _build_template_context(request, "ledger"),
    )


@app.get("/session/reset", response_class=HTMLResponse)
def session_reset(request: Request) -> HTMLResponse:
    next_path = _normalize_session_reset_next(request.query_params.get("next", ""))
    session = getattr(request.state, "session_account", None)
    if session:
        return RedirectResponse(url=next_path, status_code=302)
    context = _build_template_context(request, "session_reset")
    context["session_reset_next"] = next_path
    return templates.TemplateResponse(
        "session_reset.html",
        context,
    )


@app.get("/welcome", response_class=HTMLResponse)
def welcome(request: Request) -> HTMLResponse:
    session = getattr(request.state, "session_account", None)
    if session:
        return RedirectResponse(url="/", status_code=302)
    token = (request.query_params.get("token") or "").strip()
    if token:
        context = _build_template_context(request, "lobby")
        context["lobby_token_present"] = True
        return templates.TemplateResponse(
            "lobby.html",
            context,
        )
    return templates.TemplateResponse(
        "welcome.html",
        _build_template_context(request, "welcome"),
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


@app.get("/settings/users", response_class=HTMLResponse)
def users(request: Request) -> HTMLResponse:
    session = getattr(request.state, "session_account", None)
    if not session or not auth.is_admin_account(session.account_id):
        raise HTTPException(status_code=403, detail="Admin access required")
    return templates.TemplateResponse(
        "users.html",
        _build_template_context(request, "settings"),
    )


@app.get("/debug/confetti", response_class=HTMLResponse)
def confetti_debug(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "confetti_debug.html",
        _build_template_context(request, "confetti_debug"),
    )
