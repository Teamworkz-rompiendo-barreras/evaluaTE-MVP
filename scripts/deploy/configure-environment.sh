#!/bin/bash

echo "🔧 CONFIGURACIÓN DE VARIABLES DE ENTORNO EN AZURE"
echo "================================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Verificar si existe el archivo .env
if [ ! -f "backend/.env" ]; then
    print_warning "No se encontró backend/.env"
    print_status "Creando archivo .env desde env.example..."
    cp backend/env.example backend/.env
    print_warning "Por favor, edita backend/.env con tus valores reales antes de continuar"
    echo ""
    print_status "Presiona Enter cuando hayas configurado el archivo .env..."
    read
fi

# Leer variables del archivo .env
print_status "Leyendo variables de entorno desde backend/.env..."
source backend/.env

# Verificar variables críticas
if [ -z "$AZURE_OPENAI_API_KEY" ] || [ "$AZURE_OPENAI_API_KEY" = "tu_api_key_aqui" ]; then
    print_error "AZURE_OPENAI_API_KEY no está configurada correctamente"
    exit 1
fi

if [ -z "$AZURE_OPENAI_ENDPOINT" ] || [ "$AZURE_OPENAI_ENDPOINT" = "https://tu-recurso.openai.azure.com" ]; then
    print_error "AZURE_OPENAI_ENDPOINT no está configurado correctamente"
    exit 1
fi

print_success "Variables críticas verificadas correctamente"

echo ""
print_status "Configurando variables de entorno en Azure Web App..."

# Configurar variables de entorno en Azure Web App
az webapp config appsettings set \
    --resource-group evaluador-backend_group \
    --name evaluador-backend \
    --settings \
    AZURE_OPENAI_API_KEY="$AZURE_OPENAI_API_KEY" \
    AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
    AZURE_OPENAI_DEPLOYMENT="$AZURE_OPENAI_DEPLOYMENT" \
    AZURE_OPENAI_API_VERSION="$AZURE_OPENAI_API_VERSION" \
    PORT="$PORT" \
    HOST="$HOST" \
    ALLOWED_ORIGINS="$ALLOWED_ORIGINS"

if [ $? -eq 0 ]; then
    print_success "Variables de entorno configuradas correctamente"
else
    print_error "Error al configurar las variables de entorno"
    exit 1
fi

# Configurar variables opcionales si están definidas
if [ ! -z "$AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT" ] && [ "$AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT" != "https://tu-recurso-document-intelligence.cognitiveservices.azure.com/" ]; then
    print_status "Configurando Azure Document Intelligence..."
    az webapp config appsettings set \
        --resource-group evaluador-backend_group \
        --name evaluador-backend \
        --settings \
        AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT="$AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT" \
        AZURE_DOCUMENT_INTELLIGENCE_KEY="$AZURE_DOCUMENT_INTELLIGENCE_KEY"
fi

if [ ! -z "$AZURE_STORAGE_CONNECTION_STRING" ] && [ "$AZURE_STORAGE_CONNECTION_STRING" != "DefaultEndpointsProtocol=https;AccountName=tu-cuenta;AccountKey=tu-clave;EndpointSuffix=core.windows.net" ]; then
    print_status "Configurando Azure Storage..."
    az webapp config appsettings set \
        --resource-group evaluador-backend_group \
        --name evaluador-backend \
        --settings \
        AZURE_STORAGE_CONNECTION_STRING="$AZURE_STORAGE_CONNECTION_STRING" \
        AZURE_STORAGE_CONTAINER="$AZURE_STORAGE_CONTAINER"
fi

if [ ! -z "$SMTP_SERVER" ] && [ "$SMTP_SERVER" != "smtp.gmail.com" ]; then
    print_status "Configurando SMTP para notificaciones..."
    az webapp config appsettings set \
        --resource-group evaluador-backend_group \
        --name evaluador-backend \
        --settings \
        SMTP_SERVER="$SMTP_SERVER" \
        SMTP_PORT="$SMTP_PORT" \
        EMAIL_USER="$EMAIL_USER" \
        EMAIL_PASSWORD="$EMAIL_PASSWORD" \
        ADMIN_EMAIL="$ADMIN_EMAIL"
fi

echo ""
print_success "¡Configuración completada!"
print_status "Reiniciando la aplicación para aplicar los cambios..."

# Reiniciar la aplicación
az webapp restart --name evaluador-backend --resource-group evaluador-backend_group

if [ $? -eq 0 ]; then
    print_success "Aplicación reiniciada correctamente"
else
    print_warning "No se pudo reiniciar la aplicación automáticamente"
    print_status "Puedes reiniciarla manualmente con: az webapp restart --name evaluador-backend --resource-group evaluador-backend_group"
fi

echo ""
print_status "Verificando configuración..."
az webapp config appsettings list --name evaluador-backend --resource-group evaluador-backend_group --query "[?name[?contains(@, 'AZURE_OPENAI')]].{name:name, value:value}" -o table

echo ""
print_success "¡Variables de entorno configuradas y aplicación reiniciada!"
print_warning "Recuerda que los cambios pueden tardar unos minutos en propagarse"
