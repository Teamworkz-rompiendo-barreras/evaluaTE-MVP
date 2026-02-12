import sys
import os
import traceback

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

try:
    from backend.main import app
except Exception as e:
    # If import fails, create a minimal ASGI app that returns the error
    from fastapi import FastAPI
    app = FastAPI()
    
    error_detail = {
        "error": str(e),
        "type": type(e).__name__,
        "traceback": traceback.format_exc()
    }
    
    @app.get("/api/health")
    async def health():
        return {"status": "error", "detail": error_detail}
    
    @app.get("/api/{path:path}")
    async def catch_all(path: str):
        return {"status": "error", "detail": error_detail}
