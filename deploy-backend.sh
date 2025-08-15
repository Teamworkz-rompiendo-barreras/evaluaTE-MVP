#!/bin/bash

echo "🚀 Desplegando backend a Azure Web App..."

# Configuración
RESOURCE_GROUP="evaluador-backend_group"
WEB_APP="evaluador-backend"

# Verificar que estamos en el directorio correcto
if [ ! -f "backend/main.py" ]; then
    echo "❌ Error: No se encontró backend/main.py. Asegúrate de estar en el directorio raíz del proyecto."
    exit 1
fi

# Crear archivo ZIP para despliegue
echo "📦 Creando archivo de despliegue del backend..."
cd backend

# Crear archivo ZIP con todos los archivos necesarios
zip -r ../backend-deploy.zip . -x "venv/*" "__pycache__/*" "*.pyc" ".git/*" "uploads/*"

cd ..

if [ ! -f "backend-deploy.zip" ]; then
    echo "❌ Error: No se pudo crear el archivo ZIP del backend"
    exit 1
fi

echo "✅ Archivo ZIP del backend creado correctamente"

# Desplegar usando Azure CLI
echo "🚀 Desplegando a Azure Web App..."
az webapp deploy --resource-group ${RESOURCE_GROUP} --name ${WEB_APP} --src-path backend-deploy.zip --type zip

if [ $? -eq 0 ]; then
    echo "✅ Backend desplegado correctamente"
else
    echo "❌ Error en el despliegue del backend"
    exit 1
fi

# Verificar el estado del despliegue
echo "⏳ Verificando estado del despliegue..."
sleep 10

# Mostrar información de la aplicación
echo "📊 Información de la aplicación:"
az webapp show --name ${WEB_APP} --resource-group ${RESOURCE_GROUP} --query "{name:name, state:state, hostname:defaultHostName, location:location, sku:sku.name}" -o table

echo ""
echo "🎉 ¡Backend desplegado correctamente!"
echo "🌐 URL: https://$(az webapp show --name ${WEB_APP} --resource-group ${RESOURCE_GROUP} --query "defaultHostName" -o tsv)"
echo ""
echo "📝 Para verificar el despliegue, visita la URL anterior en tu navegador"
echo "🔍 Para ver los logs: az webapp log tail --name ${WEB_APP} --resource-group ${RESOURCE_GROUP}"
