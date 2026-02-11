import sys
try:
    import fastapi
    import uvicorn
    import google.generativeai
    print("SUCCESS: All critical packages imported.")
except ImportError as e:
    print(f"FAILURE: Could not import {e.name}")
    sys.exit(1)
