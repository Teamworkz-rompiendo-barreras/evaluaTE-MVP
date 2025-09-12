#!/bin/bash

set -euo pipefail

echo "🔨 Construyendo frontend..."
cd "$(dirname "$0")/../../nuevo-frontend"
npm run build

if [ ! -d "dist" ]; then
  echo "❌ Error: No se generó dist/"
  exit 1
fi

NAME="frontend-build-$(date +%Y%m%d-%H%M%S).zip"
echo "📦 Empaquetando: $NAME"
cd dist
zip -qr "../$NAME" .
cd ..

echo "✅ Paquete creado: $(pwd)/$NAME"
echo "
Siguiente paso:
- Sube manualmente el zip a Azure Static Web Apps o usa tu pipeline CI/CD.
"

#!/bin/bash

echo "🚀 Desplegando frontend a Azure Static Web Apps..."

# Configuración
RESOURCE_GROUP="evaluador-web_group"
STATIC_WEB_APP="evaluador-web"
DEPLOYMENT_TOKEN="aebf1d49e3563ed29cbad51f918b803e42c75fe04ae919b300d466e29962b31206-02a10979-c52c-4d1b-8007-0ecee55f986d01e13320b6281c1e"
API_URL="https://management.azure.com/subscriptions/824553b7-ed65-481c-bd34-5b6bcb6b360b/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Web/staticSites/${STATIC_WEB_APP}/deployments"

# Construir el frontend
echo "🔨 Construyendo el frontend..."
cd nuevo-frontend
npm run build

if [ ! -d "dist" ]; then
    echo "❌ Error: No se pudo crear el directorio dist/"
    exit 1
fi

# Crear archivo ZIP para despliegue
echo "📦 Creando archivo de despliegue..."
cd dist
zip -r ../frontend-deploy.zip .
cd ..

# Desplegar usando la API REST de Azure
echo "🚀 Desplegando a Azure..."
curl -X POST "${API_URL}?api-version=2021-02-01" \
  -H "Authorization: Bearer $(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)" \
  -H "Content-Type: application/json" \
  -d "{
    \"properties\": {
      \"source\": \"manual\",
      \"buildProperties\": {
        \"apiLocation\": \"\",
        \"appLocation\": \".\",
        \"outputLocation\": \".\"
      }
    }
  }"

echo "✅ Despliegue iniciado. Verificando estado..."

# Verificar el estado del despliegue
sleep 10
az staticwebapp show --name ${STATIC_WEB_APP} --resource-group ${RESOURCE_GROUP} --query "defaultHostname" -o tsv

echo ""
echo "🎉 Frontend desplegado correctamente!"
echo "🌐 URL: https://$(az staticwebapp show --name ${STATIC_WEB_APP} --resource-group ${RESOURCE_GROUP} --query "defaultHostname" -o tsv)"
