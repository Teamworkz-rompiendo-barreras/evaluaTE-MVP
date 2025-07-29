# 🚀 Configuración de Azure OpenAI para EvaluaTE

Esta guía te ayudará a configurar Azure OpenAI correctamente para que la aplicación pueda generar informes personalizados con IA.

## 📋 Requisitos Previos

- Una cuenta de Microsoft Azure
- Acceso a Azure OpenAI Service
- Python 3.8+ instalado

## 🔧 Paso a Paso: Configuración de Azure OpenAI

### 1. Crear Recurso de Azure OpenAI

1. Ve a [Azure Portal](https://portal.azure.com)
2. Busca "Azure OpenAI" en la barra de búsqueda
3. Selecciona "Azure OpenAI" y haz clic en "Crear"
4. Completa la información básica:
   - **Suscripción**: Selecciona tu suscripción
   - **Grupo de recursos**: Crea uno nuevo o usa uno existente
   - **Región**: Selecciona una región cercana (ej: West Europe)
   - **Nombre**: Dale un nombre descriptivo (ej: `evaluate-openai`)
   - **Plan de tarifa**: Selecciona "Standard S0" (suficiente para desarrollo)
5. Haz clic en "Revisar + crear" y luego "Crear"

### 2. Obtener Credenciales

Una vez creado el recurso:

1. Ve al recurso de Azure OpenAI
2. En el menú lateral, ve a **"Keys and Endpoint"**
3. Copia:
   - **Key 1** (será tu `AZURE_OPENAI_API_KEY`)
   - **Endpoint** (será tu `AZURE_OPENAI_ENDPOINT`)

### 3. Crear Deployment de Modelo

1. En el menú lateral, ve a **"Model deployments"**
2. Haz clic en **"Create"**
3. Completa la información:
   - **Deployment name**: Usa un nombre simple (ej: `gpt-35-turbo`)
   - **Model**: Selecciona uno de estos modelos:
     - `gpt-35-turbo` (recomendado para desarrollo - más económico)
     - `gpt-4` (más potente, más costoso)
     - `gpt-4o` (balanceado)
   - **Model version**: Selecciona la versión más reciente
4. Haz clic en **"Create"**

### 4. Configurar Variables de Entorno

1. En la carpeta `backend`, copia el archivo de ejemplo:
   ```bash
   cp env.example .env
   ```

2. Edita el archivo `.env` y actualiza las variables:
   ```env
   # Azure OpenAI Configuration
   AZURE_OPENAI_API_KEY=tu_api_key_real_aqui
   AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com
   AZURE_OPENAI_DEPLOYMENT=gpt-35-turbo
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   
   # Configuración del backend
   PORT=8000
   HOST=0.0.0.0
   
   # Configuración de CORS
   ALLOWED_ORIGINS=http://localhost:3005,http://localhost:3006,http://localhost:5173
   ```

### 5. Verificar Configuración

Ejecuta el script de verificación:

```bash
cd backend
python setup_azure_openai.py
```

Este script verificará:
- ✅ Que el archivo `.env` existe
- ✅ Que las variables están configuradas
- ✅ Que la conexión con Azure OpenAI funciona
- ✅ Que el deployment está disponible

## 🧪 Probar la Configuración

Una vez configurado, puedes probar que todo funciona:

1. Inicia el backend:
   ```bash
   cd backend
   python main.py
   ```

2. Ve a `http://localhost:8000/docs` para ver la documentación de la API

3. Prueba el endpoint `/api/informe-ia` con datos de ejemplo

## 🔍 Solución de Problemas

### Error: "DeploymentNotFound"

**Síntomas**: Error 404 con mensaje "The API deployment for this resource does not exist"

**Solución**:
1. Verifica que el deployment existe en Azure Portal
2. Asegúrate de que el nombre en `.env` coincida exactamente
3. Espera unos minutos si acabas de crear el deployment

### Error: "Unauthorized"

**Síntomas**: Error 401 o 403

**Solución**:
1. Verifica que la API Key sea correcta
2. Asegúrate de que tienes permisos para usar el servicio
3. Verifica que el endpoint sea correcto

### Error: "Rate limit exceeded"

**Síntomas**: Error 429

**Solución**:
1. Espera unos minutos antes de hacer otra petición
2. Considera actualizar el plan de tarifa si necesitas más capacidad

### Error: "Timeout"

**Síntomas**: La petición tarda demasiado

**Solución**:
1. El prompt puede ser muy largo, considera acortarlo
2. Verifica la conexión a internet
3. Intenta con un modelo más rápido (gpt-35-turbo)

## 💰 Costos

- **gpt-35-turbo**: ~$0.002 por 1K tokens (muy económico)
- **gpt-4**: ~$0.03 por 1K tokens (más costoso)
- **gpt-4o**: ~$0.005 por 1K tokens (balanceado)

Un informe típico usa entre 2000-4000 tokens, por lo que el costo por informe es muy bajo.

## 🔒 Seguridad

- Nunca compartas tu API Key
- No subas el archivo `.env` a repositorios públicos
- Usa variables de entorno en producción
- Considera usar Azure Key Vault para mayor seguridad

## 📞 Soporte

Si tienes problemas:

1. Ejecuta `python setup_azure_openai.py` para diagnóstico
2. Verifica los logs del backend
3. Consulta la documentación de Azure OpenAI
4. Contacta con soporte de Azure si es necesario

---

¡Con esta configuración, tu aplicación estará lista para generar informes personalizados con IA! 🎉