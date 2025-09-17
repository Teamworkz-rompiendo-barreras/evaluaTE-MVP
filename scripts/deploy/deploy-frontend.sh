#!/bin/bash

set -euo pipefail

# -----------------------------------------------------------------------------
# Despliega el frontend a Azure Static Web Apps.
#
# El token de despliegue nunca debe almacenarse en el repositorio. Proporciónalo
# de forma segura en tiempo de ejecución exportando la variable de entorno
# DEPLOYMENT_TOKEN o dejando que el script lo obtenga mediante
# `az staticwebapp secrets list`. Consulta scripts/deploy/README.md para más
# detalles sobre cómo integrarlo con un gestor de secretos o con tu pipeline de
# CI/CD.
# -----------------------------------------------------------------------------

RESOURCE_GROUP="evaluador-web_group"
STATIC_WEB_APP="evaluador-web"
SUBSCRIPTION_ID="824553b7-ed65-481c-bd34-5b6bcb6b360b"
API_URL="https://management.azure.com/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Web/staticSites/${STATIC_WEB_APP}/deployments"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="${SCRIPT_DIR}/../../nuevo-frontend"
DIST_DIR="${FRONTEND_DIR}/dist"
PACKAGE_NAME="frontend-deploy.zip"
PACKAGE_PATH="${FRONTEND_DIR}/${PACKAGE_NAME}"

log() {
  printf '%s\n' "$1"
}

obtain_deployment_token() {
  if [ -n "${DEPLOYMENT_TOKEN:-}" ]; then
    return 0
  fi

  if ! command -v az >/dev/null 2>&1; then
    return 1
  fi

  log "🔐 Intentando obtener DEPLOYMENT_TOKEN con Azure CLI..."
  local token
  if ! token=$(az staticwebapp secrets list \
      --name "${STATIC_WEB_APP}" \
      --resource-group "${RESOURCE_GROUP}" \
      --query "properties.apiKey" \
      -o tsv 2>/dev/null); then
    return 1
  fi

  if [ -z "${token}" ]; then
    return 1
  fi

  export DEPLOYMENT_TOKEN="${token}"
  return 0
}

if ! obtain_deployment_token; then
  cat >&2 <<'EOF'
❌ Error: No se encontró el token de despliegue de Azure Static Web Apps.
Proporciona el secreto exportando la variable de entorno DEPLOYMENT_TOKEN o
asegúrate de tener Azure CLI instalado y autenticado para ejecutar
`az staticwebapp secrets list`. Revisa scripts/deploy/README.md para más
información.
EOF
  exit 1
fi

log "🔨 Construyendo el frontend..."
cd "${FRONTEND_DIR}"
npm run build

if [ ! -d "${DIST_DIR}" ]; then
  echo "❌ Error: No se pudo crear el directorio dist/" >&2
  exit 1
fi

log "📦 Creando paquete de despliegue..."
rm -f "${PACKAGE_PATH}"
cd "${DIST_DIR}"
zip -qr "${PACKAGE_PATH}" .
cd "${FRONTEND_DIR}"

if [ ! -f "${PACKAGE_PATH}" ]; then
  echo "❌ Error: No se pudo crear el paquete ${PACKAGE_NAME}" >&2
  exit 1
fi

log "✅ Paquete listo: ${PACKAGE_PATH}"

log "🚀 Subiendo paquete a Azure Static Web Apps..."
response_file="$(mktemp)"
status_code=$(curl --silent --show-error \
  -X POST "${API_URL}?api-version=2021-02-01" \
  -H "Authorization: Bearer $(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)" \
  -H "x-azure-static-web-apps-deployment-token: ${DEPLOYMENT_TOKEN}" \
  -H "Content-Type: application/zip" \
  --data-binary "@${PACKAGE_PATH}" \
  -w '%{http_code}' \
  -o "${response_file}")

curl_exit_code=$?

if [ "${curl_exit_code}" -ne 0 ]; then
  echo "❌ Error al subir el paquete (curl exit ${curl_exit_code})." >&2
  cat "${response_file}" >&2 || true
  rm -f "${response_file}"
  exit 1
fi

if [ "${status_code}" != "202" ] && [ "${status_code}" != "200" ]; then
  echo "❌ Error al subir el paquete. Código HTTP: ${status_code}" >&2
  cat "${response_file}" >&2 || true
  rm -f "${response_file}"
  exit 1
fi

rm -f "${response_file}"
log "✅ Paquete subido correctamente. Eliminando artefacto temporal..."
rm -f "${PACKAGE_PATH}"

default_hostname=$(az staticwebapp show --name "${STATIC_WEB_APP}" --resource-group "${RESOURCE_GROUP}" --query "defaultHostname" -o tsv)

log ""
log "🎉 Frontend desplegado correctamente!"
log "🌐 URL: https://${default_hostname}"

# Minimiza el tiempo que el token queda en variables de entorno del shell actual.
unset DEPLOYMENT_TOKEN
