"""
Vercel serverless function handler for EvaluaTE API.
Uses WSGI-compatible BaseHTTPRequestHandler as the entry point.
FastAPI app routes are handled internally.
"""
import sys
import os
import json
import traceback

# Setup paths
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "backend"))

_app = None
_error = None

try:
    from backend.main import app as _app
except Exception as e:
    _error = {
        "error": str(e),
        "type": type(e).__name__,
        "traceback": traceback.format_exc()
    }

# Export for Vercel ASGI detection
app = _app

# Also provide WSGI handler as fallback
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if _error:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "startup_error",
                "detail": _error
            }, indent=2).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "message": "EvaluaTE API handler loaded (WSGI mode)",
                "note": "Use /api/health for FastAPI health check"
            }).encode())

    def do_POST(self):
        self.do_GET()
