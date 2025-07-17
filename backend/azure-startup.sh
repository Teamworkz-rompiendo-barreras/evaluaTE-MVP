#!/bin/bash

echo "🚀 Iniciando configuración de Azure App Service..."

# Verificar que estamos en el directorio correcto
if [ ! -f "package.json" ]; then
    echo "❌ Error: No se encontró package.json. Asegúrate de estar en el directorio raíz del proyecto."
    exit 1
fi

# Instalar dependencias si no están instaladas
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias..."
    npm install
fi

# Verificar que las imágenes están en su lugar
echo "📁 Verificando archivos de assets..."
if [ ! -f "dist/src/assets/background.png" ] || [ ! -f "dist/src/assets/radarchart.png" ]; then
    echo "⚠️  Assets no encontrados en dist, copiando..."
    node copy-assets.js
fi

# Verificar dependencias nativas
echo "🔍 Verificando dependencias nativas..."
node check-dependencies.js

# Verificar variables de entorno
echo "🔧 Verificando variables de entorno..."
required_vars=("AZURE_OPENAI_API_KEY" "AZURE_OPENAI_ENDPOINT" "AZURE_OPENAI_DEPLOYMENT")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Variables de entorno faltantes: ${missing_vars[*]}"
    echo "💡 Configura estas variables en Azure App Service > Configuration > Application settings"
    exit 1
else
    echo "✅ Todas las variables de entorno están configuradas"
fi

# Establecer puerto por defecto si no está definido
if [ -z "$PORT" ]; then
    export PORT=8080
    echo "🔧 Puerto por defecto establecido: $PORT"
fi

echo "✅ Configuración completada. Iniciando aplicación..."
echo "🌐 La aplicación estará disponible en el puerto: $PORT"

# Iniciar la aplicación
exec node dist/index.js 