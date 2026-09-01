import os
from pathlib import Path


def test_load_backend_env_reads_backend_dotenv(tmp_path, monkeypatch):
    project_root = tmp_path / "project"
    backend_dir = project_root / "backend"
    backend_dir.mkdir(parents=True)

    env_file = backend_dir / ".env"
    env_file.write_text(
        "GEMINI_KEY_1=test_key_from_backend_env\n"
        "GEMINI_API_VERSION=v1beta\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(project_root)
    for key in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_KEY_1", "GEMINI_API_VERSION"]:
        monkeypatch.delenv(key, raising=False)

    import importlib

    from backend.env_loader import load_backend_env

    load_backend_env()

    assert os.getenv("GEMINI_API_KEY") == "test_key_from_backend_env"
    assert os.getenv("GOOGLE_API_KEY") == "test_key_from_backend_env"
    assert os.getenv("GEMINI_KEY_1") == "test_key_from_backend_env"
    assert os.getenv("GEMINI_API_VERSION") == "v1beta"
