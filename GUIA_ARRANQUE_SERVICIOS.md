# 🚀 Guía para Arrancar Servicios de EvaluaTE MVP

Esta guía te ayudará a arrancar todos los servicios necesarios para el proyecto EvaluaTE MVP.

## 📋 Servicios Disponibles

- **Backend**: API FastAPI en puerto 8000
- **Frontend**: Aplicación React en puerto 3005
- **Entorno Virtual**: Python virtual environment

## 🛠️ Opciones de Arranque

### Opción 1: Script Automático (Recomendado)

```bash
./start_services.sh
```

Este script:
- ✅ Activa automáticamente el entorno virtual
- ✅ Verifica dependencias
- ✅ Arranca backend y frontend en paralelo
- ✅ Maneja la limpieza de procesos al salir

### Opción 2: Script Manual

```bash
./start_manual.sh
```

Este script te permite:
- 🔧 Activar solo el entorno virtual
- 🚀 Arrancar solo el backend
- 🌐 Arrancar solo el frontend
- 📋 Ver instrucciones para arrancar todo manualmente

### Opción 3: Arranque Manual

#### 1. Activar Entorno Virtual

```bash
# Opción A: Si tienes ./venv
source venv/bin/activate

# Opción B: Si tienes ./.venv
source .venv/bin/activate
```

#### 2. Arrancar Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**URLs del Backend:**
- 🌐 API: http://localhost:8000
- 📚 Documentación: http://localhost:8000/docs

#### 3. Arrancar Frontend

```bash
cd nuevo-frontend
npm install
npm run dev
```

**URLs del Frontend:**
- 🌐 Aplicación: http://localhost:3005

## 🔧 Configuración de Puertos

- **Backend**: Puerto 8000
- **Frontend**: Puerto 3005

## 📦 Dependencias Requeridas

### Backend (Python)
- fastapi
- uvicorn
- openai
- pypdf
- pydantic
- dotenv
- Y otras dependencias en `backend/requirements.txt`

### Frontend (Node.js)
- React
- Vite
- TypeScript
- Tailwind CSS
- Y otras dependencias en `nuevo-frontend/package.json`

## 🚨 Solución de Problemas

### Error: Puerto ya en uso
```bash
# Verificar qué proceso usa el puerto
lsof -i :8000  # Para backend
lsof -i :3005  # Para frontend

# Matar el proceso
kill -9 <PID>
```

### Error: Entorno virtual no encontrado
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate
```

### Error: Dependencias faltantes
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd nuevo-frontend
npm install
```

### Error: Node.js no instalado
```bash
# Instalar Node.js (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 📊 Verificación de Servicios

### Backend
```bash
curl http://localhost:8000/
# Debería devolver: {"message": "EvaluaTE MVP Backend API"}
```

### Frontend
```bash
curl http://localhost:3005/
# Debería devolver el HTML de la aplicación React
```

## 🔍 Logs y Debugging

### Backend Logs
Los logs del backend aparecen en la terminal donde ejecutas uvicorn.

### Frontend Logs
Los logs del frontend aparecen en la terminal donde ejecutas npm run dev.

### Verificar Estado de Servicios
```bash
# Verificar procesos en ejecución
ps aux | grep uvicorn
ps aux | grep node
```

## 🛑 Detener Servicios

### Con Scripts Automáticos
Presiona `Ctrl+C` en la terminal donde ejecutaste el script.

### Manualmente
```bash
# Encontrar PIDs
ps aux | grep uvicorn
ps aux | grep node

# Matar procesos
kill -9 <PID_BACKEND>
kill -9 <PID_FRONTEND>
```

## 📝 Notas Importantes

1. **Orden de Arranque**: Primero el backend, luego el frontend
2. **Entorno Virtual**: Siempre activar antes de arrancar el backend
3. **Puertos**: Verificar que los puertos 8000 y 3005 estén libres
4. **Dependencias**: Instalar dependencias antes del primer arranque
5. **Variables de Entorno**: Asegúrate de tener configurado el archivo `.env` en el backend

## 🆘 Soporte

Si tienes problemas:
1. Verifica que todos los puertos estén libres
2. Asegúrate de que el entorno virtual esté activado
3. Revisa que todas las dependencias estén instaladas
4. Consulta los logs de error en las terminales

¡Listo para arrancar! 🚀 