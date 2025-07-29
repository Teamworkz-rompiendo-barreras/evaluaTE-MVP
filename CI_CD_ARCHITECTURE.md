# Arquitectura CI/CD - EvaluaTE MVP

## Descripción General

Este proyecto utiliza una arquitectura de CI/CD profesional con workflows separados para frontend y backend, optimizados para Azure.

## Estructura de Workflows

### 1. Frontend Deployment (`frontend-deploy.yml`)
- **Propósito**: Build y deploy del frontend React a Azure Static Web Apps
- **Trigger**: Push a `main` y Pull Requests
- **Arquitectura**:
  - Job 1: Build & Test (con cache de npm)
  - Job 2: Deploy (solo en push a main)
  - Job 3: Cleanup (cierre de PR environments)

### 2. Backend Deployment (`main_evaluador-backend.yml`)
- **Propósito**: Build y deploy del backend Node.js a Azure App Service
- **Trigger**: Push a `main` y manual dispatch
- **Arquitectura**:
  - Job 1: Build (con cache de npm)
  - Job 2: Deploy (con artifacts)

### 3. CI Backend (`ci.yml`)
- **Propósito**: Validación continua del backend
- **Trigger**: Push a `main` y Pull Requests

### 4. Workflows Deprecados
- **`azure-static-web-apps-yellow-mud-0b6281c1e.yml`**: Eliminado para evitar conflictos
- **`deploy-azure.yml`**: Deshabilitado, reemplazado por `main_evaluador-backend.yml`

## Características Profesionales

### ✅ Optimizaciones Implementadas
- **Cache de dependencias**: Uso de `actions/setup-node` con cache de npm
- **Artifacts**: Separación de build y deploy para mejor control
- **Working directories**: Uso correcto de directorios de trabajo
- **Error handling**: Manejo robusto de comandos opcionales
- **Retention policies**: Limpieza automática de artifacts

### ✅ Seguridad
- **Secrets management**: Uso de GitHub Secrets para credenciales
- **Permissions**: Configuración mínima de permisos necesarios
- **No hardcoded secrets**: Todas las credenciales están en secrets

### ✅ Mantenibilidad
- **Workflows separados**: Frontend y backend independientes
- **Documentación**: Este archivo y comentarios en código
- **Versioning**: Uso de versiones específicas de actions

## Configuración de Entornos

### Azure Static Web Apps (Frontend)
- **URL**: Configurada en `nuevo-frontend/staticwebapp.config.json`
- **API URL**: Apunta al backend de Azure App Service
- **Build command**: `npm run build`
- **Output**: `dist/`

### Azure App Service (Backend)
- **Runtime**: Node.js 20.x
- **Build**: TypeScript compilation
- **Deployment**: ZIP artifact con archivos compilados

## Troubleshooting

### Problemas Comunes
1. **Artifact not found**: Verificar que el build job complete exitosamente
2. **Package.json not found**: Asegurar que working-directory esté configurado
3. **Build failures**: Revisar logs de npm ci y build steps

### Logs y Debugging
- Todos los workflows incluyen pasos de verificación
- Artifacts se retienen por 1 día para debugging
- Logs detallados en GitHub Actions

## Mejoras Futuras

- [ ] Implementar testing de integración
- [ ] Agregar análisis de seguridad (SAST)
- [ ] Implementar deployment canary
- [ ] Agregar monitoreo de performance
- [ ] Implementar rollback automático 