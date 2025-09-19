# Despliegue a Azure

## Scripts principales
- `scripts/deploy/deploy-all.sh`: orquesta frontend + backend.
- `scripts/deploy/deploy-frontend.sh`: build y genera ZIP del frontend (sin secretos).
- `scripts/deploy/deploy-backend.sh`: empaqueta y despliega backend a Azure Web App.
- `scripts/deploy/configure-environment.sh`: aplica variables de entorno.

## Uso rápido
```bash
# Orquestado
./scripts/deploy/deploy-all.sh

# Solo frontend (build + ZIP)
./scripts/deploy/deploy-frontend.sh

# Solo backend
./scripts/deploy/deploy-backend.sh

# Variables de entorno
./scripts/deploy/configure-environment.sh
```

## Requisitos
- Azure CLI instalado y logueado: `az login`
- Node 20+ para frontend; Python 3.11 para backend

## GitHub Actions: secreto para Azure Static Web Apps
Antes de lanzar cualquiera de los workflows de despliegue del frontend (`frontend-deploy-simple.yml`, `frontend-deploy-minimal.yml` o `frontend-deploy-test.yml`) es imprescindible registrar el token de Azure como un secreto de GitHub:

1. En el portal de Azure Static Web Apps abre **Deployment token** y pulsa **Regenerate** para obtener un valor nuevo si el anterior se ha filtrado.
2. Copia el token y en el repositorio ve a **Settings → Secrets and variables → Actions → New repository secret**.
3. Usa `AZURE_STATIC_WEB_APPS_API_TOKEN` como nombre del secreto y pega el valor del token regenerado.
4. Guarda el secreto y vuelve a ejecutar el workflow que necesites.

### Rotación y saneamiento tras una filtración
- Después de regenerar el token en Azure, vuelve a actualizar el secreto del repositorio con el valor nuevo y elimina el antiguo si existía.
- Sanea el historial del repositorio para borrar el token expuesto (por ejemplo, con [`git filter-repo`](https://github.com/newren/git-filter-repo): `git filter-repo --replace-text <(printf "<token_antiguo>==>")`).
- Fuerza un push sobre la rama afectada y comunica a las personas colaboradoras que realicen un `git fetch --all` seguido de `git reset --hard origin/<rama>` para alinear sus clones locales.

## Notas
- Los scripts antiguos se han eliminado o movido a `scripts/archive/` y la documentación legacy a `docs/archive/`.
- Evita tokens secretos en el repo. Usa variables de entorno o Azure App Settings.
