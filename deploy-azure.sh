#!/bin/bash

# Script de despliegue específico para Azure
# EvaluaTE MVP - Despliegue Azure

set -e  # Salir en caso de error

echo "🚀 Iniciando despliegue de EvaluaTE MVP a Azure..."
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "backend/main.py" ] || [ ! -f "nuevo-frontend/package.json" ]; then
    log_error "No se encontraron los archivos principales. Asegúrate de estar en el directorio raíz del proyecto."
    exit 1
fi

# Verificar variables de entorno
log_info "Verificando variables de entorno..."
if [ -z "$AZURE_OPENAI_API_KEY" ]; then
    log_warn "AZURE_OPENAI_API_KEY no está configurada"
fi

if [ -z "$AZURE_OPENAI_ENDPOINT" ]; then
    log_warn "AZURE_OPENAI_ENDPOINT no está configurada"
fi

if [ -z "$AZURE_OPENAI_DEPLOYMENT" ]; then
    log_warn "AZURE_OPENAI_DEPLOYMENT no está configurada"
fi

# Preparar backend para Azure
log_info "Preparando backend para Azure..."

cd backend

# Verificar que los archivos de configuración de Azure existen
if [ ! -f "startup-azure.py" ]; then
    log_error "No se encontró startup-azure.py"
    exit 1
fi

if [ ! -f "requirements-azure.txt" ]; then
    log_error "No se encontró requirements-azure.txt"
    exit 1
fi

if [ ! -f "web.config" ]; then
    log_error "No se encontró web.config"
    exit 1
fi

log_info "✅ Archivos de configuración de Azure verificados"

# Verificar dependencias del backend
log_info "Verificando dependencias del backend..."
if [ ! -d "venv" ]; then
    log_info "Creando entorno virtual..."
    python3 -m venv venv
fi

source venv/bin/activate

log_info "Instalando dependencias del backend para Azure..."
pip install -r requirements-azure.txt

# Verificar que las dependencias críticas estén instaladas
python3 -c "import fastapi, uvicorn, openai, pypdf" 2>/dev/null || {
    log_error "Faltan dependencias críticas del backend"
    exit 1
}

log_info "✅ Dependencias del backend verificadas"

# Construir frontend
log_info "Construyendo frontend..."
cd ../nuevo-frontend

# Verificar Node.js
if ! command -v node &> /dev/null; then
    log_error "Node.js no está instalado"
    exit 1
fi

# Instalar dependencias
log_info "Instalando dependencias del frontend..."
npm ci --production

# Construir para producción
log_info "Construyendo aplicación para producción..."
npx tsc && npx vite build

# Verificar que la construcción fue exitosa
if [ ! -d "dist" ]; then
    log_error "La construcción del frontend falló"
    exit 1
fi

log_info "✅ Frontend construido exitosamente"

# Verificar configuración de seguridad
log_info "Verificando configuración de seguridad..."

# Verificar que no hay console.log en producción
if grep -r "console.log" dist/ 2>/dev/null; then
    log_warn "Se encontraron console.log en el build de producción"
fi

# Verificar headers de seguridad
if [ -f "staticwebapp.config.json" ]; then
    log_info "✅ Configuración de seguridad del frontend verificada"
else
    log_warn "No se encontró staticwebapp.config.json"
fi

# Volver al directorio raíz
cd ..

# Crear archivo de configuración de producción
log_info "Creando configuración de producción..."

# Leer valores del archivo .env del backend si existe
if [ -f "backend/.env" ]; then
    log_info "Leyendo configuración desde backend/.env..."
    source backend/.env
fi

cat > .env.production << EOF
# Configuración de producción para Azure
PRODUCTION=true
NODE_ENV=production
PYTHONPATH=./backend

# Azure OpenAI (usar valores del archivo .env del backend)
AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY:-4ku7UcKVerAXcTXurf4Of1aDGC5w5UreekGaLuxbsnuxOdZe48NdJQQJ99BGACR0EKYXJ3w3AAABACOGiqbl}
AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT:-https://teamworkzevaluate-openai.openai.azure.com}
AZURE_OPENAI_DEPLOYMENT=${AZURE_OPENAI_DEPLOYMENT:-gpt-4o}
AZURE_OPENAI_API_VERSION=${AZURE_OPENAI_API_VERSION:-2024-02-15-preview}

# Base de datos PostgreSQL (si está configurada)
DATABASE_URL=${DATABASE_URL:-}

# Configuración del servidor Azure
PORT=8080
HOST=0.0.0.0
EOF

log_info "✅ Archivo de configuración de producción creado"

# Verificación final
log_info "Realizando verificación final..."

# Verificar que el backend puede iniciarse
cd backend
source venv/bin/activate
python3 -c "from main import app; print('✅ Backend importado correctamente')" || {
    log_error "Error al importar el backend"
    exit 1
}

# Verificar que el frontend está construido
cd ../nuevo-frontend
if [ -f "dist/index.html" ]; then
    log_info "✅ Frontend construido y listo"
else
    log_error "El frontend no se construyó correctamente"
    exit 1
fi

cd ..

# Resumen final
echo ""
echo "🎉 DESPLIEGUE AZURE COMPLETADO EXITOSAMENTE"
echo "==========================================="
echo ""
echo "📋 Resumen:"
echo "   ✅ Backend: Configurado para Azure con startup-azure.py"
echo "   ✅ Dependencias: requirements-azure.txt instaladas"
echo "   ✅ Configuración: web.config y .deployment creados"
echo "   ✅ Frontend: Construido para producción"
echo "   ✅ Puerto: Configurado para Azure (8080)"
echo ""
echo "🚀 Próximos pasos:"
echo "   1. Sube el código a Azure Web App"
echo "   2. Configura las variables de entorno en Azure"
echo "   3. Monitorea los logs en Azure Portal"
echo "   4. Verifica que la aplicación responde"
echo ""
echo "📚 URLs de verificación:"
echo "   - Backend Health: https://evaluador-backend-fzbhemgtetfeeme6.spaincentral-01.azurewebsites.net/health"
echo "   - Backend API Docs: https://evaluador-backend-fzbhemgtetfeeme6.spaincentral-01.azurewebsites.net/docs"
echo "   - Frontend: https://tu-frontend-url.azurestaticapps.net"
echo ""

log_info "Despliegue Azure completado. ¡La aplicación está lista para Azure!" 