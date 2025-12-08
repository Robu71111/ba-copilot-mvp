"""Project management routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from backend.core.database import db

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    type: str = "General"
    industry: str = "General"
    description: str = ""

@router.post("")
async def create_project(project: ProjectCreate):
    try:
        project_id = db.create_project(project.name, project.type, project.industry, project.description)
        return {"project_id": project_id, "project_name": project.name, "project_type": project.type, "industry": project.industry}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
async def get_projects():
    try:
        projects = db.get_all_projects()
        return [{"project_id": p[0], "project_name": p[1], "project_type": p[2], "industry": p[3], "created_at": p[4]} for p in projects]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}")
async def get_project(project_id: int):
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"project_id": project[0], "project_name": project[1], "project_type": project[2], "industry": project[3]}

@router.delete("/{project_id}")
async def delete_project(project_id: int):
    try:
        db.delete_project(project_id)
        return {"message": "Project deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}/summary")
async def get_project_summary(project_id: int):
    summary = db.get_project_summary(project_id)
    return summary