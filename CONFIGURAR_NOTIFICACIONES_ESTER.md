# 📧 Configuración de Notificaciones para Ester

## Email de Destino: ester@teamworkz.co

### ⚙️ Configuración Requerida

Para que recibas las notificaciones de feedback en **ester@teamworkz.co**, necesitas configurar las siguientes variables en el archivo `.env` del backend:

```bash
# Configuración de Email para Notificaciones de Feedback
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=tu_email_gmail@gmail.com
EMAIL_PASSWORD=tu_contraseña_de_aplicacion
ADMIN_EMAIL=ester@teamworkz.co
```

### 🔧 Pasos para Configurar

#### 1. **Crear/Editar archivo .env**
En el directorio `backend/`, crea o edita el archivo `.env`:

```bash
cd backend
nano .env
```

#### 2. **Agregar las variables de email**
Añade estas líneas al archivo `.env`:

```bash
# Configuración de Email para Notificaciones de Feedback
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=tu_email_gmail@gmail.com
EMAIL_PASSWORD=tu_contraseña_de_aplicacion
ADMIN_EMAIL=ester@teamworkz.co
```

#### 3. **Configurar Gmail para enviar emails**

**Opción A: Usar tu Gmail personal**
1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Activa la **verificación en 2 pasos**
3. Ve a **Seguridad** → **Verificación en 2 pasos** → **Contraseñas de aplicación**
4. Genera una contraseña para "EvaluaTE"
5. Usa esa contraseña en `EMAIL_PASSWORD`

**Opción B: Usar Gmail de Teamworkz**
1. Si tienes acceso al Gmail de Teamworkz, sigue los mismos pasos
2. Usa el email de Teamworkz en `EMAIL_USER`

### 📧 Tipos de Notificaciones que Recibirás

#### 1. **Notificación Inmediata** (Cada feedback)
- **Asunto**: "🆕 Nuevo Feedback IA - [Útil/No útil]"
- **Contenido**: Rating, comentario, fecha y contexto del usuario
- **Frecuencia**: Cada vez que alguien envía feedback

#### 2. **Resumen Diario** (Una vez al día)
- **Asunto**: "📊 Resumen Diario Feedback IA - [Fecha]"
- **Contenido**: Estadísticas del día, comentarios destacados
- **Frecuencia**: Diario (configurable)

### 🧪 Probar la Configuración

#### Verificar que el sistema funciona:
```bash
cd backend
python -c "
from feedback_notifications import feedback_notifier
print('✅ Sistema configurado para ester@teamworkz.co')
print('📧 Email de destino:', feedback_notifier.admin_email)
"
```

#### Enviar prueba manual:
```bash
cd backend
python -c "
from feedback_notifications import feedback_notifier
feedback_notifier.send_daily_summary()
print('📧 Resumen diario enviado a ester@teamworkz.co')
"
```

### 🔍 Verificar Recepción

1. **Revisar bandeja de entrada** de ester@teamworkz.co
2. **Verificar carpeta de spam** por si acaso
3. **Comprobar logs** del sistema:
   ```bash
   tail -f backend/feedback_summary.log
   ```

### 🚨 Solución de Problemas

#### Si no recibes emails:
1. **Verificar configuración SMTP**:
   ```bash
   cd backend
   python -c "from feedback_notifications import feedback_notifier; print('SMTP configurado:', feedback_notifier.smtp_server)"
   ```

2. **Probar conexión SMTP**:
   ```bash
   cd backend
   python -c "
   import smtplib
   from feedback_notifications import feedback_notifier
   try:
       with smtplib.SMTP(feedback_notifier.smtp_server, feedback_notifier.smtp_port) as server:
           server.starttls()
           server.login(feedback_notifier.email_user, feedback_notifier.email_password)
           print('✅ Conexión SMTP exitosa')
   except Exception as e:
       print('❌ Error SMTP:', str(e))
   "
   ```

3. **Verificar variables de entorno**:
   ```bash
   cd backend
   python -c "
   import os
   from dotenv import load_dotenv
   load_dotenv()
   print('ADMIN_EMAIL:', os.getenv('ADMIN_EMAIL'))
   print('EMAIL_USER:', os.getenv('EMAIL_USER'))
   print('EMAIL_PASSWORD:', 'Configurado' if os.getenv('EMAIL_PASSWORD') else 'Faltante')
   "
   ```

### 📊 Dashboard en Tiempo Real

También puedes monitorear el feedback en tiempo real:
- **URL**: `http://localhost:3000/feedback-dashboard`
- **Actualización**: Automática cada 30 segundos
- **No requiere configuración de email**

### 🔄 Configurar Resumen Diario Automático

Para recibir el resumen diario automáticamente:

```bash
# Editar crontab
crontab -e

# Agregar línea para ejecutar diariamente a las 9:00 AM
0 9 * * * cd /ruta/a/EvaluaTE_MVP_Starter/backend && python send_daily_feedback_summary.py
```

---

**¡Con esta configuración recibirás todas las notificaciones de feedback en ester@teamworkz.co!** 📧✅