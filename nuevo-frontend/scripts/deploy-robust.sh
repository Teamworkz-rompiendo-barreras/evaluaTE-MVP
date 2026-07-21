#!/bin/bash

# 🔧 Script de Deploy Robusto - Solución Definitiva
# Resuelve problemas de npm cache y deploy cancelado

set -e  # Exit on any error

echo "🚀 Iniciando deploy robusto..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "package.json" ]; then
    log_error "No se encontró package.json. Ejecuta este script desde el directorio nuevo-frontend/"
    exit 1
fi

log_info "Verificando entorno..."

# Verificar Node.js
NODE_VERSION=$(node --version)
log_success "Node.js version: $NODE_VERSION"

# Verificar npm
NPM_VERSION=$(npm --version)
log_success "npm version: $NPM_VERSION"

# Limpiar cache de npm (solución para error de cache)
log_info "Limpiando cache de npm..."
npm cache clean --force || true
log_success "Cache limpiado"

# Configurar npm para CI/CD
log_info "Configurando npm para CI/CD..."
npm config set prefer-offline true
npm config set audit false
npm config set fund false
npm config set loglevel error
log_success "npm configurado"

# Instalar dependencias de forma robusta
log_info "Instalando dependencias..."
npm install --no-audit --no-fund --prefer-offline
log_success "Dependencias instaladas"

# Verificar TypeScript
log_info "Verificando TypeScript..."
npx tsc --noEmit
log_success "TypeScript OK"

# Ejecutar lint
log_info "Ejecutando lint..."
npm run lint
log_success "Lint OK"

# Ejecutar tests
log_info "Ejecutando tests..."
npm run test -- --run --coverage
log_success "Tests OK"

# Construir proyecto
log_info "Construyendo proyecto..."
npm run build
log_success "Build completado"

# Verificar artefactos de build
log_info "Verificando artefactos..."
if [ ! -f "dist/index.html" ]; then
    log_error "index.html no encontrado en dist/"
    exit 1
fi

if [ ! -f "dist/staticwebapp.config.json" ]; then
    log_warning "staticwebapp.config.json no encontrado, copiando..."
    cp staticwebapp.config.json dist/
fi

if [ ! -d "dist/assets" ]; then
    log_warning "directorio assets no encontrado en dist/"
fi

log_success "Artefactos verificados"

# Mostrar información del build
log_info "Información del build:"
echo "📁 Directorio dist/:"
ls -la dist/
echo ""
echo "📄 Archivos críticos:"
[ -f "dist/index.html" ] && echo "✅ index.html" || echo "❌ index.html"
[ -f "dist/staticwebapp.config.json" ] && echo "✅ staticwebapp.config.json" || echo "❌ staticwebapp.config.json"
[ -d "dist/assets" ] && echo "✅ assets/" || echo "❌ assets/"

# Verificar tamaño del build
BUILD_SIZE=$(du -sh dist/ | cut -f1)
log_info "Tamaño del build: $BUILD_SIZE"

# Verificar que el build es válido
log_info "Verificando que el build es válido..."
if grep -q "error" dist/index.html 2>/dev/null; then
    log_error "Se encontraron errores en index.html"
    exit 1
fi

log_success "Build verificado y válido"

# Preparar para deploy
log_info "Preparando para deploy..."
echo "🚀 El build está listo para deploy"
echo "📁 Directorio: $(pwd)/dist"
echo "📊 Tamaño: $BUILD_SIZE"
echo "⏰ Timestamp: $(date)"

log_success "Deploy robusto completado exitosamente!"

# Instrucciones para deploy manual
echo ""
echo "📋 Para deploy manual a Azure Static Web Apps:"
echo "1. Sube el contenido de dist/ a tu Azure Static Web App"
echo "2. O usa el workflow de GitHub Actions"
echo "3. Verifica que la aplicación funcione correctamente"
echo ""
echo "🔗 Documentación: SOLUCION_DEFINITIVA_NPM_DEPLOY.md" 