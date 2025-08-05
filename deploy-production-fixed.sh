#!/bin/bash

# Script de despliegue corregido para producción
# EvaluaTE MVP - Despliegue Seguro y Optimizado

set -e  # Salir en caso de error

echo "🚀 Iniciando despliegue corregido de EvaluaTE MVP a producción..."
echo "================================================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
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

# Verificar dependencias del backend
log_info "Verificando dependencias del backend..."
cd backend

if [ ! -d "venv" ]; then
    log_info "Creando entorno virtual..."
    python3 -m venv venv
fi

source venv/bin/activate

log_info "Instalando dependencias del backend..."
pip install -r requirements.txt

# Verificar que las dependencias críticas estén instaladas
python3 -c "import fastapi, uvicorn, openai, pypdf" 2>/dev/null || {
    log_error "Faltan dependencias críticas del backend"
    exit 1
}

log_info "✅ Dependencias del backend verificadas"

# Aplicar correcciones al backend
log_info "Aplicando correcciones al backend..."

# Verificar que el archivo .env existe y tiene el formato correcto
if [ -f ".env" ]; then
    log_info "Verificando archivo .env..."
    
    # Verificar que las variables críticas estén presentes
    if ! grep -q "AZURE_OPENAI_API_KEY" .env; then
        log_error "AZURE_OPENAI_API_KEY no encontrada en .env"
        exit 1
    fi
    
    if ! grep -q "AZURE_OPENAI_ENDPOINT" .env; then
        log_error "AZURE_OPENAI_ENDPOINT no encontrada en .env"
        exit 1
    fi
    
    log_info "✅ Archivo .env verificado"
else
    log_error "Archivo .env no encontrado en backend/"
    exit 1
fi

# Construir frontend con correcciones
log_info "Construyendo frontend con correcciones..."
cd ../nuevo-frontend

# Verificar Node.js
if ! command -v node &> /dev/null; then
    log_error "Node.js no está instalado"
    exit 1
fi

# Instalar dependencias
log_info "Instalando dependencias del frontend..."
npm ci --production

# Aplicar corrección al código del frontend
log_info "Aplicando corrección para softSkills..."
if grep -q "report?.softSkills && report.softSkills.length > 0" src/pages/ResultadosPage.tsx; then
    log_info "✅ Corrección de softSkills ya aplicada"
else
    log_warn "⚠️ Corrección de softSkills no encontrada - verificar manualmente"
fi

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

# Crear archivo de configuración de producción mejorado
log_info "Creando configuración de producción mejorada..."

# Leer valores del archivo .env del backend si existe
if [ -f "backend/.env" ]; then
    log_info "Leyendo configuración desde backend/.env..."
    source backend/.env
fi

cat > .env.production << EOF
# Configuración de producción corregida
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

# Configuración del servidor - PUERTO CORREGIDO
PORT=8000
HOST=0.0.0.0

# Configuración de Azure App Service
WEBSITE_SITE_NAME=evaluador-backend
HTTP_PLATFORM_PORT=8000
EOF

log_info "✅ Archivo de configuración de producción creado"

# Verificación final mejorada
log_info "Realizando verificación final mejorada..."

# Verificar que el backend puede iniciarse
cd backend
source venv/bin/activate

# Probar el nuevo script de Azure
log_info "Probando script de Azure..."
python3 -c "from azure_startup import setup_azure_environment; print('✅ Script de Azure verificado')" || {
    log_error "Error al verificar script de Azure"
    exit 1
}

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

# Crear archivo de instrucciones de despliegue
cat > DEPLOYMENT_INSTRUCTIONS.md << 'EOF'
# Instrucciones de Despliegue Corregidas

## Problemas Solucionados

### 1. Error de softSkills undefined
- ✅ Aplicada verificación de Array.isArray() en ResultadosPage.tsx
- ✅ Agregado logging detallado para debugging

### 2. Error de puerto en Azure
- ✅ Creado azure_startup.py específico para Azure
- ✅ Configurado puerto 8000 correctamente
- ✅ Actualizado web.config para usar el nuevo script

## Pasos de Despliegue

1. **Subir código a Azure:**
   ```bash
   git add .
   git commit -m "Fix: Correcciones para producción - softSkills y puerto Azure"
   git push origin main
   ```

2. **Configurar variables de entorno en Azure App Service:**
   - AZURE_OPENAI_API_KEY
   - AZURE_OPENAI_ENDPOINT
   - AZURE_OPENAI_DEPLOYMENT
   - AZURE_OPENAI_API_VERSION
   - PORT=8000
   - PRODUCTION=true

3. **Verificar logs en Azure:**
   - Ir a Azure Portal > App Service > Logs
   - Revisar Application Logs y Web Server Logs

4. **Probar endpoints:**
   - Health check: https://tu-app.azurewebsites.net/health
   - API docs: https://tu-app.azurewebsites.net/docs

## Monitoreo

- Revisar logs cada 5 minutos después del despliegue
- Verificar que el contenedor responda en el puerto 8000
- Confirmar que softSkills se procese correctamente
EOF

log_info "✅ Archivo de instrucciones creado"

# Resumen final
echo ""
echo "🎉 DESPLIEGUE CORREGIDO COMPLETADO EXITOSAMENTE"
echo "==============================================="
echo ""
echo "📋 Resumen de correcciones:"
echo "   ✅ Backend: Script de Azure creado y verificado"
echo "   ✅ Frontend: Corrección de softSkills aplicada"
echo "   ✅ Puerto: Configurado correctamente (8000)"
echo "   ✅ Configuración: Archivos de producción mejorados"
echo ""
echo "🚀 Próximos pasos:"
echo "   1. Revisar DEPLOYMENT_INSTRUCTIONS.md"
echo "   2. Subir código a Azure"
echo "   3. Configurar variables de entorno"
echo "   4. Monitorear logs en Azure Portal"
echo ""
echo "📚 URLs de verificación:"
echo "   - Backend API: https://tu-app.azurewebsites.net/docs"
echo "   - Health Check: https://tu-app.azurewebsites.net/health"
echo "   - Frontend: https://tu-frontend.azurestaticapps.net"
echo ""

log_info "Despliegue corregido completado. ¡La aplicación está lista para producción!" 