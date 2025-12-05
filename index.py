"""
Vercel Entry Point for BA Copilot API
"""
import sys
import os
from pathlib import Path
import traceback

# Get the root directory
root_dir = Path(__file__).parent

# Add to Python path
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "backend"))

print(f"Root directory: {root_dir}")
print(f"Python path: {sys.path[:3]}")

# Import and create app
try:
    # Try importing the main module
    print("Attempting to import backend.api.main...")
    from backend.api import main as main_module
    app = main_module.app
    print("✅ Successfully imported FastAPI app")
    
except Exception as e:
    print(f"❌ Failed to import: {e}")
    traceback.print_exc()
    
    # Create fallback app that shows the error
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="BA Copilot API - Error State")
    
    error_details = {
        "error": "Failed to import main application",
        "exception": str(e),
        "traceback": traceback.format_exc(),
        "python_path": sys.path[:5],
        "root_dir": str(root_dir),
        "files_in_root": [str(f) for f in root_dir.iterdir()][:10]
    }
    
    @app.get("/")
    @app.get("/api/health")
    async def error_info():
        return JSONResponse(
            status_code=500,
            content=error_details
        )
    
    print("Created fallback error app")

# Mangum handler for Vercel
from mangum import Mangum
handler = Mangum(app, lifespan="off")

print("✅ Handler created successfully")