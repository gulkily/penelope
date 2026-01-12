from fastapi import APIRouter, HTTPException

from app import db
from app.schemas import ItemCreate, ObjectiveUpdate, ProgressUpdate, QuestionsUpdate

router = APIRouter()


@router.get("/projects")
def list_projects() -> dict:
    return {"projects": db.list_projects()}


@router.get("/projects/{project_id}")
def get_project(project_id: int) -> dict:
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/projects/{project_id}/items")
def add_item(project_id: int, payload: ItemCreate) -> dict:
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        item = db.add_item(project_id, payload.section, payload.text.strip())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"item": item}


@router.put("/projects/{project_id}/questions")
def update_questions(project_id: int, payload: QuestionsUpdate) -> dict:
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.update_questions(project_id, payload.questions)
    return {"questions": payload.questions}


@router.put("/projects/{project_id}/objective")
def update_objective(project_id: int, payload: ObjectiveUpdate) -> dict:
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.update_objective(project_id, payload.objective)
    return {"objective": payload.objective}


@router.put("/projects/{project_id}/progress")
def update_progress(project_id: int, payload: ProgressUpdate) -> dict:
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.update_progress(project_id, payload.progress)
    return {"progress": payload.progress}
