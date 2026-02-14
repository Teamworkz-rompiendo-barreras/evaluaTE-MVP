import sys
import os

# Setup root directory for imports
# os.path.dirname(os.path.abspath(__file__)) is the 'api' directory
# The parent is the root of the project
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from backend.main import app
except ImportError:
    # Fallback to backend direct import if needed
    import backend.main as backend_main
    app = backend_main.app

# Vercel expects a module-level variable named 'app'
# This file serves as the single entry point for all /api requests
