"""Audio recording and transcription routes"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from backend.core.database import db
from backend.services.audio_transcriber import audio_transcriber

router = APIRouter()


class AudioTranscription(BaseModel):
    audio_data: str  # Base64 encoded audio
    project_id: int
    audio_format: str = "wav"


@router.post("/transcribe")
async def transcribe_audio(data: AudioTranscription):
    """
    Transcribe audio to text using MAIN Gemini API (gemini-2.0-flash)
    This uses your MAIN API KEY, not the audio API key
    """
    try:
        print(f"Received audio transcription request for project {data.project_id}")
        print(f"Audio format: {data.audio_format}")
        print(f"Audio data length: {len(data.audio_data)} characters (base64)")
        
        # Transcribe audio using MAIN API
        transcript = audio_transcriber.transcribe_audio(
            data.audio_data,
            data.audio_format
        )
        
        if not transcript or len(transcript) < 10:
            raise Exception("Transcription resulted in empty or very short text")
        
        # Save to database as input
        input_id = db.save_input(
            data.project_id,
            "voice",
            transcript,
            file_name="audio_recording.wav"
        )
        
        print(f"✅ Transcription saved with input_id: {input_id}")
        
        return {
            "input_id": input_id,
            "transcript": transcript,
            "text_length": len(transcript),
            "message": "Audio transcribed successfully"
        }
    
    except Exception as e:
        print(f"Transcription error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_audio_file(
    file: UploadFile = File(...), 
    project_id: int = Form(...)
):
    """
    Upload and transcribe audio file
    Uses MAIN API KEY for transcription
    """
    try:
        print(f"Received audio file upload: {file.filename}")
        
        # Read audio file
        audio_data = await file.read()
        print(f"File size: {len(audio_data)} bytes")
        
        # Get file format
        audio_format = file.filename.split('.')[-1].lower()
        if audio_format not in ['wav', 'mp3', 'm4a', 'ogg', 'webm']:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported audio format: {audio_format}. Supported: wav, mp3, m4a, ogg, webm"
            )
        
        # Transcribe using MAIN API
        transcript = audio_transcriber.transcribe_audio(audio_data, audio_format)
        
        if not transcript or len(transcript) < 10:
            raise Exception("Transcription resulted in empty or very short text")
        
        # Save to database
        input_id = db.save_input(
            project_id,
            "voice",
            transcript,
            file_name=file.filename
        )
        
        print(f"✅ File transcription saved with input_id: {input_id}")
        
        return {
            "input_id": input_id,
            "transcript": transcript,
            "text_length": len(transcript),
            "file_name": file.filename
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check")
async def check_audio_api():
    """Check if audio APIs are configured"""
    config_status = audio_transcriber.is_configured()
    # helpful debug log if things are unexpected:
    print("is_configured() returned:", config_status, "type:", type(config_status))

    # Normalize config_status to a dict
    if isinstance(config_status, dict):
        audio_api = bool(config_status.get("audio_api", False))
        transcription_api = bool(config_status.get("transcription_api", False))
        both = bool(config_status.get("both", audio_api and transcription_api))
    else:
        # If upstream returned a single boolean, assume it means "both" (or change as needed)
        both = bool(config_status)
        audio_api = both
        transcription_api = both

    return {
        "audio_api_configured": audio_api,
        "transcription_api_configured": transcription_api,
        "audio_model": "gemini-2.5-flash-native-audio-preview-09-2025",
        "transcription_model": "gemini-2.0-flash",
        "status": "ready" if both else "partial"
    }
