#!/bin/bash

# Script de despliegue para Azure Web App
# Este script prepara el backend para el despliegue en Azure

set -e

echo "🚀 Preparando despliegue del backend para Azure Web App..."

# Verificar que estamos en el directorio correcto
if [ ! -d "backend" ]; then
    echo "❌ Error: No se encontró el directorio 'backend'"
    exit 1
fi

cd backend

# Limpiar archivos temporales y cachés
echo "🧹 Limpiando archivos temporales..."
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete
find . -type d -name "venv" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".venv" -exec rm -rf {} + 2>/dev/null || true

# Verificar que los archivos de configuración existen
echo "✅ Verificando archivos de configuración..."
required_files=(
    "main.py"
    "startup-azure.py"
    "azure-app-service-config.py"
    "requirements-azure.txt"
    ".deployment"
    "deploy-config.json"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Error: No se encontró el archivo requerido: $file"
        exit 1
    fi
    echo "  ✓ $file"
done

# Crear archivo de configuración para Azure
echo "📝 Creando archivo de configuración para Azure..."
cat > .azure-deployment << EOF
# Configuración de despliegue para Azure Web App
# Este archivo es leído por Azure durante el despliegue

[config]
command = python azure-app-service-config.py
EOF

# Crear archivo startup.txt para Azure
echo "📝 Creando archivo startup.txt para Azure..."
cat > startup.txt << EOF
python azure-app-service-config.py
EOF

# Verificar que la aplicación se puede importar
echo "🔍 Verificando que la aplicación se puede importar..."
python -c "
import sys
sys.path.insert(0, '.')
try:
    from main import app
    print('✅ Aplicación FastAPI importada correctamente')
    print(f'   - App: {app}')
    print(f'   - Título: {app.title}')
    print(f'   - Versión: {app.version}')
except Exception as e:
    print(f'❌ Error importando la aplicación: {e}')
    sys.exit(1)
"

# Crear archivo de configuración para Azure App Service
echo "📝 Creando configuración para Azure App Service..."
cat > azure-app-service-config.py << 'EOF'
#!/usr/bin/env python3
"""
Configuración específica para Azure App Service
Este archivo se ejecuta cuando Azure inicia la aplicación
"""
import os
import sys
from pathlib import Path

# Configurar el path de Python
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configurar variables de entorno para Azure
os.environ.setdefault("HOST", "0.0.0.0")
os.environ.setdefault("PORT", "8000")
os.environ.setdefault("LOG_LEVEL", "INFO")

# Importar la aplicación FastAPI
from main import app

# Para Azure App Service, necesitamos exportar la app
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
EOF

# Crear archivo de configuración para Azure
echo "📝 Creando archivo de configuración para Azure..."
cat > azure.yaml << EOF
language: python
buildCommands:
  - pip install -r requirements-azure.txt
startupCommand: python azure-app-service-config.py
EOF

# Crear archivo web.config para Azure
echo "📝 Creando archivo web.config para Azure..."
cat > web.config << EOF
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="httpPlatformHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified" />
    </handlers>
    <httpPlatform processPath="%home%\site\wwwroot\env\Scripts\python.exe"
                  arguments="%home%\site\wwwroot\azure-app-service-config.py"
                  stdoutLogEnabled="true"
                  stdoutLogFile="%home%\LogFiles\stdout"
                  startupTimeLimit="60">
      <environmentVariables>
        <environmentVariable name="PORT" value="%HTTP_PLATFORM_PORT%" />
        <environmentVariable name="HOST" value="0.0.0.0" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>
EOF

# Crear archivo de configuración para el despliegue
echo "📝 Creando archivo de configuración para el despliegue..."
cat > deploy-config.json << EOF
{
  "language": "python",
  "buildCommands": [
    "pip install -r requirements-azure.txt"
  ],
  "startupCommand": "python azure-app-service-config.py",
  "pythonVersion": "3.11",
  "deploymentTarget": "Azure Web App",
  "framework": "FastAPI",
  "entryPoint": "azure-app-service-config.py"
}
EOF

# Crear archivo .deployment
echo "📝 Creando archivo .deployment..."
cat > .deployment << EOF
[config]
command = python azure-app-service-config.py
EOF

# Crear archivo startup.txt
echo "📝 Creando archivo startup.txt..."
cat > startup.txt << EOF
python azure-app-service-config.py
EOF

# Crear archivo de configuración para Azure
echo "📝 Creando archivo de configuración para Azure..."
cat > azure-deployment-config.txt << EOF
# Configuración de despliegue para Azure Web App
# Archivos principales:
# - azure-app-service-config.py: Punto de entrada principal
# - main.py: Aplicación FastAPI
# - requirements-azure.txt: Dependencias
# - .deployment: Comando de inicio
# - startup.txt: Comando de inicio alternativo
# - web.config: Configuración de IIS (si es necesario)
# - azure.yaml: Configuración de Azure

# Comando de inicio: python azure-app-service-config.py
# Puerto por defecto: 8000
# Host por defecto: 0.0.0.0
EOF

echo "✅ Configuración completada. Archivos creados:"
ls -la *.py *.txt *.json *.yaml *.config .deployment 2>/dev/null || true

echo ""
echo "🚀 El backend está listo para el despliegue en Azure Web App"
echo "📋 Archivos de configuración creados:"
echo "   - azure-app-service-config.py (punto de entrada principal)"
echo "   - .deployment (comando de inicio)"
echo "   - startup.txt (comando de inicio alternativo)"
echo "   - web.config (configuración de IIS)"
echo "   - azure.yaml (configuración de Azure)"
echo "   - deploy-config.json (configuración del despliegue)"
echo ""
echo "💡 Para desplegar, sube estos archivos a Azure Web App"
echo "   o usa el workflow de GitHub Actions existente"
