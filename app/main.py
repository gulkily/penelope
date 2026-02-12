from pathlib import Path

from dotenv import load_dotenv

from fastapi import FastAPI, Request
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

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(transcript_router, prefix="/api")
app.include_router(transcription_router, prefix="/api")


@app.middleware("http")
async def require_auth(request: Request, call_next):
    path = request.url.path
    if request.method == "OPTIONS":
        return await call_next(request)
    if (
        path.startswith("/static/")
        or path == "/favicon.ico"
        or path.startswith("/api/auth")
        or path == "/lobby"
        or path == "/session/reset"
    ):
        return await call_next(request)

    session = auth.get_session_account(request)
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
        {
            "request": request,
            "current_page": "dashboard",
            "show_back_to_dashboard": False,
            "show_ledger_link": False,
        },
    )


@app.get("/lobby", response_class=HTMLResponse)
def lobby(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "lobby.html",
        {
            "request": request,
            "current_page": "lobby",
            "show_back_to_dashboard": False,
            "show_ledger_link": False,
        },
    )


@app.get("/ledger", response_class=HTMLResponse)
def ledger(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "ledger.html",
        {
            "request": request,
            "current_page": "ledger",
            "show_back_to_dashboard": False,
            "show_ledger_link": False,
        },
    )


@app.get("/session/reset", response_class=HTMLResponse)
def session_reset(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "session_reset.html",
        {
            "request": request,
            "current_page": "session_reset",
            "show_back_to_dashboard": False,
            "show_ledger_link": False,
        },
    )


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "favicon.ico")


@app.get("/projects", response_class=HTMLResponse)
def manage_projects(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "manage_projects.html",
        {
            "request": request,
            "current_page": "projects",
            "show_back_to_dashboard": True,
            "show_ledger_link": False,
        },
    )


@app.get("/settings", response_class=HTMLResponse)
def settings(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "current_page": "settings",
            "show_back_to_dashboard": True,
            "show_ledger_link": True,
        },
    )


@app.get("/debug/confetti", response_class=HTMLResponse)
def confetti_debug(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "confetti_debug.html",
        {
            "request": request,
            "current_page": "confetti_debug",
            "show_back_to_dashboard": True,
            "show_ledger_link": False,
        },
    )
