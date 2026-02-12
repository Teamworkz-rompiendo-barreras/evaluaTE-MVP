import sys
import os

# Setup paths for Vercel
# Note: For nested files like api/report/generate.py, root_dir is 3 levels up?
# os.path.dirname(os.path.abspath(__file__)) is .../api/report
# dirname(...) is .../api
# dirname(...) is .../ (root)
current_dir = os.path.dirname(os.path.abspath(__file__))
api_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(api_dir)

sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "backend"))

from backend.main import app

# Vercel entry point
# This file handles /api/report/generate requests
