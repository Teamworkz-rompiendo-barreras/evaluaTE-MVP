#!/bin/bash
# Script para iniciar el backend con entorno virtual

set -e

echo "🚀 Iniciando EvaluaTE Backend con entorno virtual..."

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ]; then
    echo "❌ Error: No se encontró main.py. Asegúrate de estar en el directorio del backend."
    exit 1
fi

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "❌ Error: No se encontró el entorno virtual 'venv'"
    echo "💡 Ejecuta: python3 -m venv venv"
    exit 1
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Verificar que el entorno virtual esté activado
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Error: No se pudo activar el entorno virtual"
    exit 1
fi

echo "✅ Entorno virtual activado: $VIRTUAL_ENV"

# Ejecutar el startup
echo "🚀 Ejecutando startup..."
python3 startup-azure.py 