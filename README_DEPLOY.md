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

## Notas
- Los scripts antiguos se han eliminado o movido a `scripts/archive/` y la documentación legacy a `docs/archive/`.
- Evita tokens secretos en el repo. Usa variables de entorno o Azure App Settings.
