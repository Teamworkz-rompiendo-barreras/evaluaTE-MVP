import sys
import os

# Ensure we can import from backend directory
backend_dir = os.path.join(os.getcwd(), 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

print(f"Checking imports with sys.path: {sys.path}")

try:
    import main
    print("Import main: OK")
except Exception as e:
    print(f"Import main: FAIL {e}")

try:
    import cv_analyzer
    print("Import cv_analyzer: OK")
except Exception as e:
    print(f"Import cv_analyzer: FAIL {e}")

try:
    from pdf_service import create_employability_pdf
    print("Import pdf_service: OK")
except Exception as e:
    print(f"Import pdf_service: FAIL {e}")
