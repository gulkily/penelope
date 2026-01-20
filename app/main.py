from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api import router as api_router
from app.db import init_db

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(api_router, prefix="/api")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "favicon.ico")


@app.get("/projects", response_class=HTMLResponse)
def manage_projects(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("manage_projects.html", {"request": request})


@app.get("/settings", response_class=HTMLResponse)
def settings(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("settings.html", {"request": request})


@app.get("/debug/confetti", response_class=HTMLResponse)
def confetti_debug(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("confetti_debug.html", {"request": request})
