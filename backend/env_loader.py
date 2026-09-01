import os
from pathlib import Path
from dotenv import load_dotenv


def get_gemini_api_keys() -> list[str]:
    """Devuelve las claves de Gemini en orden de prioridad para rotación."""
    keys = []
    for key_name in ["GOOGLE_API_KEY", "GEMINI_API_KEY", "GEMINI_KEY_1", "GEMINI_KEY_2"]:
        value = (os.getenv(key_name) or "").strip()
        if value and value not in keys:
            keys.append(value)
    return keys


def load_backend_env() -> str | None:
    """Carga el .env correcto para el backend y normaliza la prioridad de las claves de Gemini."""
    backend_dir = Path(__file__).resolve().parent
    project_root = backend_dir.parent
    candidates = [project_root / ".env", backend_dir / ".env"]

    resolved = None
    for env_path in candidates:
        if env_path.exists():
            load_dotenv(env_path, override=False)
            resolved = str(env_path)

    keys = get_gemini_api_keys()
    if keys:
        primary = keys[0]
        secondary = keys[1] if len(keys) > 1 else keys[0]
        os.environ["GEMINI_API_KEY"] = primary
        os.environ["GOOGLE_API_KEY"] = primary
        os.environ["GEMINI_KEY_1"] = primary
        os.environ["GEMINI_KEY_2"] = secondary

    os.environ.setdefault("GEMINI_API_VERSION", "v1beta")
    return resolved
