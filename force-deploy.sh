#!/bin/bash

echo "🚀 Forzando deployment del frontend con correcciones..."

cd nuevo-frontend

# 1. Limpiar build anterior
echo "🧹 Limpiando build anterior..."
rm -rf dist/

# 2. Nuevo build
echo "🔨 Creando nuevo build..."
npm run build

# 3. Verificar que el build se creó correctamente
if [ ! -d "dist" ]; then
    echo "❌ Error: No se pudo crear el directorio dist/"
    exit 1
fi

# 4. Crear zip con timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
ZIP_NAME="frontend-fixed-$TIMESTAMP.zip"

echo "📦 Creando $ZIP_NAME..."
zip -r "$ZIP_NAME" dist/

echo "✅ Deployment package creado: $ZIP_NAME"
echo ""
echo "📋 INSTRUCCIONES PARA DEPLOYMENT MANUAL:"
echo "1. Ve a Azure Portal → Static Web Apps → evaluador-web"
echo "2. En 'Overview' busca el botón 'Browse' o 'Manage deployment'"
echo "3. Sube el archivo: $(pwd)/$ZIP_NAME"
echo "4. Espera 2-3 minutos y prueba el sitio"
echo ""
echo "🔗 O arrastra este archivo al navegador en la página de Azure:"
echo "   $(pwd)/$ZIP_NAME"
