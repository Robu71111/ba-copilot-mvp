"""Acceptance criteria generation routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from backend.services.criteria_generator import criteria_gen

router = APIRouter()

class CriteriaGenerate(BaseModel):
    story_id: int
    user_story: str

@router.post("/generate")
async def generate_criteria(data: CriteriaGenerate):
    try:
        criteria = criteria_gen.generate(data.user_story)
        return criteria
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{story_id}")
async def get_criteria(story_id: int):
    # Implementation: retrieve from database
    return {"criteria": []}

@router.post("/export/gherkin")
async def export_gherkin(data: dict):
    criteria_data = data.get('criteria', {})
    feature_name = data.get('feature_name', 'Feature')
    gherkin = criteria_gen.format_for_gherkin(criteria_data, feature_name)
    return {"gherkin": gherkin}