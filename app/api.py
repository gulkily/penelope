from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app import db
from app.schemas import (
    GoalUpdate,
    ItemCreate,
    ItemUpdate,
    ObjectiveUpdate,
    ProgressUpdate,
    ProgressHistoryResponse,
    ProjectArchiveUpdate,
    ProjectCreate,
    QuestionsUpdate,
    SummaryUpdate,
)

router = APIRouter()
PROJECTS_PAGE_SIZE = 100


@router.get("/backup")
def backup_database() -> FileResponse:
    db_path = db.get_db_path()
    if not db_path.exists():
        raise HTTPException(status_code=404, detail="Database not found")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"north_star_backup_{timestamp}.sqlite"
    return FileResponse(
        path=db_path,
        filename=filename,
        media_type="application/x-sqlite3",
    )


@router.get("/projects")
def list_projects(
    include_archived: bool = False,
    page: int | None = None,
    sort_key: str = "id",
    sort_dir: str = "asc",
) -> dict:
    try:
        if page is None:
            projects, total = db.list_projects(
                include_archived=include_archived,
                sort_key=sort_key,
                sort_direction=sort_dir,
            )
            return {"projects": projects, "total": total}
        if page < 1:
            raise HTTPException(status_code=400, detail="page must be >= 1")
        offset = (page - 1) * PROJECTS_PAGE_SIZE
        projects, total = db.list_projects(
            include_archived=include_archived,
            limit=PROJECTS_PAGE_SIZE,
            offset=offset,
            sort_key=sort_key,
            sort_direction=sort_dir,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "projects": projects,
        "total": total,
        "page": page,
        "page_size": PROJECTS_PAGE_SIZE,
    }


@router.get("/projects/{project_id}")
def get_project(project_id: int) -> dict:
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Resident not found")
    return project


@router.post("/projects")
def create_project(payload: ProjectCreate) -> dict:
    project = db.create_project(payload.name.strip())
    return {"project": project}


@router.put("/projects/{project_id}/archive")
def update_project_archive(project_id: int, payload: ProjectArchiveUpdate) -> dict:
    updated = db.set_project_archived(project_id, payload.archived)
    if not updated:
        raise HTTPException(status_code=404, detail="Resident not found")
    return {"archived": payload.archived}


@router.post("/projects/{project_id}/items")
def add_item(project_id: int, payload: ItemCreate) -> dict:
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Resident not found")
    try:
        item = db.add_item(project_id, payload.section, payload.text.strip())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"item": item}


@router.put("/items/{item_id}")
def update_item(item_id: int, payload: ItemUpdate) -> dict:
    item = db.update_item(item_id, payload.text.strip())
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": item}


@router.delete("/items/{item_id}")
def delete_item(item_id: int) -> dict:
    deleted = db.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"deleted": True}


@router.put("/projects/{project_id}/questions")
def update_questions(project_id: int, payload: QuestionsUpdate) -> dict:
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Resident not found")
    db.update_questions(project_id, payload.questions)
    return {"questions": payload.questions}


@router.put("/projects/{project_id}/summary")
def update_summary(project_id: int, payload: SummaryUpdate) -> dict:
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Resident not found")
    db.update_summary(project_id, payload.summary)
    return {"summary": payload.summary}


@router.put("/projects/{project_id}/objective")
def update_objective(project_id: int, payload: ObjectiveUpdate) -> dict:
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Resident not found")
    db.update_objective(project_id, payload.objective)
    return {"objective": payload.objective}


@router.put("/projects/{project_id}/goal")
def update_goal(project_id: int, payload: GoalUpdate) -> dict:
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Resident not found")
    db.update_goal(project_id, payload.goal)
    return {"goal": payload.goal}


@router.put("/projects/{project_id}/progress")
def update_progress(project_id: int, payload: ProgressUpdate) -> dict:
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Resident not found")
    db.update_progress(project_id, payload.progress)
    return {"progress": payload.progress}


@router.get(
    "/projects/{project_id}/progress/history",
    response_model=ProgressHistoryResponse,
)
def list_progress_history(project_id: int) -> dict:
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Resident not found")
    history = db.list_progress_history(project_id)
    return {"history": history}
