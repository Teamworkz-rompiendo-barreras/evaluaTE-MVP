import sys
import os

# Setup paths for Vercel
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "backend"))

from backend.main import app

# Vercel entry point
# This file handles /api/analyze requests
