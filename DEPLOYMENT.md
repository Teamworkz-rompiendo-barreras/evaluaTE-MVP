# 🚀 Guía de Despliegue a Azure - EvaluaTE MVP

Esta guía te ayudará a desplegar tu aplicación EvaluaTE MVP a Azure de manera profesional y automatizada.

## 📋 Prerrequisitos

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) instalado y configurado
- Cuenta de Azure activa
- Acceso a recursos de Azure OpenAI (para funcionalidades de IA)

## 🔧 Configuración Inicial

### 1. Login en Azure
```bash
az login
```

### 2. Verificar suscripción
```bash
az account show
```

## 🚀 Despliegue Automatizado

### Opción 1: Despliegue Completo (Recomendado)
```bash
./deploy-all.sh
```

Este script desplegará tanto el frontend como el backend automáticamente.

### Opción 2: Despliegue Individual

#### Frontend (Static Web App)
```bash
./deploy-manual.sh
```

#### Backend (Web App)
```bash
./deploy-backend.sh
```

## 🔐 Configuración de Variables de Entorno

### 1. Configurar archivo .env
```bash
cp backend/env.example backend/.env
# Editar backend/.env con tus valores reales
```

### 2. Aplicar configuración a Azure
```bash
./configure-environment.sh
```

## 📊 Verificación del Despliegue

### URLs de las Aplicaciones
- **Frontend**: https://yellow-mud-0b6281c1e.6.azurestaticapps.net
- **Backend**: https://evaluador-backend-fzbhemgtetfeeme6.spaincentral-01.azurewebsites.net

### Verificar Estado
```bash
# Estado del frontend
az staticwebapp show --name evaluador-web --resource-group evaluador-web_group

# Estado del backend
az webapp show --name evaluador-backend --resource-group evaluador-backend_group
```

## 📝 Comandos Útiles

### Logs
```bash
# Logs del backend
az webapp log tail --name evaluador-backend --resource-group evaluador-backend_group

# Logs del frontend
az staticwebapp show --name evaluador-web --resource-group evaluador-web_group
```

### Reiniciar Aplicaciones
```bash
# Reiniciar backend
az webapp restart --name evaluador-backend --resource-group evaluador-backend_group

# Reiniciar frontend (se reinicia automáticamente con cada despliegue)
```

### Actualizar Variables de Entorno
```bash
# Ver variables actuales
az webapp config appsettings list --name evaluador-backend --resource-group evaluador-backend_group

# Actualizar variable específica
az webapp config appsettings set --name evaluador-backend --resource-group evaluador-backend_group --settings NOMBRE_VARIABLE="valor"
```

## 🔄 Flujo de Despliegue

1. **Construir Frontend**: `npm run build` en `nuevo-frontend/`
2. **Crear ZIP**: Archivo comprimido del build
3. **Desplegar Frontend**: Subida a Azure Static Web Apps
4. **Desplegar Backend**: Subida a Azure Web App
5. **Configurar Variables**: Aplicar configuración de entorno
6. **Verificar**: Comprobar funcionamiento de ambas aplicaciones

## 🚨 Solución de Problemas

### Error: "No se pudo obtener el token de acceso"
```bash
az login
az account set --subscription "tu-suscripcion-id"
```

### Error: "Resource not found"
Verificar que los nombres de recursos y grupos coincidan con tu configuración.

### Error: "Build failed"
Verificar que el frontend se construya correctamente localmente:
```bash
cd nuevo-frontend
npm run build
```

### Error: "Variables de entorno no configuradas"
Ejecutar el script de configuración:
```bash
./configure-environment.sh
```

## 📚 Recursos Adicionales

- [Azure Static Web Apps Documentation](https://docs.microsoft.com/en-us/azure/static-web-apps/)
- [Azure Web Apps Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Azure CLI Documentation](https://docs.microsoft.com/en-us/cli/azure/)

## 🎯 Próximos Pasos

1. **Configurar Dominio Personalizado**: Agregar tu dominio a las aplicaciones
2. **Configurar SSL**: Certificados HTTPS automáticos
3. **Monitoreo**: Configurar Azure Application Insights
4. **Escalabilidad**: Configurar reglas de auto-scaling
5. **Backup**: Configurar copias de seguridad automáticas

## 📞 Soporte

Si encuentras problemas durante el despliegue:

1. Verifica los logs de la aplicación
2. Revisa la configuración de Azure
3. Asegúrate de que las variables de entorno estén correctamente configuradas
4. Verifica que los recursos de Azure estén en la misma región

---

**¡Tu aplicación EvaluaTE MVP está ahora desplegada y funcionando en Azure! 🎉**
