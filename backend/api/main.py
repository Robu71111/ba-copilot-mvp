"""
BA Copilot - FastAPI Backend
=============================
Main application entry point for the FastAPI backend.

This serves as the API layer between React frontend and AI services.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.api.routes import projects, requirements, stories, criteria
from backend.core.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="BA Copilot API",
    description="AI-powered assistant for Business Analysts",
    version="1.0.0"
)

# CORS configuration - Allow frontend to call API
# CORS configuration - Allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ========================================
# HEALTH CHECK ENDPOINTS
# ========================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "BA Copilot API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "BA Copilot API is running"
    }


@app.get("/api/health/apis")
async def check_apis():
    """Check status of external APIs"""
    from backend.core.config import APIConfig
    
    status = APIConfig.get_status()
    
    return {
        "status": status["status"],
        "apis": {
            "gemini": status["gemini"][0],
            "audio": status["audio"][0]
        }
    }

# ========================================
# INCLUDE ROUTERS
# ========================================

# Project management routes
app.include_router(
    projects.router,
    prefix="/api/projects",
    tags=["projects"]
)

# Input handling routes
from backend.api.routes import input as input_routes
app.include_router(
    input_routes.router,
    prefix="/api/input",
    tags=["input"]
)

# Requirements extraction routes
app.include_router(
    requirements.router,
    prefix="/api/requirements",
    tags=["requirements"]
)

# User stories generation routes
app.include_router(
    stories.router,
    prefix="/api/stories",
    tags=["stories"]
)

# Acceptance criteria generation routes
app.include_router(
    criteria.router,
    prefix="/api/criteria",
    tags=["criteria"]
)

# Audio routes
from backend.api.routes import audio
app.include_router(
    audio.router,
    prefix="/api/audio",
    tags=["audio"]
)

# ========================================
# ERROR HANDLERS
# ========================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


# ========================================
# STARTUP EVENT
# ========================================

@app.on_event("startup")
async def startup_event():
    """Initialize database and check API keys on startup"""
    print(">>> BA Copilot API starting...")
    
    # Initialize database
    from backend.core.database import db
    print("[OK] Database initialized")
    
    # Check API configuration
    from backend.core.config import APIConfig
    status = APIConfig.get_status()
    
    # Check Gemini APIs
    if status["gemini"][0]:
        print("[OK] Gemini API configured")
    else:
        print("[WARNING] Main Gemini API not configured")
    
    if status["audio"][0]:
        print("[OK] Audio API configured")
    else:
        print("[WARNING] Audio API not configured")
    
    if status["status"] == "connected":
        print(">>> BA Copilot API ready! ✅")
    else:
        print(">>> BA Copilot API started with warnings ⚠️")