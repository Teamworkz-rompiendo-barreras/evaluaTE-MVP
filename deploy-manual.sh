#!/bin/bash

echo "🚀 Despliegue manual del frontend a Azure Static Web Apps..."

# Configuración
RESOURCE_GROUP="evaluador-web_group"
STATIC_WEB_APP="evaluador-web"
SUBSCRIPTION_ID="824553b7-ed65-481c-bd34-5b6bcb6b360b"

# Construir el frontend
echo "🔨 Construyendo el frontend..."
cd nuevo-frontend
npm run build

if [ ! -d "dist" ]; then
    echo "❌ Error: No se pudo crear el directorio dist/"
    exit 1
fi

echo "✅ Frontend construido correctamente"

# Obtener token de acceso
echo "🔑 Obteniendo token de acceso..."
ACCESS_TOKEN=$(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Error: No se pudo obtener el token de acceso"
    exit 1
fi

echo "✅ Token obtenido correctamente"

# Crear archivo ZIP para despliegue
echo "📦 Creando archivo de despliegue..."
cd dist
zip -r ../frontend-deploy.zip .
cd ..

# Desplegar usando la API REST de Azure
echo "🚀 Iniciando despliegue..."

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
echo "⏳ Esperando que el despliegue se complete..."
sleep 15

# Mostrar información de la aplicación
echo "📊 Información de la aplicación:"
az staticwebapp show --name ${STATIC_WEB_APP} --resource-group ${RESOURCE_GROUP} --query "{name:name, hostname:defaultHostname, location:location, sku:sku.name}" -o table

echo ""
echo "🎉 ¡Despliegue completado!"
echo "🌐 URL: https://$(az staticwebapp show --name ${STATIC_WEB_APP} --resource-group ${RESOURCE_GROUP} --query "defaultHostname" -o tsv)"
echo ""
echo "📝 Para verificar el despliegue, visita la URL anterior en tu navegador"
