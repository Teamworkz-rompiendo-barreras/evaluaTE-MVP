# Despliegue del Frontend en Azure Static Web Apps

## Configuración Actual

El frontend ya está configurado para usar la variable de entorno `VITE_API_URL` que apunta al backend de Azure.

## Pasos para Desplegar

### 1. Configurar Variables de Entorno en Azure Static Web Apps

1. Ve al [Portal de Azure](https://portal.azure.com)
2. Busca tu **Static Web App**
3. Ve a **Configuration > Application settings**
4. Agrega la variable:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://evaluador-backend.azurewebsites.net`

### 2. Desplegar desde GitHub

El frontend se despliega automáticamente cuando haces push a la rama principal.

### 3. Verificar la Configuración

Después del despliegue, verifica que:
- El frontend esté funcionando en tu URL de Azure Static Web Apps
- Las peticiones al backend no den errores de CORS
- La variable `VITE_API_URL` esté configurada correctamente

## Solución de Problemas

### Error de CORS
Si sigues viendo errores de CORS:
1. Verifica que el backend esté desplegado y funcionando
2. Confirma que la URL del backend sea correcta
3. Revisa los logs del backend en Azure

### Variables de Entorno no Funcionan
Si las variables de entorno no se están aplicando:
1. Reinicia la aplicación después de cambiar las variables
2. Verifica que el nombre de la variable sea exactamente `VITE_API_URL`
3. Asegúrate de que el valor sea la URL completa del backend

## URLs de Referencia

- **Frontend**: `https://yellow-mud-0b6281c1e.6.azurestaticapps.net`
- **Backend**: `https://evaluador-backend.azurewebsites.net` 