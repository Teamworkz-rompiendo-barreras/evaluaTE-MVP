import sys
import os

# Setup paths for Vercel
# .../api/debug/cv_data.py
current_dir = os.path.dirname(os.path.abspath(__file__))
api_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(api_dir)

sys.path.insert(0, root_dir)

# type: ignore
from backend.main import app

# Vercel entry point
# This file handles /api/debug/cv_data requests
