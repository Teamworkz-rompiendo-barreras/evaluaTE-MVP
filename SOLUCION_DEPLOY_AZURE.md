# Solución para Problemas de Deploy en Azure Static Web Apps

## Problemas Identificados

### 1. Error Principal
```
Failed to find a default file in the app artifacts folder (.). Valid default files: index.html,Index.html.
```

### 2. Causas del Problema
- **Configuración incorrecta del workflow**: `app_location` apuntaba al directorio raíz (`"."`) en lugar del directorio con los archivos construidos
- **Rutas de assets incorrectas**: Los assets en `index.html` usaban rutas absolutas (`/assets/...`) en lugar de relativas
- **Falta de archivo de configuración**: El `staticwebapp.config.json` no se copiaba al directorio de deploy

## Soluciones Implementadas

### 1. Corrección del Workflow de GitHub Actions

**Archivo**: `.github/workflows/frontend-deploy.yml`

**Cambios realizados**:
- Cambio de `app_location: "."` a `app_location: "dist"`
- Agregado paso para copiar `staticwebapp.config.json` al directorio dist
- Agregadas verificaciones para asegurar que los archivos necesarios existan
- Mejorado el manejo de artefactos

### 2. Configuración de Vite Actualizada

**Archivo**: `nuevo-frontend/vite.config.js`

**Cambios realizados**:
- Agregado `base: './'` para usar rutas relativas
- Configurado `assetsDir: 'assets'` explícitamente
- Agregadas opciones de `rollupOptions` para mejor control de la salida

### 3. Script de Build Automatizado

**Archivo**: `nuevo-frontend/build-deploy.sh`

**Funcionalidades**:
- Verificación de dependencias
- Limpieza de builds anteriores
- Ejecución de lint y tests
- Build de la aplicación
- Verificación de archivos generados
- Copia automática de configuración

## Verificación de la Solución

### 1. Estructura del Directorio dist
```
dist/
├── index.html                    # ✅ Archivo principal
├── staticwebapp.config.json      # ✅ Configuración de Azure
├── assets/                       # ✅ Directorio de assets
│   ├── index-[hash].js
│   ├── index-[hash].css
│   └── [otros assets]
└── api/                         # ✅ Directorio de API (si existe)
```

### 2. Contenido del index.html
```html
<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>EvalúaTE</title>
    <script type="module" crossorigin src="./assets/index-[hash].js"></script>
    <link rel="stylesheet" crossorigin href="./assets/index-[hash].css">
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
```

**Nota**: Las rutas de assets ahora son relativas (`./assets/...`) en lugar de absolutas (`/assets/...`)

## Cómo Usar

### 1. Build Local
```bash
cd nuevo-frontend
./build-deploy.sh
```

### 2. Deploy Automático
El deploy se ejecuta automáticamente cuando se hace push a la rama `main`.

### 3. Verificación Manual
```bash
# Verificar que el build fue exitoso
ls -la nuevo-frontend/dist/

# Verificar contenido del index.html
head -10 nuevo-frontend/dist/index.html

# Verificar configuración de Azure
cat nuevo-frontend/dist/staticwebapp.config.json
```

## Troubleshooting

### Si el deploy sigue fallando:

1. **Verificar logs del workflow**:
   - Ir a GitHub Actions
   - Revisar el job "Deploy to Azure Static Web Apps"
   - Verificar los pasos de verificación

2. **Verificar archivos localmente**:
   ```bash
   cd nuevo-frontend
   npm run build
   ls -la dist/
   ```

3. **Verificar configuración de Azure**:
   - Asegurar que el token de Azure está configurado correctamente
   - Verificar que la aplicación está configurada en Azure Portal

4. **Problemas comunes**:
   - **Assets no encontrados**: Verificar que las rutas en `index.html` son relativas
   - **Configuración faltante**: Asegurar que `staticwebapp.config.json` está en `dist/`
   - **Permisos**: Verificar que el workflow tiene permisos para acceder a los secrets

## Mejoras Futuras

1. **Optimización de bundle**: Implementar code splitting para reducir el tamaño del bundle
2. **Cache de assets**: Configurar headers de cache apropiados
3. **Monitoreo**: Agregar métricas de performance y errores
4. **CI/CD mejorado**: Agregar más validaciones y tests automatizados

## Contacto

Para problemas adicionales, revisar:
- Logs de GitHub Actions
- Documentación de Azure Static Web Apps
- Issues del repositorio 