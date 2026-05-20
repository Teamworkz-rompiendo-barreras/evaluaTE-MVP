
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

print("Attempting to import backend.main...")
try:
    from backend.main import app
    print("Successfully imported backend.main.app")
except Exception as e:
    print(f"FAILED to import backend.main: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Startup check passed.")
