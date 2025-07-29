#!/bin/bash

# Script de build y deploy para Azure Static Web Apps
set -e

echo "🚀 Iniciando proceso de build y deploy..."

# Verificar que estamos en el directorio correcto
if [ ! -f "package.json" ]; then
    echo "❌ Error: No se encontró package.json. Asegúrate de estar en el directorio nuevo-frontend"
    exit 1
fi

# Limpiar build anterior
echo "🧹 Limpiando build anterior..."
rm -rf dist/

# Instalar dependencias
echo "📦 Instalando dependencias..."
npm ci

# Ejecutar lint
echo "🔍 Ejecutando lint..."
npm run lint

# Ejecutar tests
echo "🧪 Ejecutando tests..."
npm run test -- --run --coverage

# Build de la aplicación
echo "🔨 Construyendo aplicación..."
npm run build

# Verificar que el build fue exitoso
echo "✅ Verificando build..."
if [ ! -f "dist/index.html" ]; then
    echo "❌ Error: No se generó index.html"
    exit 1
fi

# Copiar configuración de Static Web Apps
echo "📋 Copiando configuración de Static Web Apps..."
cp staticwebapp.config.json dist/

# Verificar contenido del directorio dist
echo "📁 Contenido del directorio dist:"
ls -la dist/

echo "✅ Build completado exitosamente!"
echo "📄 index.html generado:"
head -5 dist/index.html

echo "🚀 Listo para deploy en Azure Static Web Apps" 