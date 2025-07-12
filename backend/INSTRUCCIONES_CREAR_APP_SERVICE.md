# Crear App Service en Azure - Paso a Paso

## 🔧 Crear el App Service

### 1. Acceder al Portal de Azure
1. Ve a [portal.azure.com](https://portal.azure.com)
2. Inicia sesión con tu cuenta

### 2. Crear Nuevo App Service
1. Haz clic en **"Crear un recurso"** (botón verde)
2. Busca **"App Service"**
3. Selecciona **"App Service"** y haz clic en **"Crear"**

### 3. Configuración Básica
**Pestaña "Básico":**
- **Suscripción**: Selecciona tu suscripción
- **Grupo de recursos**: 
  - Si no tienes uno: **"Crear nuevo"** → Nombre: `evaluate-rg`
  - Si ya tienes uno: Selecciona el existente
- **Nombre**: `evaluate-backend` ⭐ (IMPORTANTE: exactamente este nombre)
- **Publicar**: `Código`
- **Pila en tiempo de ejecución**: `Node.js 18 LTS`
- **Sistema operativo**: `Linux`
- **Región**: Selecciona la más cercana a tus usuarios (ej: West Europe)
- **Plan de App Service**: 
  - **Crear nuevo**
  - **Nombre**: `evaluate-plan`
  - **SKU y tamaño**: `B1` (Básico) o `F1` (Gratuito)

### 4. Configuración Avanzada (Opcional)
**Pestaña "Implementación":**
- **Continuos deployment**: `Habilitado`
- **GitHub Actions**: Selecciona tu repositorio

### 5. Crear
- Haz clic en **"Revisar y crear"**
- Revisa la configuración
- Haz clic en **"Crear"**

## ⚙️ Configurar Variables de Entorno

### 1. Ir a la Configuración
1. Una vez creado, ve a tu App Service
2. En el menú lateral, busca **"Configuración"**
3. Haz clic en **"Configuración"**

### 2. Agregar Variables
En **"Configuración de la aplicación"**, agrega:

| Nombre | Valor |
|--------|-------|
| `NODE_ENV` | `production` |
| `PORT` | `8080` |
| `PYTHON_VERSION` | `3.11` |

### 3. Guardar
- Haz clic en **"Guardar"**
- Confirma el reinicio

## 🔗 Obtener Perfil de Publicación

### 1. Ir a Deployment Center
1. En tu App Service, ve a **"Centro de implementación"**
2. Selecciona **"GitHub Actions"**
3. Haz clic en **"Descargar perfil de publicación"**

### 2. Configurar en GitHub
1. Ve a tu repositorio en GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret**
4. **Name**: `AZURE_WEBAPP_PUBLISH_PROFILE`
5. **Value**: Pega todo el contenido del archivo descargado

## ✅ Verificación

### 1. Verificar que el App Service esté funcionando
- URL: `https://evaluador-backend.azurewebsites.net`
- Debería mostrar una página de bienvenida de Azure

### 2. Verificar logs
- En tu App Service → **"Registros"** → **"Stream de registros"**
- Deberías ver logs de la aplicación

## 🚨 Solución de Problemas

### Error: "El nombre no está disponible"
- Intenta con otro nombre: `evaluate-backend-2024`, `my-evaluate-backend`, etc.

### Error: "No se pudo crear el recurso"
- Verifica que tu suscripción tenga créditos disponibles
- Intenta con un plan gratuito (F1) primero

### Error: "Dominio no encontrado"
- Espera unos minutos después de crear el App Service
- Verifica que el nombre sea exactamente `evaluate-backend`

## 📞 URLs Importantes

- **Portal Azure**: https://portal.azure.com
- **Tu App Service**: https://evaluador-backend.azurewebsites.net (después de crearlo)
- **Frontend**: https://yellow-mud-0b6281c1e.6.azurestaticapps.net 