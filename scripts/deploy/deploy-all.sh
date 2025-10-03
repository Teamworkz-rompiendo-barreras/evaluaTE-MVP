#!/bin/bash

echo "🚀 DESPLIEGUE COMPLETO DE EVALUATE MVP A AZURE"
echo "================================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar Azure CLI
print_status "Verificando Azure CLI..."
if ! command -v az &> /dev/null; then
    print_error "Azure CLI no está instalado. Por favor, instálalo primero."
    exit 1
fi

# Verificar login en Azure
print_status "Verificando login en Azure..."
if ! az account show &> /dev/null; then
    print_error "No estás logueado en Azure. Ejecuta 'az login' primero."
    exit 1
fi

print_success "Conectado a Azure: $(az account show --query name -o tsv)"

echo ""
print_status "Iniciando despliegue del FRONTEND..."
echo "----------------------------------------"

# Desplegar frontend (build + zip manual)
if ./deploy-frontend.sh; then
    print_success "Frontend desplegado correctamente"
else
    print_error "Error en el despliegue del frontend"
    exit 1
fi

echo ""
print_status "Iniciando despliegue del BACKEND..."
echo "----------------------------------------"

# Desplegar backend
if ./deploy-backend.sh; then
    print_success "Backend desplegado correctamente"
else
    print_error "Error en el despliegue del backend"
    exit 1
fi

echo ""
echo "🎉 DESPLIEGUE COMPLETADO EXITOSAMENTE!"
echo "========================================"
echo ""

# Mostrar resumen final
print_status "RESUMEN DEL DESPLIEGUE:"
echo ""

# Frontend info
FRONTEND_URL=$(az staticwebapp show --name evaluador-web --resource-group evaluador-web_group --query "defaultHostname" -o tsv)
print_success "Frontend: https://${FRONTEND_URL}"

# Backend info
BACKEND_URL=$(az webapp show --name evaluador-backend --resource-group evaluador-backend_group --query "defaultHostName" -o tsv)
print_success "Backend: https://${BACKEND_URL}"

echo ""
print_status "COMANDOS ÚTILES:"
echo "• Ver logs del frontend: az staticwebapp show --name evaluador-web --resource-group evaluador-web_group"
echo "• Ver logs del backend: az webapp log tail --name evaluador-backend --resource-group evaluador-backend_group"
echo "• Estado del frontend: az staticwebapp show --name evaluador-web --resource-group evaluador-web_group --query state"
echo "• Estado del backend: az webapp show --name evaluador-backend --resource-group evaluador-backend_group --query state"

echo ""
print_warning "IMPORTANTE: Asegúrate de que las variables de entorno estén configuradas correctamente en Azure"
print_warning "para que la aplicación funcione completamente."

echo ""
print_success "¡Tu aplicación EvaluaTE MVP está ahora desplegada y funcionando en Azure!"
