"""User stories generation routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from backend.core.database import db
from backend.services.story_generator import story_gen

router = APIRouter()

class StoriesGenerate(BaseModel):
    input_id: int
    project_type: str = "General"

@router.post("/generate")
async def generate_stories(data: StoriesGenerate):
    try:
        # Get requirements
        requirements = db.get_requirements(data.input_id)
        
        if not requirements:
            raise HTTPException(status_code=404, detail="No requirements found")
        
        # Format requirements text
        req_text = "## Requirements\n"
        for req in requirements:
            req_text += f"- {req[1]}: {req[3]}\n"
        
        # Generate stories
        stories = story_gen.generate(req_text, data.project_type)
        
        return stories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{input_id}")
async def get_stories(input_id: int):
    # Implementation: retrieve from database
    return {"stories": []}

@router.post("/export/jira")
async def export_jira(data: dict):
    stories_data = data.get('stories', {})
    csv = story_gen.format_for_jira(stories_data)
    return {"csv": csv}