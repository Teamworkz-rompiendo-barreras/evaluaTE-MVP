try:
    import fastapi
    print("fastapi: OK")
except ImportError as e:
    print(f"fastapi: MISSING ({e})")

try:
    import google.generativeai
    print("google.generativeai: OK")
except ImportError as e:
    print(f"google.generativeai: MISSING ({e})")

try:
    import supabase
    print("supabase: OK")
except ImportError as e:
    print(f"supabase: MISSING ({e})")

try:
    import uvicorn
    print("uvicorn: OK")
except ImportError as e:
    print(f"uvicorn: MISSING ({e})")
