import sys
import os

# Setup paths for Vercel
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from backend.main import app
except ImportError:
    # If the above fails, maybe we are running in an environment where backend is already in path
    # or should be imported differently
    import backend.main as backend_main
    app = backend_main.app

# Vercel entry point
# This file handles /api/analyze requests
