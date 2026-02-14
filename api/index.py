from fastapi import FastAPI, Request
import os
import sys

# Setup paths
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

app = FastAPI()

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "debug": "index.py reached",
        "root_dir": root_dir,
        "sys_path": sys.path[:5]
    }

@app.post("/api/analyze")
async def analyze_proxy(request: Request):
    # Try to import real app later
    try:
        from backend.main import app as real_app
        # This is a bit hacky for a proxy, but let's see if we can just import
        return {"status": "backend_imported"}
    except Exception as e:
        return {"error": str(e)}

@app.api_route("/api/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(request: Request, path_name: str):
    return {
        "message": "Catch-all reached",
        "path": path_name,
        "method": request.method
    }
