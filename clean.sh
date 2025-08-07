#!/bin/bash

# Script de limpieza profesional para EvaluaTE MVP
# Elimina archivos temporales, cachés y archivos innecesarios

echo "🧹 Iniciando limpieza profesional del proyecto..."

# Eliminar archivos de caché de Python
echo "📦 Eliminando cachés de Python..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Eliminar entornos virtuales
echo "🐍 Eliminando entornos virtuales..."
rm -rf .venv/ backend/venv/ 2>/dev/null || true

# Eliminar node_modules y archivos de compilación
echo "📦 Eliminando node_modules y archivos de compilación..."
rm -rf nuevo-frontend/node_modules/ nuevo-frontend/dist/ nuevo-frontend/coverage/ 2>/dev/null || true

# Eliminar archivos de prueba temporales
echo "🧪 Eliminando archivos de prueba temporales..."
rm -f test-*.py test-*.js test-*.json resultado-*.json diagnostico-*.json informe-*.json 2>/dev/null || true

# Eliminar archivos de sistema
echo "💻 Eliminando archivos de sistema..."
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "Thumbs.db" -delete 2>/dev/null || true
find . -name "*.log" -delete 2>/dev/null || true

# Eliminar archivos temporales específicos
echo "🗑️ Eliminando archivos temporales..."
rm -f *-la* *status* *.sh 2>/dev/null || true
rm -f *.md 2>/dev/null || true

# Recrear README.md
echo "📝 Recreando README.md..."
cat > README.md << 'EOF'
# EvaluaTE MVP

Aplicación de evaluación de currículums vitae utilizando inteligencia artificial.

## Estructura del Proyecto

- `backend/` - API REST en Python con FastAPI
- `nuevo-frontend/` - Frontend en React/TypeScript

## Instalación

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend
```bash
cd nuevo-frontend
npm install
```

## Desarrollo

### Backend
```bash
cd backend
python main.py
```

### Frontend
```bash
cd nuevo-frontend
npm run dev
```

## Despliegue

El proyecto está configurado para desplegarse en Azure.
EOF

echo "✅ Limpieza completada exitosamente!"
echo "📊 Espacio liberado en el proyecto"
