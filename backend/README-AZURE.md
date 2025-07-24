# Despliegue en Azure App Service

Este documento explica cómo desplegar el backend de EvaluaTE en Azure App Service usando GitHub Actions.

## Prerrequisitos

1. **Cuenta de Azure** con suscripción activa
2. **Repositorio en GitHub** con el código del backend
3. **Azure CLI** instalado (opcional, para configuración manual)

## Configuración en Azure

### 1. Crear App Service

1. Ve al [Portal de Azure](https://portal.azure.com)
2. Crea un nuevo **App Service**
3. Configuración recomendada:
   - **Nombre**: `evaluador-backend`
   - **Runtime stack**: `Node.js 18 LTS`
   - **Operating System**: `Linux`
   - **Region**: Cerca de tus usuarios
   - **Pricing Plan**: B1 (básico) o superior

### 2. Configurar Variables de Entorno

En la configuración de tu App Service, ve a **Configuration > Application settings** y agrega:

```
NODE_ENV=production
PORT=8000
PYTHON_VERSION=3.11
```

### 3. Obtener Perfil de Publicación

1. En tu App Service, ve a **Deployment Center**
2. Selecciona **GitHub Actions**
3. Copia el **Publish Profile** (se descargará un archivo)

## Configuración en GitHub

### 1. Agregar Secret

1. Ve a tu repositorio en GitHub
2. **Settings > Secrets and variables > Actions**
3. Crea un nuevo secret llamado `AZURE_WEBAPP_PUBLISH_PROFILE`
4. Pega el contenido del archivo de perfil de publicación descargado

### 2. Configurar Branch

Asegúrate de que tu código esté en la rama `main` o `master`.

## Despliegue Automático

Una vez configurado, cada vez que hagas push a la rama principal, GitHub Actions:

1. Compilará el código TypeScript
2. Instalará las dependencias de Python
3. Creará un paquete de despliegue
4. Desplegará automáticamente a Azure

## Verificación

1. Ve a tu App Service en Azure
2. Verifica que esté funcionando en la URL: `https://evaluador-backend.azurewebsites.net`
3. Revisa los logs en **Log stream** si hay problemas

## Solución de Problemas

### Error de Build
- Revisa los logs de GitHub Actions
- Verifica que todas las dependencias estén en `package.json` y `requirements.txt`

### Error de Runtime
- Revisa los logs de la aplicación en Azure
- Verifica las variables de entorno
- Asegúrate de que los puertos estén configurados correctamente

### Problemas de CORS
- Configura los dominios permitidos en tu aplicación
- Verifica que el frontend esté apuntando a la URL correcta

## Estructura del Despliegue

```
backend/
├── dist/           # Código TypeScript compilado
├── src/            # Código fuente TypeScript
├── main.py         # Servidor Python
├── requirements.txt # Dependencias Python
├── package.json    # Dependencias Node.js
└── uploads/        # Archivos subidos por usuarios
```

## Comandos Útiles

```bash
# Despliegue manual (desde el directorio backend)
bash azure-deploy.sh

# Ver logs en Azure
az webapp log tail --name evaluate-backend --resource-group tu-grupo

# Reiniciar aplicación
az webapp restart --name evaluate-backend --resource-group tu-grupo
```

## Notas Importantes

- El backend maneja tanto Node.js como Python
- Los archivos subidos se almacenan en el directorio `uploads/`
- Las variables de entorno deben configurarse en Azure
- El despliegue es automático con cada push a main/master 