#!/usr/bin/env python3
import os
import subprocess
import sys
import time


def log(level: str, msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{ts} - {level} - {msg}")
    sys.stdout.flush()


def ensure_utf8() -> None:
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("LC_ALL", "C.UTF-8")
    os.environ.setdefault("LANG", "C.UTF-8")
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def install_requirements() -> None:
    req_file_candidates = [
        os.path.join(os.getcwd(), "requirements-azure.txt"),
        os.path.join(os.getcwd(), "requirements.txt"),
    ]
    req_file = next((p for p in req_file_candidates if os.path.exists(p)), None)
    if not req_file:
        log("WARN", "No se encontró requirements*.txt; se continúa sin instalar dependencias")
        return
    log("INFO", f"📦 Instalando dependencias desde: {os.path.basename(req_file)}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "-r", req_file])
        log("INFO", "✅ Dependencias instaladas correctamente")
    except subprocess.CalledProcessError as e:
        log("ERROR", f"Falló la instalación de dependencias: {e}")
        # Continuar para permitir arranque si ya estaban instaladas


def run_uvicorn() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = os.getenv("PORT", "8080")
    app_path = os.getenv("APP", "main:app")
    log("INFO", f"🚀 Iniciando Uvicorn {app_path} en {host}:{port}")
    os.execvp(sys.executable, [sys.executable, "-m", "uvicorn", app_path, "--host", host, "--port", port])


def main() -> None:
    log("INFO", "🚀 Iniciando EvaluaTE Backend en Azure...")
    ensure_utf8()
    # Limpia posibles proxies heredados
    for var in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
        if var in os.environ:
            del os.environ[var]
    log("INFO", "🔧 Verificando/instalando dependencias...")
    install_requirements()
    log("INFO", "✅ Configuración verificada")
    run_uvicorn()


if __name__ == "__main__":
    main()


