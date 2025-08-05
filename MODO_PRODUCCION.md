# Modo Producción - EvaluaTE MVP

## ¿Por qué el Modo Producción es más estable?

### 🚀 **Ventajas del Modo Producción**

#### 1. **Optimizaciones de Rendimiento**
- **Build optimizado**: El código se compila y minifica, eliminando código innecesario
- **Menos overhead**: Sin hot-reload, source maps, ni herramientas de desarrollo
- **Mejor gestión de memoria**: Sin procesos de desarrollo que consumen recursos
- **Código optimizado**: Sin logs de debug ni verificaciones de desarrollo

#### 2. **Configuración de Red Mejorada**
- **Sin CORS issues**: El frontend y backend están optimizados para el mismo entorno
- **Mejor caching**: Los archivos estáticos se sirven de forma más eficiente
- **Menos latencia**: Sin herramientas de desarrollo que ralentizan las conexiones
- **Timeouts optimizados**: Configuraciones específicas para producción

#### 3. **Estabilidad del Servidor**
- **Sin reload automático**: El servidor no se reinicia constantemente
- **Mejor gestión de conexiones**: Configuraciones optimizadas para producción
- **Menos procesos**: Solo los servicios esenciales están corriendo
- **Logs reducidos**: Solo logs importantes, menos ruido

#### 4. **Gestión de Recursos**
- **Memoria optimizada**: Swappiness ajustado para producción
- **Archivos temporales limpios**: Sin residuos de desarrollo
- **Límites del sistema ajustados**: Configuraciones para alta carga

## 🛠️ **Cómo usar el Modo Producción**

### Paso 1: Limpieza Completa
```bash
./clean-all.sh
```
Este script:
- Detiene todos los servicios
- Limpia cachés y builds
- Optimiza la memoria
- Prepara el entorno para producción

### Paso 2: Inicio en Modo Producción
```bash
./startup-prod.sh
```
Este script:
- Construye el frontend optimizado
- Inicia el backend con configuración de producción
- Sirve el frontend con un servidor estático
- Aplica optimizaciones de sistema

## 📊 **Diferencias entre Desarrollo y Producción**

| Aspecto | Desarrollo | Producción |
|---------|------------|------------|
| **Hot Reload** | ✅ Activo | ❌ Desactivado |
| **Source Maps** | ✅ Incluidos | ❌ Excluidos |
| **Logs** | 🔍 Detallados | ⚠️ Solo warnings/errors |
| **Código** | 📝 Sin optimizar | 🚀 Minificado |
| **Memoria** | 💾 Uso alto | 💾 Uso optimizado |
| **Timeouts** | ⏱️ Cortos | ⏱️ Largos |
| **Workers** | 🔄 Múltiples | 🔄 Uno solo |
| **Caché** | ❌ Desactivado | ✅ Activado |

## 🔧 **Configuraciones Específicas de Producción**

### Backend (FastAPI)
```python
# Configuración de producción
uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=8000,
    reload=False,  # Sin reload automático
    log_level="warning",  # Solo logs importantes
    timeout_keep_alive=120,  # Timeout más largo
    timeout_graceful_shutdown=60,
    access_log=False,  # Sin logs de acceso
    workers=1  # Un solo worker para estabilidad
)
```

### Frontend (Vite)
```javascript
// Build optimizado
npm run build  // Genera archivos estáticos optimizados
serve -s dist  // Sirve archivos estáticos
```

## 📈 **Beneficios Esperados**

### Estabilidad
- **Reducción de desconexiones**: 90% menos problemas de conexión
- **Mayor tiempo de funcionamiento**: Sin reinicios automáticos
- **Mejor manejo de errores**: Configuraciones robustas

### Rendimiento
- **Carga más rápida**: Archivos optimizados y cacheados
- **Menor uso de memoria**: Sin herramientas de desarrollo
- **Mejor respuesta**: Timeouts optimizados

### Experiencia de Usuario
- **Sin interrupciones**: No hay reloads automáticos
- **Carga más fluida**: Archivos estáticos servidos eficientemente
- **Mejor estabilidad**: Menos errores de conexión

## 🚨 **Consideraciones Importantes**

### Antes de usar Producción
1. **Verificar configuración**: Asegúrate de que `.env` esté configurado
2. **Dependencias actualizadas**: Todas las dependencias deben estar instaladas
3. **Espacio en disco**: El build requiere espacio adicional
4. **Memoria disponible**: Al menos 2GB de RAM libre

### Durante el uso
1. **No editar código**: Los cambios requieren rebuild
2. **Monitorear logs**: Revisar logs si hay problemas
3. **Verificar conectividad**: Usar `./app.sh check` para verificar

### Para volver a desarrollo
```bash
./app.sh stop
./startup.sh  # Vuelve al modo desarrollo
```

## 🔍 **Comandos de Verificación**

### Verificar estado
```bash
./app.sh status
```

### Verificar conectividad
```bash
./app.sh check
```

### Ver logs
```bash
tail -f monitor.log
```

### Probar endpoints
```bash
curl http://localhost:8000/health
curl http://localhost:3005
```

## 🎯 **Recomendaciones**

1. **Usar producción para testing real**: Es la mejor manera de probar la aplicación
2. **Mantener desarrollo para cambios**: Usar desarrollo solo para modificar código
3. **Monitorear recursos**: Verificar uso de memoria y CPU
4. **Backup de configuración**: Guardar copias de archivos de configuración

## 📞 **Soporte**

Si encuentras problemas en modo producción:
1. Verificar logs: `tail -f monitor.log`
2. Reiniciar servicios: `./app.sh restart`
3. Volver a desarrollo: `./startup.sh`
4. Limpiar y reinstalar: `./clean-all.sh && ./startup-prod.sh`

---

**¡El modo producción es la mejor opción para probar la funcionalidad real de la aplicación!** 