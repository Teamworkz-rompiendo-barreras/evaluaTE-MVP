#!/bin/bash

echo "🚀 DESPLIEGUE DIRECTO A AZURE STATIC WEB APPS"
echo "=============================================="
echo ""

# Configuración
RESOURCE_GROUP="evaluador-web_group"
STATIC_WEB_APP="evaluador-web"
DEPLOYMENT_TOKEN="ad5f34aebb8b854d7a97186453bc71a4a574acda6c1174870276da3619bd312706-131fe071-1100-48e3-9692-cb4df94c79f01e13320b6281c1e"
SUBSCRIPTION_ID="824553b7-ed65-481c-bd34-5b6bcb6b360b"

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

# Construir el frontend
print_status "🔨 Construyendo el frontend..."
cd nuevo-frontend
npm run build

if [ ! -d "dist" ]; then
    print_error "No se pudo crear el directorio dist/"
    exit 1
fi

print_success "Frontend construido correctamente"

# Copiar archivo de configuración
print_status "📋 Copiando archivo de configuración..."
cp staticwebapp.config.json dist/
print_success "Configuración copiada"

# Crear archivo ZIP para despliegue
print_status "📦 Creando archivo de despliegue..."
cd dist
zip -r ../frontend-deploy-direct.zip .
cd ..

# Obtener token de acceso de Azure
print_status "🔑 Obteniendo token de acceso de Azure..."
ACCESS_TOKEN=$(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)

if [ -z "$ACCESS_TOKEN" ]; then
    print_error "No se pudo obtener el token de acceso"
    exit 1
fi

print_success "Token obtenido correctamente"

# Desplegar usando la API REST de Azure
print_status "🚀 Iniciando despliegue directo..."

DEPLOYMENT_RESPONSE=$(curl -s -X POST \
  "https://management.azure.com/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Web/staticSites/${STATIC_WEB_APP}/deployments?api-version=2021-02-01" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "source": "manual",
      "buildProperties": {
        "apiLocation": "",
        "appLocation": ".",
        "outputLocation": "."
      }
    }
  }')

echo "📋 Respuesta del despliegue: ${DEPLOYMENT_RESPONSE}"

# Verificar el estado
print_status "⏳ Esperando que el despliegue se complete..."
sleep 20

# Mostrar información de la aplicación
print_status "📊 Verificando estado de la aplicación..."
az staticwebapp show --name ${STATIC_WEB_APP} --resource-group ${RESOURCE_GROUP} --query "{name:name, hostname:defaultHostname, location:location, sku:sku.name}" -o table

echo ""
print_success "🎉 ¡Despliegue directo completado!"
print_status "🌐 URL: https://$(az staticwebapp show --name ${STATIC_WEB_APP} --resource-group ${RESOURCE_GROUP} --query "defaultHostname" -o tsv)"

echo ""
print_warning "IMPORTANTE: El despliegue puede tardar unos minutos en propagarse completamente"
print_status "Para verificar, visita la URL anterior y prueba la página de privacidad: /privacidad"
