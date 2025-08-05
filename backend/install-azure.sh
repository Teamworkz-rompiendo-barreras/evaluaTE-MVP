#!/bin/bash
# Script de instalación para Azure Web App

set -e

echo "🚀 Iniciando instalación para Azure Web App..."

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ]; then
    echo "❌ Error: No se encontró main.py. Asegúrate de estar en el directorio del backend."
    exit 1
fi

# Actualizar pip
echo "📦 Actualizando pip..."
python3 -m pip install --upgrade pip

# Instalar dependencias
echo "📦 Instalando dependencias..."
if [ -f "requirements-azure.txt" ]; then
    echo "📋 Usando requirements-azure.txt"
    python3 -m pip install -r requirements-azure.txt
else
    echo "📋 Usando requirements.txt"
    python3 -m pip install -r requirements.txt
fi

# Verificar instalación
echo "🧪 Verificando instalación..."
python3 test-setup.py

echo "✅ Instalación completada exitosamente"
echo "🚀 El backend está listo para funcionar en Azure" 