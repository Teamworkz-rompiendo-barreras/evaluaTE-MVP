# Configuración de Azure OpenAI para EvaluaTE

## 🎯 Objetivo
Configurar Azure OpenAI para que tu aplicación pueda:
- Analizar CVs en PDF
- Generar informes de empleabilidad
- Aprender de los datos que reciba (Fine-tuning)

## 📋 Pasos para configurar Azure OpenAI

### 1. Crear recurso Azure OpenAI
1. Ve al portal de Azure
2. Busca "Azure OpenAI" en la barra de búsqueda
3. Haz clic en "Crear" o "Create"
4. Completa la configuración:
   - **Suscripción:** Tu suscripción actual
   - **Grupo de recursos:** El mismo que `evaluador-backend`
   - **Región:** **Spain Central** (importante para evitar problemas de conectividad)
   - **Nombre:** `evaluador-openai`
   - **Plan de precios:** Elige según tu uso

### 2. Configurar modelo base
1. Ve a tu recurso Azure OpenAI
2. Navega a **"Model deployments"** o **"Deployments"**
3. Haz clic en **"Create deployment"**
4. Configura:
   - **Model:** GPT-4o o GPT-4
   - **Deployment name:** `gpt-4o-cv-analysis`
   - **Version:** La más reciente disponible

### 3. Obtener credenciales
1. En tu recurso Azure OpenAI, ve a **"Keys and Endpoint"**
2. Copia:
   - **Key 1** o **Key 2**
   - **Endpoint** (URL completa)

### 4. Configurar variables de entorno
1. Copia el archivo `env.example` como `.env`:
   ```bash
   cp env.example .env
   ```

2. Edita `.env` con tus valores reales:
   ```env
   AZURE_OPENAI_API_KEY=tu_api_key_real
   AZURE_OPENAI_ENDPOINT=https://evaluador-openai.openai.azure.com
   AZURE_OPENAI_DEPLOYMENT=gpt-4o-cv-analysis
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

### 5. Probar la configuración
```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar script de prueba
python test_azure_openai.py
```

## 🔧 Configuración para aprendizaje con datos

### Para Fine-tuning (aprendizaje automático):
1. En Azure OpenAI, ve a **"Fine-tuning"**
2. Crea un nuevo job de fine-tuning
3. Sube tus datos de entrenamiento (CVs analizados, feedback de usuarios)
4. Entrena el modelo personalizado

### Para Document Intelligence (extracción de PDF):
1. Ve a **"Document Intelligence"** en Azure
2. Crea un recurso en la misma región
3. Configura para extraer texto de CVs

## 🚨 Solución de problemas

### Error 404 - Resource not found
- Verifica que el deployment name sea exacto
- Asegúrate de que la región sea Spain Central
- Confirma que el endpoint termine en `.openai.azure.com`

### Variables de entorno vacías
- Verifica que el archivo `.env` esté en la carpeta `backend/`
- Asegúrate de que `python-dotenv` esté instalado
- Reinicia el servidor después de cambiar `.env`

### Error de conectividad
- Verifica que el backend y Azure OpenAI estén en la misma región
- Confirma que no haya restricciones de red

## 📞 Soporte
Si tienes problemas:
1. Ejecuta `python test_azure_openai.py` y comparte el resultado
2. Verifica las variables de entorno con `echo $AZURE_OPENAI_API_KEY`
3. Revisa los logs del backend para errores específicos 