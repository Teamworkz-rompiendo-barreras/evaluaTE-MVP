# 🔧 Guía Completa: Configuración de Azure OpenAI

## 🎯 **Objetivo**

Configurar Azure OpenAI para que la aplicación genere informes de empleabilidad personalizados con IA avanzada.

## ✅ **Estado Actual**

- ✅ **Backend funcionando** sin Azure OpenAI (modo de prueba)
- ✅ **Frontend conectado** y recibiendo datos
- ✅ **CI/CD optimizado** y funcionando
- ⚠️ **Azure OpenAI** pendiente de configuración

---

## 🚀 **PASO 1: Crear Recurso Azure OpenAI**

### **1.1 Acceder al Portal de Azure**
1. Ve a [https://portal.azure.com](https://portal.azure.com)
2. Inicia sesión con tu cuenta de Azure

### **1.2 Crear el Recurso**
1. Busca "Azure OpenAI" en la barra de búsqueda
2. Selecciona "Azure OpenAI"
3. Haz clic en "Crear"
4. Completa la información:
   - **Suscripción**: Tu suscripción de Azure
   - **Grupo de recursos**: Usa uno existente o crea uno nuevo
   - **Región**: Elige la más cercana (ej: West Europe)
   - **Nombre**: `evaluador-openai` (o el que prefieras)
   - **Plan de precios**: Elige "Standard S0" (más económico)

### **1.3 Esperar la Creación**
- El proceso puede tomar 5-10 minutos
- Recibirás una notificación cuando esté listo

---

## 🔑 **PASO 2: Obtener Credenciales**

### **2.1 Obtener API Key**
1. Ve a tu recurso de Azure OpenAI
2. En el menú lateral, ve a **"Keys and Endpoint"**
3. Copia la **"Key 1"** (será tu `AZURE_OPENAI_API_KEY`)

### **2.2 Obtener Endpoint**
1. En la misma página "Keys and Endpoint"
2. Copia el **"Endpoint"** (será tu `AZURE_OPENAI_ENDPOINT`)
3. Debe terminar en `.openai.azure.com`

---

## 🤖 **PASO 3: Crear Deployment**

### **3.1 Acceder a Model Deployments**
1. En tu recurso de Azure OpenAI
2. Ve a **"Model deployments"**
3. Haz clic en **"Create"**

### **3.2 Configurar el Deployment**
1. **Nombre**: `gpt-35-turbo` (o el que prefieras)
2. **Modelo**: Selecciona `gpt-35-turbo` (más económico)
3. **Versión**: Usa la más reciente disponible
4. **Capacidad**: Elige "Standard" (suficiente para pruebas)

### **3.3 Esperar la Creación**
- El deployment se creará en unos minutos
- Anota el nombre exacto del deployment

---

## ⚙️ **PASO 4: Configurar Variables de Entorno**

### **4.1 Crear Archivo .env**
En el directorio `backend/`, crea un archivo `.env`:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=tu_api_key_aqui
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-35-turbo
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Configuración del backend
PORT=8000
HOST=0.0.0.0

# Configuración de CORS
ALLOWED_ORIGINS=http://localhost:3005,http://localhost:3006,http://localhost:5173,https://yellow-mud-0b6281c1e.6.azurestaticapps.net
```

### **4.2 Reemplazar con tus Valores**
- `tu_api_key_aqui`: La API Key que copiaste
- `tu-recurso.openai.azure.com`: Tu endpoint
- `gpt-35-turbo`: El nombre de tu deployment

---

## 🌐 **PASO 5: Configurar en Azure Web App**

### **5.1 Acceder a la Configuración**
1. Ve a tu Azure Web App (`evaluador-backend`)
2. En el menú lateral, ve a **"Configuration"**
3. Haz clic en **"Application settings"**

### **5.2 Agregar Variables**
Agrega estas variables de entorno:

| **Nombre** | **Valor** |
|------------|-----------|
| `AZURE_OPENAI_API_KEY` | Tu API Key |
| `AZURE_OPENAI_ENDPOINT` | Tu Endpoint |
| `AZURE_OPENAI_DEPLOYMENT` | Nombre de tu deployment |
| `AZURE_OPENAI_API_VERSION` | `2024-02-15-preview` |

### **5.3 Guardar y Reiniciar**
1. Haz clic en **"Save"**
2. La aplicación se reiniciará automáticamente

---

## 🧪 **PASO 6: Verificar la Configuración**

### **6.1 Probar el Backend**
```bash
curl https://evaluador-backend-fzbhemgtetfeeme6.spaincentral-01.azurewebsites.net/
```

**Debería devolver:**
```json
{"message": "Bienvenida/o a EvaluaTE MVP", "status": "running"}
```

### **6.2 Probar la IA**
```bash
curl -X POST https://evaluador-backend-fzbhemgtetfeeme6.spaincentral-01.azurewebsites.net/api/informe-ia \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test",
    "fullName": "Usuario de Prueba",
    "softSkills": [
      {"skill": "Comunicación", "score": 85, "level": "alto", "confidence": 90}
    ],
    "completedGames": []
  }'
```

**Debería devolver un informe generado por IA.**

---

## 📊 **PASO 7: Verificar en la Aplicación**

### **7.1 Probar el Frontend**
1. Ve a tu aplicación frontend
2. Completa el proceso de evaluación
3. Verifica que se genere un informe con IA

### **7.2 Verificar Logs**
En Azure Portal, ve a:
- Tu Web App → **"Log stream"**
- Busca mensajes como:
  - `✅ Azure OpenAI configurado correctamente`
  - `🤖 Enviando prompt a Azure OpenAI`

---

## 🔧 **SOLUCIÓN DE PROBLEMAS**

### **Error: "DeploymentNotFound"**
- Verifica que el nombre del deployment sea correcto
- Asegúrate de que el deployment esté creado y activo

### **Error: "Unauthorized"**
- Verifica que la API Key sea correcta
- Asegúrate de que tengas permisos para usar el deployment

### **Error: "Timeout"**
- El prompt puede ser muy largo
- Intenta con menos datos o aumenta el timeout

### **Error: "Endpoint not found"**
- Verifica que el endpoint termine en `.openai.azure.com`
- Asegúrate de que el recurso esté en la región correcta

---

## 💰 **COSTOS ESTIMADOS**

### **Modelo gpt-35-turbo**
- **Entrada**: ~$0.0015 por 1K tokens
- **Salida**: ~$0.002 por 1K tokens
- **Informe típico**: ~2K tokens = ~$0.007 por informe

### **Recomendaciones**
- Usa `gpt-35-turbo` para desarrollo y pruebas
- Considera `gpt-4` solo para producción si necesitas mayor calidad
- Monitorea el uso en Azure Portal

---

## 🎉 **RESULTADO FINAL**

Una vez configurado:

1. ✅ **Backend funcionando** con IA completa
2. ✅ **Informes personalizados** generados por IA
3. ✅ **Análisis avanzado** de CV y habilidades
4. ✅ **Recomendaciones específicas** para neuroinclusión
5. ✅ **Aplicación completamente funcional**

**¡La aplicación estará completamente operativa con IA avanzada!** 