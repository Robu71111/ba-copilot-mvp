"""
Backend Configuration
=====================
Configuration settings for FastAPI backend and API keys.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from root .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings"""
    PROJECT_NAME = "BA Copilot"
    VERSION = "1.0.0"
    API_PREFIX = "/api"


class APIConfig:
    """API keys and external service configuration"""
    
    # ========================================
    # 🔑 MAIN GEMINI API KEY (REQUIRED)
    # ========================================
    # This key is for: Transcription, Requirements, Stories, Criteria
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # ========================================
    # 🎤 AUDIO GEMINI API KEY (REQUIRED)
    # ========================================
    # This key is for: Audio recording/generation
    GEMINI_AUDIO_API_KEY = os.getenv('GEMINI_AUDIO_API_KEY')
    
    # Main model for transcription, requirements, stories, criteria
    GEMINI_MODEL = "gemini-2.5-flash"
    
    # Audio model for real-time recording
    GEMINI_AUDIO_MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"
    
    GEMINI_CONFIG = {
        "temperature": 0.7,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 2048,
    }
    
    # Audio-specific config
    AUDIO_CONFIG = {
        "sample_rate": 16000,
        "channels": 1,
        "format": "wav"
    }
    
    # ========================================
    # DATABASE CONFIGURATION
    # ========================================
    DATABASE_PATH = os.getenv('DATABASE_PATH', "database/ba_copilot.db")
    
    # ========================================
    # VALIDATION METHODS
    # ========================================
    @staticmethod
    def validate_gemini_api():
        """Check if Main Gemini API key is configured"""
        if not APIConfig.GEMINI_API_KEY:
            return False, "⚠️ Main Gemini API key not configured"
        return True, "✅ Gemini API configured"
    
    @staticmethod
    def validate_audio_api():
        """Check if Audio Gemini API key is configured"""
        if not APIConfig.GEMINI_AUDIO_API_KEY:
            return False, "⚠️ Audio Gemini API key not configured"
        return True, "✅ Audio API configured"
    
    @staticmethod
    def get_status():
        """Get configuration status"""
        gemini_status = APIConfig.validate_gemini_api()
        audio_status = APIConfig.validate_audio_api()
        
        # Return overall API health
        all_configured = gemini_status[0] and audio_status[0]
        
        return {
            "status": "connected" if all_configured else "error",
            "gemini": gemini_status,
            "audio": audio_status
        }


# Initialize settings
settings = Settings()