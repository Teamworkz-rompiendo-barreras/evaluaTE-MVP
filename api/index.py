import os
import sys
import traceback

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

_import_error = None
try:
    from backend.main import app  # noqa: E402
except Exception as _e:
    _import_error = f"{type(_e).__name__}: {_e}\n{traceback.format_exc()}"

if _import_error:
    from fastapi import FastAPI
    from fastapi.responses import PlainTextResponse
    app = FastAPI()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    async def error_handler(path: str):
        return PlainTextResponse(_import_error, status_code=500)
