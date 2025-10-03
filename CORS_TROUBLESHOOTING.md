# Solución de Problemas CORS - EvaluaTE

## Problema Identificado

El backend está configurado para permitir solo orígenes locales en CORS, lo que causa errores 503 preflight cuando el frontend en producción intenta comunicarse con el backend.

## Errores Típicos

```
Access to fetch at 'https://evaluador-backend-fzbhemgtetfeeme6.spaincentral-01.azurewebsites.net/api/informe-ia' 
from origin 'https://yellow-mud-0b6281c1e.6.azurestaticapps.net' 
has been blocked by CORS policy: Response to preflight request doesn't pass access control check: 
It does not have HTTP ok status.
```

## Solución Implementada

### 1. Configuración Actualizada del Backend

El archivo `backend/main.py` ha sido actualizado para:

- Incluir el dominio de producción del frontend por defecto
- Agregar lógica para incluir dominios de Azure Static Web Apps en producción
- Mantener compatibilidad con desarrollo local

### 2. Variables de Entorno Requeridas

Configurar en Azure App Service las siguientes variables:

```bash
ALLOWED_ORIGINS=http://localhost:3005,http://localhost:3006,http://localhost:5173,http://localhost:8080,https://yellow-mud-0b6281c1e.6.azurestaticapps.net
PRODUCTION=true
HOST=0.0.0.0
PORT=8080
```

### 3. Pasos para Aplicar la Solución

#### Opción A: Portal de Azure (Recomendado)

1. Ve al [Portal de Azure](https://portal.azure.com)
2. Navega a tu App Service: `evaluador-backend-fzbhemgtetfeeme6`
3. Ve a **Settings** > **Configuration** > **Application settings**
4. Agrega o actualiza las variables:
   - `ALLOWED_ORIGINS`: `http://localhost:3005,http://localhost:3006,http://localhost:5173,http://localhost:8080,https://yellow-mud-0b6281c1e.6.azurestaticapps.net`
   - `PRODUCTION`: `true`
   - `HOST`: `0.0.0.0`
   - `PORT`: `8080`
5. **Guarda** y **reinicia** la App Service

#### Opción B: Azure CLI

```bash
# Configurar CORS origins
az webapp config appsettings set \
  --name evaluador-backend-fzbhemgtetfeeme6 \
  --resource-group evaluador-rg \
  --settings ALLOWED_ORIGINS="http://localhost:3005,http://localhost:3006,http://localhost:5173,http://localhost:8080,https://yellow-mud-0b6281c1e.6.azurestaticapps.net"

# Configurar modo producción
az webapp config appsettings set \
  --name evaluador-backend-fzbhemgtetfeeme6 \
  --resource-group evaluador-rg \
  --settings PRODUCTION=true

# Reiniciar la App Service
az webapp restart \
  --name evaluador-backend-fzbhemgtetfeeme6 \
  --resource-group evaluador-rg
```

### 4. Verificación

#### Script de Prueba Automatizado

```bash
node test-cors-configuration.js
```

#### Verificación Manual

1. **Health Check**: `https://evaluador-backend-fzbhemgtetfeeme6.spaincentral-01.azurewebsites.net/health`
2. **Preflight Request**: Usar las herramientas de desarrollador del navegador
3. **Frontend**: Probar la funcionalidad completa en `https://yellow-mud-0b6281c1e.6.azurestaticapps.net`

### 5. URLs Importantes

- **Backend**: `https://evaluador-backend-fzbhemgtetfeeme6.spaincentral-01.azurewebsites.net`
- **Frontend**: `https://yellow-mud-0b6281c1e.6.azurestaticapps.net`
- **Health Check**: `https://evaluador-backend-fzbhemgtetfeeme6.spaincentral-01.azurewebsites.net/health`

### 6. Monitoreo

Después de aplicar los cambios:

1. Verifica que el backend esté funcionando: `/health`
2. Revisa los logs de la App Service para errores
3. Prueba la funcionalidad completa del frontend
4. Monitorea las métricas de la App Service

### 7. Solución de Problemas Adicionales

Si persisten los problemas:

1. **Verifica que el backend esté funcionando**:
   ```bash
   curl https://evaluador-backend-fzbhemgtetfeeme6.spaincentral-01.azurewebsites.net/health
   ```

2. **Revisa los logs de la App Service**:
   - Portal de Azure > App Service > Monitoring > Log stream

3. **Verifica la configuración de CORS**:
   - Usa las herramientas de desarrollador del navegador
   - Revisa las cabeceras de respuesta

4. **Reinicia la App Service** si es necesario

## Archivos Modificados

- `backend/main.py`: Configuración de CORS mejorada
- `configure-cors-azure.sh`: Script de configuración para Azure
- `test-cors-configuration.js`: Script de prueba automatizado
- `CORS_TROUBLESHOOTING.md`: Esta documentación

## Notas Importantes

- Los cambios en `main.py` son compatibles con desarrollo local
- La configuración es flexible y se adapta automáticamente al entorno
- Se mantiene la seguridad al especificar orígenes permitidos explícitamente
