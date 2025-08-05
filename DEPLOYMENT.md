# Guía de Despliegue - EvaluaTE MVP

## Problemas Corregidos

### 1. Problema del Puerto
- **Problema**: Azure Web Apps usa el puerto 8080 por defecto, pero la aplicación estaba configurada para el puerto 8000
- **Solución**: 
  - Actualizado `backend/startup-azure.py` para usar la variable de entorno `PORT`
  - Configurado el backend para escuchar en el puerto que Azure asigna (8080)
  - Actualizado `package.json` para usar `python3` en lugar de `python`

### 2. Problema del Frontend
- **Problema**: El frontend no podía acceder a los datos de `softSkills` porque buscaba en `report?.softSkills` en lugar de `personal.softSkills`
- **Solución**: Corregidas todas las referencias en `ResultadosPage.tsx` para usar `personal.softSkills` directamente

### 3. Problema de Python
- **Problema**: Azure intentaba ejecutar `python startup.py` pero Python no estaba disponible
- **Solución**: 
  - Creado `startup-azure.py` específico para Azure
  - Actualizado `package.json` para usar `python3`
  - Configurado para usar `uvicorn` directamente

## Archivos Modificados

### Backend
- `backend/package.json` - Scripts actualizados para usar `python3`
- `backend/startup-azure.py` - Nuevo script de inicio para Azure
- `backend/startup.py` - Actualizado para usar variable de entorno PORT

### Frontend
- `nuevo-frontend/src/pages/ResultadosPage.tsx` - Corregidas referencias a softSkills
- `nuevo-frontend/src/config/azure-config.ts` - URL del backend actualizada
- `nuevo-frontend/env.production` - Variables de entorno actualizadas

### Scripts
- `deploy-production.sh` - Actualizado para incluir las correcciones

## Instrucciones de Despliegue

### 1. Preparación Local
```bash
# Ejecutar el script de despliegue
./deploy-production.sh
```

### 2. Configuración en Azure

#### Variables de Entorno Requeridas
```bash
AZURE_OPENAI_API_KEY=tu_api_key
AZURE_OPENAI_ENDPOINT=https://tu-endpoint.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
PORT=8080
```

#### Configuración del Backend
- **Runtime**: Python 3.12
- **Startup Command**: `python3 startup-azure.py`
- **Port**: 8080 (manejado automáticamente por Azure)

#### Configuración del Frontend
- **Build Command**: `npm ci && npm run build`
- **Output Directory**: `dist`
- **API URL**: Configurada automáticamente para Azure

### 3. Verificación Post-Despliegue

#### Backend
```bash
# Verificar que el backend responde
curl https://evaluador-backend-fzbhemgtetfeeme6.spaincentral-01.azurewebsites.net/health
```

#### Frontend
```bash
# Verificar que el frontend carga correctamente
curl https://tu-frontend-url.azurestaticapps.net
```

### 4. Monitoreo

#### Logs del Backend
- Revisar logs en Azure Portal > App Service > Logs
- Buscar errores relacionados con Python o uvicorn

#### Logs del Frontend
- Revisar logs en Azure Portal > Static Web App > Logs
- Verificar que las llamadas al backend sean exitosas

## Troubleshooting

### Error: "python: not found"
- **Causa**: Azure no encuentra Python
- **Solución**: Usar `python3` en lugar de `python`

### Error: "Container didn't respond to HTTP pings on port: 8080"
- **Causa**: El backend no está escuchando en el puerto correcto
- **Solución**: Verificar que `startup-azure.py` use la variable de entorno `PORT`

### Error: "CONDICIÓN NO CUMPLIDA - No se ejecuta fetchIaReport"
- **Causa**: Los datos de `softSkills` no están disponibles
- **Solución**: Verificar que los juegos se completen y los datos se guarden en Redux

### Error: "Failed to fetch"
- **Causa**: El frontend no puede conectarse al backend
- **Solución**: Verificar la URL del backend en la configuración de Azure

## Estructura de Archivos de Despliegue

```
backend/
├── main.py                 # Aplicación FastAPI
├── startup-azure.py        # Script de inicio para Azure
├── package.json           # Configuración de Node.js para Azure
├── requirements.txt       # Dependencias de Python
└── venv/                 # Entorno virtual (no incluir en git)

nuevo-frontend/
├── dist/                 # Build de producción
├── src/
│   ├── config/
│   │   ├── api.ts        # Configuración de API
│   │   └── azure-config.ts # Configuración específica de Azure
│   └── pages/
│       └── ResultadosPage.tsx # Página corregida
├── env.production        # Variables de entorno de producción
└── package.json         # Dependencias de Node.js
```

## Notas Importantes

1. **Puerto**: Azure Web Apps usa el puerto 8080 por defecto
2. **Python**: Siempre usar `python3` en Azure
3. **Variables de Entorno**: Configurar todas las variables requeridas en Azure
4. **Logs**: Monitorear logs regularmente para detectar problemas
5. **Testing**: Probar la aplicación completa después del despliegue

## Contacto

Para problemas de despliegue, contactar al equipo de desarrollo con:
- Logs de error completos
- Configuración de variables de entorno
- Pasos para reproducir el problema 