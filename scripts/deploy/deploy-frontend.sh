#!/bin/bash

set -euo pipefail

echo "🚀 Desplegando frontend a Azure Static Web Apps..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="${SCRIPT_DIR}/../../nuevo-frontend"
DIST_DIR="${FRONTEND_DIR}/dist"

RESOURCE_GROUP="evaluador-web_group"
STATIC_WEB_APP="evaluador-web"
DEPLOYMENT_TOKEN="aebf1d49e3563ed29cbad51f918b803e42c75fe04ae919b300d466e29962b31206-02a10979-c52c-4d1b-8007-0ecee55f986d01e13320b6281c1e"
ZIPDEPLOY_URL="https://${STATIC_WEB_APP}.scm.azurestaticapps.net/api/zipdeploy"

if [ ! -d "${FRONTEND_DIR}" ]; then
  echo "❌ Error: No se encontró el directorio ${FRONTEND_DIR}."
  exit 1
fi

cd "${FRONTEND_DIR}"

if [ -d "${DIST_DIR}" ] && [ -n "$(find "${DIST_DIR}" -mindepth 1 -maxdepth 1 -print -quit)" ]; then
  echo "♻️ Reutilizando build existente en dist/."
else
  echo "🔨 Construyendo frontend..."
  npm run build
fi

if [ ! -d "${DIST_DIR}" ] || [ -z "$(find "${DIST_DIR}" -mindepth 1 -print -quit)" ]; then
  echo "❌ Error: No se pudo encontrar un build válido en dist/."
  exit 1
fi

PACKAGE_NAME="frontend-build-$(date +%Y%m%d-%H%M%S).zip"
PACKAGE_PATH="${FRONTEND_DIR}/${PACKAGE_NAME}"

echo "📦 Empaquetando dist/ en ${PACKAGE_PATH}"
(
  cd "${DIST_DIR}"
  zip -qr "${PACKAGE_PATH}" .
)

cd "${SCRIPT_DIR}"

if ! command -v curl >/dev/null 2>&1; then
  echo "❌ Error: curl no está instalado en el sistema."
  exit 1
fi

echo "🚀 Subiendo paquete a Azure Static Web Apps..."
if ! curl --fail --show-error --silent \
  -X POST "${ZIPDEPLOY_URL}" \
  -H "Authorization: Bearer ${DEPLOYMENT_TOKEN}" \
  -H "Content-Type: application/zip" \
  --data-binary @"${PACKAGE_PATH}"; then
  echo ""
  echo "❌ Error: fallo al subir el artefacto generado."
  exit 1
fi

echo ""
echo "✅ Frontend desplegado correctamente."
echo "📦 Paquete utilizado: ${PACKAGE_PATH}"
echo "🌐 URL: https://${STATIC_WEB_APP}.azurestaticapps.net"
