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

# Instalar dependencias dentro del paquete para evitar errores de build en Azure
echo "🧩 Empaquetando dependencias en .python_packages ..."
mkdir -p .python_packages/lib/site-packages
python3 -m pip install --upgrade pip >/dev/null 2>&1 || true
python3 -m pip install -r requirements.txt -t .python_packages/lib/site-packages

# Crear archivo ZIP con todos los archivos necesarios
# Excluir entornos virtuales y artefactos que no deben ir al servidor
zip -r ../backend-deploy.zip . \
  -x \
  ".venv/*" \
  "venv/*" \
  "__pycache__/*" \
  "*.pyc" \
  ".git/*" \
  "uploads/*" \
  "dist/*" \
  "node_modules/*" \
  "src/*" \
  "package.json" \
  "tsconfig.json" \
  "package-lock.json" \
  ".deployment" \
  ".azure-deployment" \
  "web.config" \
  ".env" \
  ".env.*" \
  "*.log" \
  "*.pid" \
  "*.pdf"

cd ..

if [ ! -f "backend-deploy.zip" ]; then
    echo "❌ Error: No se pudo crear el archivo ZIP del backend"
    exit 1
fi

echo "✅ Archivo ZIP del backend creado correctamente"

# Desplegar usando Azure CLI
echo "🚀 Desplegando a Azure Web App..."
# Evitar build en Azure (usamos dependencias vendorizadas) y Always On
az webapp config appsettings set --resource-group ${RESOURCE_GROUP} --name ${WEB_APP} --settings SCM_DO_BUILD_DURING_DEPLOYMENT=false ENABLE_ORYX_BUILD=false PYTHONPATH="/home/site/wwwroot/.python_packages/lib/site-packages" > /dev/null
az webapp config set --resource-group ${RESOURCE_GROUP} --name ${WEB_APP} --always-on true > /dev/null
# Definir startup command usando el script específico de Azure
az webapp config set --resource-group ${RESOURCE_GROUP} --name ${WEB_APP} --startup-file "python azure_startup.py" > /dev/null
# Preferir config-zip (ZipDeploy) por estabilidad
if ! az webapp deployment source config-zip --resource-group ${RESOURCE_GROUP} --name ${WEB_APP} --src backend-deploy.zip; then
    echo "⚠️  Fallback a onedeploy (menos estable)"
    az webapp deploy --resource-group ${RESOURCE_GROUP} --name ${WEB_APP} --src-path backend-deploy.zip --type zip
fi

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
