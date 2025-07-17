#!/bin/bash

# Script de despliegue para Azure App Service
# Este script configura el entorno para ejecutar Node.js

echo "🚀 Configurando entorno de despliegue para Azure..."

# Instalar dependencias de Node.js
echo "📦 Instalando dependencias de Node.js..."
npm ci --production

# Compilar TypeScript y copiar assets
echo "🔨 Compilando TypeScript..."
npm run build

# Verificar que las imágenes se copiaron correctamente
echo "📁 Verificando assets..."
if [ ! -f "dist/src/assets/background.png" ] || [ ! -f "dist/src/assets/radarchart.png" ]; then
    echo "❌ Error: Los assets no se copiaron correctamente"
    exit 1
fi

echo "✅ Assets verificados correctamente"

# Verificar dependencias nativas
echo "🔍 Verificando dependencias nativas..."
node check-dependencies.js

echo "✅ Despliegue configurado correctamente"
echo "🌐 La aplicación estará disponible en el puerto: $PORT" 