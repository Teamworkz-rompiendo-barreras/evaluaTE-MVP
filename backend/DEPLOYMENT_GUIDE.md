# Guía de Despliegue - Backend EvaluaTE

## 📋 Resumen de Cambios Realizados

### ✅ Problemas Corregidos

1. **Rutas de imágenes corregidas**: El `pdfService.ts` ahora busca las imágenes en múltiples ubicaciones posibles
2. **Versión de OpenAI actualizada**: Se cambió a `2024-02-15-preview` en `iaReportRoute.ts`
3. **Script de copia de assets**: Se creó `copy-assets.js` que se ejecuta automáticamente durante el build
4. **Verificación de dependencias**: Se creó `check-dependencies.js` para verificar canvas y puppeteer
5. **Script de inicio para Azure**: Se creó `azure-startup.sh` para configurar el entorno correctamente

### 📁 Archivos Creados/Modificados

- `backend/src/services/pdfService.ts` - Corregidas las rutas de imágenes
- `backend/src/routes/iaReportRoute.ts` - Actualizada versión de OpenAI
- `backend/copy-assets.js` - Script para copiar assets durante build
- `backend/check-dependencies.js` - Script de verificación de dependencias
- `backend/azure-startup.sh` - Script de inicio para Azure
- `backend/package.json` - Actualizado con nuevos scripts
- `backend/.deployment` - Configurado para usar el script de inicio

## 🚀 Pasos para Desplegar

### 1. Configurar Variables de Entorno en Azure

En Azure App Service > Configuration > Application settings, configurar:

```
AZURE_OPENAI_API_KEY=tu_api_key_aqui
AZURE_OPENAI_ENDPOINT=https://teamworkz-openai.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=tu_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
PORT=8000
```

### 2. Verificar Dependencias Nativas

Azure App Service debe tener las dependencias nativas para `canvas` y `puppeteer`. Si no las tiene:

1. Ir a Azure App Service > Configuration > General settings
2. Cambiar "Stack" a "Node.js" versión 18 o superior
3. En "Startup Command" poner: `bash azure-startup.sh`

### 3. Desplegar el Código

1. Hacer commit de todos los cambios
2. Hacer push a la rama principal
3. Azure debería detectar los cambios y hacer el despliegue automáticamente

### 4. Verificar el Despliegue

1. Ir a Azure App Service > Logs > Log stream
2. Verificar que aparecen los mensajes:
   - "✅ Assets copiados correctamente"
   - "✅ Canvas: OK"
   - "✅ Puppeteer: OK"
   - "✅ Todas las variables de entorno están configuradas"

## 🔧 Comandos Locales Útiles

```bash
# Verificar dependencias
npm run check-deps

# Copiar assets manualmente
npm run copy-assets

# Build completo
npm run build

# Iniciar en desarrollo
npm run dev
```

## 🐛 Solución de Problemas

### Error: "No se pudo cargar la imagen"

1. Verificar que `background.png` y `radarchart.png` están en `backend/src/assets/`
2. Ejecutar `npm run copy-assets` para copiarlos a `dist/`
3. Verificar que se copiaron correctamente en `backend/dist/src/assets/`

### Error: "Canvas: ERROR"

Azure App Service necesita dependencias nativas. Soluciones:

1. **Opción 1**: Usar un contenedor Docker personalizado
2. **Opción 2**: Cambiar a Azure Container Instances
3. **Opción 3**: Usar Azure Functions con Node.js runtime

### Error: "Variables de entorno faltantes"

1. Ir a Azure App Service > Configuration > Application settings
2. Agregar todas las variables requeridas
3. Reiniciar la aplicación

### Error: "Puerto no disponible"

1. Verificar que `PORT=8000` está configurado en Azure
2. Verificar que no hay conflictos con otros servicios
3. Revisar los logs de Azure para más detalles

## 📞 Contacto

Si tienes problemas, revisa:
1. Los logs de Azure App Service
2. El script `check-dependencies.js` localmente
3. Las variables de entorno en Azure 