# 📊 Guía de Monitoreo de Feedback IA - EvaluaTE

## ¿Cómo estar informada de los feedbacks?

### 🎯 Opciones Disponibles

#### 1. **Dashboard en Tiempo Real** (Recomendado)
- **URL**: `http://localhost:3000/feedback-dashboard`
- **Actualización**: Automática cada 30 segundos
- **Características**:
  - 📊 Estadísticas en tiempo real
  - 📝 Lista de feedbacks recientes
  - 🔍 Detalles completos de cada feedback
  - 📈 Porcentaje de satisfacción
  - 💬 Comentarios frecuentes

#### 2. **Notificaciones por Email** (Automático)
- **Cuándo**: Cada vez que se recibe nuevo feedback
- **Contenido**: Rating, comentario, fecha y contexto del usuario
- **Configuración**: Variables de entorno en `.env`

#### 3. **Resumen Diario por Email** (Automático)
- **Cuándo**: Una vez al día (configurable)
- **Contenido**: Estadísticas del día, comentarios destacados
- **Ejecución**: Script automático o manual

### ⚙️ Configuración del Sistema

#### Variables de Entorno Necesarias
```bash
# Configuración de Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=tu_email@gmail.com
EMAIL_PASSWORD=tu_contraseña_de_aplicacion
ADMIN_EMAIL=tu_email_para_recibir@ejemplo.com
```

#### Configurar Gmail para Notificaciones
1. **Activar verificación en 2 pasos** en tu cuenta de Gmail
2. **Generar contraseña de aplicación**:
   - Ve a Configuración de Google Account
   - Seguridad → Verificación en 2 pasos → Contraseñas de aplicación
   - Genera una contraseña para "EvaluaTE"
3. **Usar esa contraseña** en `EMAIL_PASSWORD`

### 📱 Cómo Usar el Dashboard

#### Acceso al Dashboard
1. Inicia el servidor frontend: `npm run dev`
2. Ve a: `http://localhost:3000/feedback-dashboard`
3. El dashboard se actualiza automáticamente

#### Información Disponible
- **Tarjetas de estadísticas**: Total, Útil, No Útil, % Satisfacción
- **Lista de feedbacks**: Los últimos 10 feedbacks recibidos
- **Detalles**: Click en cualquier feedback para ver información completa
- **Comentarios frecuentes**: Patrones detectados automáticamente

### 📧 Configurar Notificaciones por Email

#### 1. Configurar Variables de Entorno
```bash
# En el archivo .env del backend
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=tu_email@gmail.com
EMAIL_PASSWORD=tu_contraseña_de_aplicacion
ADMIN_EMAIL=tu_email_para_recibir@ejemplo.com
```

#### 2. Probar Configuración
```bash
cd backend
python -c "
from feedback_notifications import feedback_notifier
print('✅ Sistema de notificaciones configurado')
"
```

### 🔄 Resumen Diario Automático

#### Configurar Tarea Programada (Linux/Mac)
```bash
# Editar crontab
crontab -e

# Agregar línea para ejecutar diariamente a las 9:00 AM
0 9 * * * cd /ruta/a/EvaluaTE_MVP_Starter/backend && python send_daily_feedback_summary.py
```

#### Ejecutar Manualmente
```bash
cd backend
python send_daily_feedback_summary.py
```

### 📊 Interpretar las Estadísticas

#### Métricas Clave
- **Total Feedback**: Número total de feedbacks recibidos
- **Útil**: Feedback positivo (👍)
- **No Útil**: Feedback negativo (👎)
- **% Satisfacción**: Porcentaje de feedbacks útiles

#### Alertas Importantes
- **Satisfacción < 70%**: Revisar calidad de informes
- **Muchos "No Útil"**: Analizar comentarios para mejoras
- **Sin feedback**: Verificar que el sistema funciona

### 🛠️ Mantenimiento del Sistema

#### Limpieza Periódica
```bash
# Revisar archivo de feedback
ls -la backend/feedback_ia.json

# Ver tamaño del archivo
du -h backend/feedback_ia.json

# Hacer backup
cp backend/feedback_ia.json backend/feedback_ia_backup_$(date +%Y%m%d).json
```

#### Logs del Sistema
```bash
# Ver logs de notificaciones
tail -f backend/feedback_summary.log

# Ver logs del servidor
tail -f backend/app.log
```

### 🚨 Solución de Problemas

#### Dashboard no carga
1. Verificar que el frontend esté corriendo
2. Comprobar que el backend esté activo
3. Revisar la consola del navegador

#### Emails no llegan
1. Verificar configuración SMTP
2. Comprobar contraseña de aplicación
3. Revisar carpeta de spam
4. Verificar logs del sistema

#### Feedback no se guarda
1. Verificar permisos de escritura en `backend/`
2. Comprobar espacio en disco
3. Revisar logs del servidor

### 📈 Mejoras Futuras

- [ ] **Notificaciones push** en el navegador
- [ ] **Dashboard móvil** responsive
- [ ] **Exportación de datos** a Excel/CSV
- [ ] **Análisis de sentimientos** automático
- [ ] **Alertas personalizadas** por umbrales
- [ ] **Integración con Slack/Discord**

### 📞 Contacto y Soporte

Si tienes problemas con el sistema de monitoreo:

1. **Revisar logs**: `backend/feedback_summary.log`
2. **Verificar configuración**: Variables de entorno
3. **Probar endpoints**: `/api/informe-ia/feedback/stats`
4. **Reiniciar servicios**: Backend y frontend

---

**¡Con este sistema tendrás visibilidad completa de cómo los usuarios perciben los informes de IA y podrás mejorar continuamente la calidad del servicio!** 🎯