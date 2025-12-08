"""Input handling routes - file upload, text input"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from backend.core.database import db
from backend.services.document_parser import parser

router = APIRouter()

class TextInput(BaseModel):
    project_id: int
    text: str
    input_type: str = "text"

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), project_id: int = Form(...)):
    try:
        content = await file.read()
        text = parser.parse_document(file.filename, content)
        is_valid, message = parser.validate_text(text)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        input_id = db.save_input(project_id, "document", text, file.filename)
        return {"input_id": input_id, "file_name": file.filename, "text_length": len(text), "message": "Document uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text")
async def submit_text(input_data: TextInput):
    try:
        is_valid, message = parser.validate_text(input_data.text)
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        input_id = db.save_input(input_data.project_id, input_data.input_type, input_data.text)
        return {"input_id": input_id, "text_length": len(input_data.text), "message": "Text submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mock-transcript")
async def get_mock_transcript():
    from backend.services.speech_to_text import stt
    transcript = stt.mock_transcribe()
    return {"transcript": transcript, "source": "mock"}