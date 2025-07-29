#!/bin/bash

# Script para activar automáticamente el entorno correcto
echo "🚀 Activando entorno de EvaluaTE..."

# Verificar si estamos en el directorio correcto
if [ ! -f "backend/main.py" ]; then
    echo "❌ Error: No estás en el directorio raíz de EvaluaTE"
    echo "   Navega al directorio del proyecto y ejecuta este script"
    exit 1
fi

# Activar entorno virtual del backend
if [ -d "backend/venv" ]; then
    echo "✅ Activando entorno virtual del backend..."
    source backend/venv/bin/activate
    echo "🎉 Entorno activado. Ahora puedes ejecutar:"
    echo "   python backend/main.py"
    echo "   uvicorn backend.main:app --reload"
else
    echo "❌ Entorno virtual no encontrado. Ejecuta:"
    echo "   ./fix_dependencies.sh"
fi
