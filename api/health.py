"""Direct handler for /api/health endpoint."""
import sys
import os
import json
import traceback

# Setup paths
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "backend"))

from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status_info = {
            "status": "ok",
            "service": "EvaluaTE Backend",
            "runtime": "vercel-python",
        }
        
        # Try to check if backend.main can be imported
        try:
            from backend.main import app, APP_VERSION
            status_info["fastapi"] = "loaded"
            status_info["version"] = APP_VERSION
        except Exception as e:
            status_info["fastapi"] = "error"
            status_info["error"] = str(e)
            status_info["traceback"] = traceback.format_exc()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status_info, indent=2).encode())
