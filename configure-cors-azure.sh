#!/bin/bash

# Script para configurar CORS en Azure App Service
# Este script ayuda a configurar las variables de entorno necesarias para CORS

echo "=== Configuración de CORS para Azure App Service ==="
echo ""

# URL del frontend de Azure Static Web Apps
FRONTEND_URL="https://evaluador-frontend-fzbhemgtetfeeme6.spaincentral-01.azurestaticapps.net"

# URL del backend de Azure App Service
BACKEND_URL="https://evaluador-backend-fzbhemgtetfeeme6.spaincentral-01.azurewebsites.net"

echo "Frontend URL: $FRONTEND_URL"
echo "Backend URL: $BACKEND_URL"
echo ""

echo "=== Variables de entorno a configurar en Azure App Service ==="
echo ""
echo "1. Ve al Portal de Azure (https://portal.azure.com)"
echo "2. Navega a tu App Service: evaluador-backend-fzbhemgtetfeeme6"
echo "3. Ve a Settings > Configuration > Application settings"
echo "4. Agrega o actualiza las siguientes variables:"
echo ""

echo "Variable: ALLOWED_ORIGINS"
echo "Valor: http://localhost:3005,http://localhost:3006,http://localhost:5173,http://localhost:8080,$FRONTEND_URL"
echo ""

echo "Variable: PRODUCTION"
echo "Valor: true"
echo ""

echo "Variable: HOST"
echo "Valor: 0.0.0.0"
echo ""

echo "Variable: PORT"
echo "Valor: 8080"
echo ""

echo "=== Comandos Azure CLI (alternativa) ==="
echo ""
echo "# Configurar CORS origins"
echo "az webapp config appsettings set --name evaluador-backend-fzbhemgtetfeeme6 --resource-group evaluador-rg --settings ALLOWED_ORIGINS=\"http://localhost:3005,http://localhost:3006,http://localhost:5173,http://localhost:8080,$FRONTEND_URL\""
echo ""
echo "# Configurar modo producción"
echo "az webapp config appsettings set --name evaluador-backend-fzbhemgtetfeeme6 --resource-group evaluador-rg --settings PRODUCTION=true"
echo ""

echo "=== Verificación ==="
echo ""
echo "Después de configurar las variables:"
echo "1. Reinicia la App Service"
echo "2. Verifica el endpoint de salud: $BACKEND_URL/health"
echo "3. Prueba una solicitud CORS desde el frontend"
echo ""

echo "=== URLs para probar ==="
echo "Health check: $BACKEND_URL/health"
echo "API endpoint: $BACKEND_URL/api/informe-ia"
echo "Frontend: $FRONTEND_URL"
echo ""
