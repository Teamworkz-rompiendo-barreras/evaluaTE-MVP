from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import sys
import traceback

# Setup root directory for imports
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

#app = FastAPI()

# Global error storage for debug
init_error = None
try:
    from backend.main import app as backend_app
    # If we got here, backend_app is loaded
    # Instead of replacing global 'app', we can delegate
except Exception as e:
    init_error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
    #backend_app = None
    app = FastAPI()

    @app.get("/api/debug/init_error")
    async def debug_init_error():
        return {
            "ok": False,
            "error": init_error
        }

@app.get("/api/health")
async def health():
    if init_error:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Backend failed to initialize",
                "error": init_error
            }
        )
    return {
        "status": "ok",
        "service": "unified-router",
        "backend": "loaded"
    }

@app.api_route("/api/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(request: Request, path_name: str):
    if backend_app:
        # Simple delegation
        # Note: This is simplified, real mounting might be better
        # but let's see if we can at least reach this point
        return {
            "message": "Backend loaded, but route not found in index.py",
            "requested_path": path_name,
            "method": request.method
        }
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": init_error or "Backend not loaded"
        }
    )

# If backend loaded successfully, we can actually mount it or use it
if backend_app:
    # Mount the backend app under /api if needed, or just use it as the main app
    # But Vercel wants 'app' to be the entry point.
    app = backend_app
