# 🚀 Despliegue en Azure Web App - EvaluaTE Backend

## 📋 Resumen del Problema

El despliegue anterior falló porque Azure Web App no podía encontrar el punto de entrada correcto para la aplicación FastAPI. Aunque Oryx construyó correctamente el proyecto e instaló todas las dependencias, el despliegue final falló en la fase de ejecución.

## ✅ Solución Implementada

Se han creado múltiples archivos de configuración para asegurar que Azure Web App pueda ejecutar correctamente la aplicación:

### 🔧 Archivos de Configuración Principales

1. **`azure-app-service-config.py`** - Punto de entrada principal
   - Configura el entorno para Azure
   - Importa y ejecuta la aplicación FastAPI
   - Exporta la variable `application` requerida por Azure

2. **`.deployment`** - Comando de inicio para Azure
   - Especifica que Azure debe ejecutar `python azure-app-service-config.py`

3. **`startup.txt`** - Comando de inicio alternativo
   - Comando de inicio en formato de texto plano

4. **`azure.yaml`** - Configuración de Azure
   - Especifica el lenguaje (Python)
   - Define los comandos de construcción
   - Establece el comando de inicio

5. **`web.config`** - Configuración de IIS (si es necesario)
   - Configuración para el handler HTTP Platform

6. **`deploy-config.json`** - Configuración del despliegue
   - Metadatos del proyecto para Azure

## 🚀 Instrucciones de Despliegue

### Opción 1: Despliegue Manual

1. **Descargar el archivo preparado:**
   ```bash
   # El archivo backend-azure-ready.zip ya está preparado
   ```

2. **Subir a Azure Web App:**
   - Ve al portal de Azure
   - Navega a tu Web App "evaluador-backend"
   - Ve a "Deployment Center" → "Manual deployment"
   - Sube el archivo `backend-azure-ready.zip`

### Opción 2: GitHub Actions (Recomendado)

1. **Hacer commit de los cambios:**
   ```bash
   git add .
   git commit -m "Fix Azure deployment configuration"
   git push origin main
   ```

2. **El workflow se ejecutará automáticamente:**
   - GitHub Actions construirá el proyecto
   - Se creará un nuevo ZIP con la configuración correcta
   - Se desplegará automáticamente en Azure

## 🔍 Verificación del Despliegue

### 1. Verificar Logs
- Ve a Azure Portal → Web App → "Log stream"
- Deberías ver mensajes como:
  ```
  🚀 Iniciando EvaluaTE Backend en Azure...
  ✅ Configuración del entorno completada
  🚀 Iniciando EvaluaTE Backend en 0.0.0.0:8000
  ```

### 2. Verificar Endpoints
- La aplicación debería estar disponible en:
  - `https://evaluador-backend-fzbhemgtetfeeme6.spaincentral-01.azurewebsites.net/`
  - `/docs` - Documentación de la API
  - `/health` - Endpoint de salud (si existe)

### 3. Verificar Variables de Entorno
- Asegúrate de que las variables de entorno estén configuradas en Azure:
  - `OPENAI_API_KEY`
  - `AZURE_FORM_RECOGNIZER_ENDPOINT`
  - `AZURE_FORM_RECOGNIZER_KEY`
  - `AZURE_STORAGE_CONNECTION_STRING`

## 🐛 Solución de Problemas

### Error: "Module not found"
- **Causa:** Dependencias no instaladas correctamente
- **Solución:** Verificar que `requirements-azure.txt` esté presente y actualizado

### Error: "Application failed to start"
- **Causa:** Punto de entrada incorrecto
- **Solución:** Verificar que `azure-app-service-config.py` esté presente

### Error: "Port already in use"
- **Causa:** Puerto 8000 ocupado
- **Solución:** Azure asignará automáticamente el puerto correcto

## 📁 Estructura de Archivos

```
backend/
├── azure-app-service-config.py  # ← Punto de entrada principal
├── main.py                      # ← Aplicación FastAPI
├── requirements-azure.txt       # ← Dependencias para Azure
├── .deployment                  # ← Comando de inicio
├── startup.txt                  # ← Comando de inicio alternativo
├── azure.yaml                   # ← Configuración de Azure
├── web.config                   # ← Configuración de IIS
└── deploy-config.json           # ← Configuración del despliegue
```

## 🔄 Flujo de Despliegue

1. **GitHub Actions** construye el proyecto
2. **Oryx** instala las dependencias de Python
3. **Azure Web App** ejecuta `python azure-app-service-config.py`
4. **La aplicación** se inicia en el puerto asignado por Azure
5. **FastAPI** comienza a servir las APIs

## 📞 Soporte

Si el despliegue sigue fallando:

1. Revisa los logs en Azure Portal
2. Verifica que todos los archivos de configuración estén presentes
3. Asegúrate de que las variables de entorno estén configuradas
4. Revisa que la aplicación se pueda importar localmente

## 🎯 Próximos Pasos

1. **Desplegar** usando el archivo `backend-azure-ready.zip`
2. **Verificar** que la aplicación esté funcionando
3. **Configurar** variables de entorno en Azure
4. **Probar** los endpoints de la API
5. **Monitorear** logs y métricas

---

**Nota:** Este archivo ZIP está optimizado para Azure Web App y excluye archivos innecesarios como entornos virtuales y cachés de Python.
