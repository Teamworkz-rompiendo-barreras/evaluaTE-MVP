#!/bin/bash

# Script para activar el entorno virtual y ejecutar la aplicación
# Uso: source activate_venv.sh

echo "Activando entorno virtual..."
source venv/bin/activate

echo "Verificando dependencias..."
python -c "import fastapi, openai, pypdf, uvicorn, pydantic; print('✓ Todas las dependencias están instaladas')"

echo "Entorno virtual activado. Puedes ejecutar:"
echo "  python main.py"
echo "  uvicorn main:app --reload"
echo ""
echo "Para desactivar el entorno virtual, ejecuta: deactivate" 