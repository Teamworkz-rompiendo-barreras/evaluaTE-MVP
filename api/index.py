import sys
import os
import json
import traceback

# Add backend directory to Python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "backend"))

startup_error = None

try:
    from backend.main import app
except Exception as e:
    startup_error = {
        "error": str(e),
        "type": type(e).__name__,
        "traceback": traceback.format_exc()
    }
    
    # Fallback: create minimal handler using stdlib only
    # (FastAPI import may also fail if the error is in a shared dependency)
    from http.server import BaseHTTPRequestHandler
    
    class handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "startup_error",
                "detail": startup_error
            }, indent=2).encode())
        
        def do_POST(self):
            self.do_GET()
