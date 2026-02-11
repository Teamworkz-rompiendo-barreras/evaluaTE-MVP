try:
    import fastapi
    print("fastapi: OK")
except ImportError as e:
    print(f"fastapi: MISSING ({e})")

try:
    import supabase
    print("supabase: OK")
except ImportError as e:
    print(f"supabase: MISSING ({e})")
