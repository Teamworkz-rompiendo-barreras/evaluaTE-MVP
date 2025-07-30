#!/bin/bash

# Script de verificación para el build del frontend
# Este script simula los pasos que se ejecutan en GitHub Actions

set -e  # Salir si hay algún error

echo "🔍 VERIFICACIÓN DE BUILD DEL FRONTEND"
echo "======================================"

# Verificar que estamos en el directorio correcto
if [ ! -f "package.json" ]; then
    echo "❌ Error: No se encontró package.json. Ejecuta este script desde el directorio nuevo-frontend/"
    exit 1
fi

echo "✅ Directorio correcto detectado"

# Verificar archivos de dependencias
echo ""
echo "📦 Verificando archivos de dependencias..."
if [ ! -f "package-lock.json" ]; then
    echo "❌ package-lock.json no encontrado. Generando..."
    npm install
else
    echo "✅ package-lock.json encontrado"
fi

# Instalar dependencias
echo ""
echo "📥 Instalando dependencias..."
npm ci --prefer-offline --no-audit
echo "✅ Dependencias instaladas correctamente"

# Verificar configuración de TypeScript
echo ""
echo "🔧 Verificando configuración de TypeScript..."
npx tsc --noEmit
echo "✅ TypeScript configurado correctamente"

# Ejecutar linting
echo ""
echo "🧹 Ejecutando linting..."
npm run lint
echo "✅ Linting completado"

# Ejecutar tests
echo ""
echo "🧪 Ejecutando tests unitarios..."
npm run test -- --run --coverage
echo "✅ Tests unitarios completados"

# Construir el proyecto
echo ""
echo "🏗️ Construyendo el proyecto..."
npm run build
echo "✅ Build completado"

# Verificar archivos de salida
echo ""
echo "📁 Verificando archivos de salida..."
if [ ! -d "dist" ]; then
    echo "❌ Directorio dist no encontrado"
    exit 1
fi

echo "✅ Directorio dist encontrado"
ls -la dist/

# Verificar index.html
if [ ! -f "dist/index.html" ]; then
    echo "❌ index.html no encontrado en dist/"
    exit 1
fi
echo "✅ index.html encontrado"

# Verificar assets
if [ ! -d "dist/assets" ]; then
    echo "❌ Directorio assets no encontrado en dist/"
    exit 1
fi
echo "✅ Directorio assets encontrado"
ls -la dist/assets/ | head -5

# Copiar configuración de Static Web Apps
echo ""
echo "📋 Copiando configuración de Static Web Apps..."
if [ -f "staticwebapp.config.json" ]; then
    cp staticwebapp.config.json dist/
    echo "✅ staticwebapp.config.json copiado"
else
    echo "❌ staticwebapp.config.json no encontrado"
    exit 1
fi

# Verificación final
echo ""
echo "🎉 VERIFICACIÓN COMPLETADA EXITOSAMENTE"
echo "======================================="
echo "✅ Todos los archivos necesarios están presentes"
echo "✅ El build se completó sin errores"
echo "✅ La configuración está lista para deploy"

echo ""
echo "📊 Resumen del build:"
echo "  - index.html: ✅"
echo "  - assets/: ✅"
echo "  - staticwebapp.config.json: ✅"
echo "  - TypeScript: ✅"
echo "  - Linting: ✅"
echo "  - Tests: ✅"

echo ""
echo "🚀 El proyecto está listo para deploy en Azure Static Web Apps" 