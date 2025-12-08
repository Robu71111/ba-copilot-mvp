"""Requirements extraction routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from backend.core.database import db
from backend.services.requirements_extractor import extractor

router = APIRouter()

class RequirementsExtract(BaseModel):
    input_id: int
    project_type: str = "General"
    industry: str = "General"

@router.post("/extract")
async def extract_requirements(data: RequirementsExtract):
    try:
        # Get input text
        conn = db._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT raw_text FROM inputs WHERE input_id = ?", (data.input_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Input not found")
        
        raw_text = result[0]
        
        print(f"Extracting requirements for input_id: {data.input_id}")
        print(f"Text length: {len(raw_text)}")
        
        # Extract requirements
        try:
            requirements = extractor.extract(raw_text, data.project_type, data.industry)
            print(f"Extracted {requirements['total_count']} requirements")
        except Exception as extract_error:
            print(f"Extraction failed: {str(extract_error)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Requirements extraction error: {str(extract_error)}")
        
        # Save to database
        try:
            all_reqs = requirements['functional'] + requirements['non_functional']
            if all_reqs:
                db.save_requirements(data.input_id, all_reqs)
                print(f"Saved {len(all_reqs)} requirements to database")
        except Exception as db_error:
            print(f"Database save error: {str(db_error)}")
            # Continue even if saving fails
        
        return requirements
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in extract_requirements: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{input_id}")
async def get_requirements(input_id: int):
    try:
        requirements = db.get_requirements(input_id)
        return {"requirements": [{"req_code": r[1], "req_type": r[2], "description": r[3]} for r in requirements]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))