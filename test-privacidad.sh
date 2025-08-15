#!/bin/bash

echo "🧪 PROBANDO PÁGINA DE PRIVACIDAD"
echo "================================="
echo ""

FRONTEND_URL="https://yellow-mud-0b6281c1e.6.azurestaticapps.net"

echo "🔍 Verificando página principal..."
MAIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${FRONTEND_URL}/")
echo "   Página principal: ${MAIN_STATUS}"

echo ""
echo "🔍 Verificando página de privacidad..."
PRIVACIDAD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${FRONTEND_URL}/privacidad")
echo "   Página privacidad: ${PRIVACIDAD_STATUS}"

echo ""
echo "🔍 Verificando contenido de la página de privacidad..."
PRIVACIDAD_CONTENT=$(curl -s "${FRONTEND_URL}/privacidad" | grep -i "política de privacidad" | wc -l)
echo "   Ocurrencias de 'política de privacidad': ${PRIVACIDAD_CONTENT}"

echo ""
echo "🔍 Verificando enlaces en la página principal..."
MAIN_LINKS=$(curl -s "${FRONTEND_URL}/" | grep -i "privacidad" | wc -l)
echo "   Enlaces a privacidad en página principal: ${MAIN_LINKS}"

echo ""
echo "🔍 Verificando archivos JavaScript..."
JS_FILES=$(curl -s "${FRONTEND_URL}/" | grep -o 'assets/index-[^"]*\.js' | head -1)
echo "   Archivo JS principal: ${JS_FILES}"

if [ ! -z "$JS_FILES" ]; then
    echo "   Verificando que el archivo JS existe..."
    JS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${FRONTEND_URL}/${JS_FILES}")
    echo "   Estado del archivo JS: ${JS_STATUS}"
fi

echo ""
echo "📋 RESUMEN:"
if [ "$PRIVACIDAD_STATUS" = "200" ] && [ "$PRIVACIDAD_CONTENT" -gt 0 ]; then
    echo "✅ La página de privacidad está funcionando correctamente"
else
    echo "❌ Hay problemas con la página de privacidad"
fi

if [ "$MAIN_LINKS" -gt 0 ]; then
    echo "✅ Los enlaces a privacidad están presentes"
else
    echo "❌ No se encontraron enlaces a privacidad"
fi

echo ""
echo "🌐 URLs para probar manualmente:"
echo "   Página principal: ${FRONTEND_URL}/"
echo "   Página privacidad: ${FRONTEND_URL}/privacidad"
echo ""
echo "💡 Si hay problemas, verifica:"
echo "   1. Que el navegador tenga JavaScript habilitado"
echo "   2. Que no haya errores en la consola del navegador"
echo "   3. Que la ruta /privacidad esté configurada en React Router"
