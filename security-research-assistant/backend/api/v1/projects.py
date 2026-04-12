"""Project CRUD API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.dependencies import get_db
from core.database.connection import DatabaseManager
from core.database.repositories.project_repo import ProjectRepository
from core.exceptions import ProjectNotFoundError
from core.logging import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/projects", tags=["projects"])


class CreateProjectRequest(BaseModel):
    name: str
    description: str | None = None


class UpdateProjectRequest(BaseModel):
    name: str | None = None
    description: str | None = None


@router.post("")
def create_project(
    request: CreateProjectRequest,
    db: DatabaseManager = Depends(get_db),
) -> dict:
    """Create a new investigation project."""
    repo = ProjectRepository()
    conn = db.get_connection()
    project = repo.create(conn, name=request.name.strip(), description=request.description)
    log.info("project_created", id=str(project.id), name=project.name)
    return {"project": project.model_dump(mode="json")}


@router.get("")
def list_projects(
    db: DatabaseManager = Depends(get_db),
) -> dict:
    """List all projects."""
    repo = ProjectRepository()
    conn = db.get_connection()
    projects = repo.list_all(conn)
    return {"projects": [p.model_dump(mode="json") for p in projects]}


@router.get("/{project_id}")
def get_project(
    project_id: UUID,
    db: DatabaseManager = Depends(get_db),
) -> dict:
    """Get a single project by ID."""
    repo = ProjectRepository()
    conn = db.get_connection()
    project = repo.get_by_id(conn, project_id)
    if project is None:
        raise ProjectNotFoundError(
            f"Project not found: {project_id}",
            details={"project_id": str(project_id)},
        )
    return project.model_dump(mode="json")


@router.put("/{project_id}")
def update_project(
    project_id: UUID,
    request: UpdateProjectRequest,
    db: DatabaseManager = Depends(get_db),
) -> dict:
    """Update a project's name or description."""
    repo = ProjectRepository()
    conn = db.get_connection()
    project = repo.update(conn, project_id, name=request.name, description=request.description)
    if project is None:
        raise ProjectNotFoundError(f"Project not found: {project_id}")
    return {"project": project.model_dump(mode="json")}


@router.delete("/{project_id}")
def delete_project(
    project_id: UUID,
    db: DatabaseManager = Depends(get_db),
) -> dict:
    """Delete a project and all its data."""
    repo = ProjectRepository()
    conn = db.get_connection()
    if not repo.delete(conn, project_id):
        raise ProjectNotFoundError(f"Project not found: {project_id}")
    log.info("project_deleted", id=str(project_id))
    return {"status": "ok", "project_id": str(project_id)}
