#!/usr/bin/env python3
import os
import subprocess
import sys
import time
import shutil


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


VENV_DIR = os.environ.get("PERSISTENT_VENV_DIR", "/home/venv-evaluate")
VENV_BIN = os.path.join(VENV_DIR, "Scripts" if os.name == "nt" else "bin")
VENV_PY = os.path.join(VENV_BIN, "python")
DEPS_MARKER = os.path.join(os.getcwd(), ".venv_ready")

def _detect_requirements_path() -> str | None:
    candidates = [
        os.path.join(os.getcwd(), "requirements-azure.txt"),
        os.path.join(os.getcwd(), "requirements.txt"),
    ]
    return next((p for p in candidates if os.path.exists(p)), None)

def install_requirements() -> None:
    if os.environ.get("SKIP_PIP_ON_START", "").lower() in ("1", "true", "yes"):
        log("INFO", "⏭️  SKIP_PIP_ON_START=1, saltando instalación de dependencias")
        return

    req_file = _detect_requirements_path()
    if not req_file:
        log("WARN", "No se encontró requirements*.txt; se continúa sin instalar dependencias")
        return

    # Si ya existe un entorno y marcador, no reinstalar
    if os.path.exists(VENV_PY) and os.path.exists(DEPS_MARKER):
        log("INFO", f"🔁 Reutilizando entorno virtual en {VENV_DIR}")
        return

    try:
        if not os.path.exists(VENV_PY):
            log("INFO", f"🧰 Creando entorno virtual persistente en {VENV_DIR}...")
            # Crear directorio contenedor si no existe
            os.makedirs(VENV_DIR, exist_ok=True)
            subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
        # Actualizar pip e instalar deps
        log("INFO", f"📦 Instalando dependencias desde: {os.path.basename(req_file)}")
        subprocess.check_call([VENV_PY, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])  # pragma: no cover
        subprocess.check_call([VENV_PY, "-m", "pip", "install", "--disable-pip-version-check", "-r", req_file])
        # Crear marcador
        try:
            with open(DEPS_MARKER, "w", encoding="utf-8") as f:
                f.write(time.strftime("%Y-%m-%d %H:%M:%S"))
        except Exception:
            pass
        log("INFO", "✅ Dependencias instaladas/reutilizadas correctamente")
    except subprocess.CalledProcessError as e:
        log("ERROR", f"Falló la instalación de dependencias: {e}")
        # Continuar para permitir arranque si ya estaban instaladas


def run_uvicorn() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = os.getenv("PORT", "8080")
    app_path = os.getenv("APP", "main:app")
    # Si existe venv, usar su intérprete para cargar dependencias persistidas
    python_exec = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    if python_exec != sys.executable:
        log("INFO", f"🚀 Iniciando con entorno virtual: {python_exec}")
    log("INFO", f"🚀 Iniciando Uvicorn {app_path} en {host}:{port}")
    os.execvp(python_exec, [python_exec, "-m", "uvicorn", app_path, "--host", host, "--port", port])


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


