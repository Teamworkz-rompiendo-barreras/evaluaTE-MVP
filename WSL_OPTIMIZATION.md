# Optimización de WSL para EvaluaTE

## Problemas Identificados y Soluciones

### 1. Problema de Puertos Incorrectos
**Problema**: El script `app.sh` estaba verificando el puerto 5173 para el frontend, pero Vite estaba configurado para usar el puerto 3005.

**Solución**: 
- Corregido el script para verificar el puerto correcto (3005)
- Actualizada la información mostrada al usuario

### 2. Configuración de Servidor Mejorada
**Problema**: El servidor uvicorn no tenía configuraciones optimizadas para WSL.

**Solución**:
- Agregados timeouts de keep-alive (65s)
- Configurado timeout de graceful shutdown (30s)
- Habilitado access log para mejor monitoreo

### 3. Endpoint de Health Check
**Problema**: No había forma de verificar el estado del servidor de manera programática.

**Solución**:
- Agregado endpoint `/health` para monitoreo
- Incluye timestamp y información de versión
- Permite verificación automática de conectividad

### 4. Script de Monitoreo Automático
**Problema**: No había sistema de detección y recuperación automática de fallos.

**Solución**:
- Creado `monitor.sh` para monitoreo continuo
- Detección automática de servicios caídos
- Reinicio automático después de 3 fallos consecutivos
- Logging de eventos para análisis posterior

### 5. Optimización de WSL
**Problema**: WSL puede tener problemas de rendimiento y memoria.

**Solución**:
- Creado `wsl-optimize.sh` para optimización del sistema
- Ajuste de parámetros de memoria y red
- Configuración de límites del sistema
- Plantilla de configuración `.wslconfig`

## Scripts Disponibles

### app.sh (Script Principal)
```bash
./app.sh start      # Iniciar servicios
./app.sh stop       # Detener servicios
./app.sh restart    # Reiniciar con verificación
./app.sh status     # Mostrar estado
./app.sh check      # Verificar conectividad
./app.sh clean      # Limpiar recursos
```

### monitor.sh (Monitoreo Automático)
```bash
./monitor.sh start  # Iniciar monitoreo automático
./monitor.sh check  # Verificación única
./monitor.sh stats  # Mostrar estadísticas
```

### wsl-optimize.sh (Optimización de WSL)
```bash
./wsl-optimize.sh full    # Optimización completa
./wsl-optimize.sh memory  # Optimizar memoria
./wsl-optimize.sh network # Optimizar red
./wsl-optimize.sh info    # Información del sistema
```

## Configuración Recomendada de WSL

Crear archivo `%USERPROFILE%\.wslconfig` en Windows con:

```ini
[wsl2]
memory=4GB
processors=2
swap=2GB
networkingMode=mirrored
localhostForwarding=true
kernelCommandLine=cgroup_enable=1 cgroup_memory=1 cgroup_enable=cpu
automount.enabled=true
automount.root=/mnt/
automount.options="metadata,umask=22,fmask=11"
```

## Mejoras de Conectividad

### Backend (FastAPI)
- Timeouts optimizados para WSL
- Endpoint de health check
- Configuración CORS mejorada
- Logging detallado

### Frontend (Vite)
- Puerto configurado correctamente (3005)
- Configuración de proxy para desarrollo
- Detección automática de entorno

### Monitoreo
- Verificación cada 30 segundos
- Reinicio automático tras 3 fallos
- Logging de eventos
- Limpieza automática de memoria

## Comandos de Verificación

### Verificar Estado Actual
```bash
./app.sh status
```

### Verificar Conectividad
```bash
./app.sh check
```

### Probar Endpoints
```bash
# Health check del backend
curl http://localhost:8000/health

# Verificar frontend
curl http://localhost:3005
```

### Monitoreo Continuo
```bash
# Iniciar monitor en segundo plano
nohup ./monitor.sh start > monitor.log 2>&1 &

# Ver logs
tail -f monitor.log
```

## Solución de Problemas

### Si el backend no responde:
1. Verificar variables de entorno: `cat backend/.env`
2. Reiniciar servicios: `./app.sh restart`
3. Verificar logs: `tail -f monitor.log`

### Si el frontend no responde:
1. Verificar puerto: `netstat -tlnp | grep 3005`
2. Reiniciar frontend: `cd nuevo-frontend && npm run dev`
3. Verificar dependencias: `npm install`

### Si hay problemas de memoria:
1. Ejecutar limpieza: `./app.sh clean`
2. Optimizar WSL: `./wsl-optimize.sh memory`
3. Reiniciar WSL desde Windows

### Si hay problemas de red:
1. Optimizar red: `./wsl-optimize.sh network`
2. Verificar configuración CORS
3. Reiniciar servicios: `./app.sh restart`

## Recomendaciones Adicionales

1. **Ejecutar optimización completa** al configurar el entorno:
   ```bash
   ./wsl-optimize.sh full
   ```

2. **Iniciar monitoreo automático** en sesiones largas:
   ```bash
   ./monitor.sh start
   ```

3. **Verificar regularmente** el estado del sistema:
   ```bash
   ./wsl-optimize.sh info
   ```

4. **Mantener logs** para análisis de problemas:
   ```bash
   tail -f monitor.log
   ```

## Notas Importantes

- Los scripts requieren permisos de ejecución: `chmod +x *.sh`
- Algunas optimizaciones requieren permisos de sudo
- El monitoreo automático consume recursos mínimos
- Los logs se guardan en `monitor.log` para análisis posterior
- Reiniciar WSL desde Windows puede ser necesario después de optimizaciones 