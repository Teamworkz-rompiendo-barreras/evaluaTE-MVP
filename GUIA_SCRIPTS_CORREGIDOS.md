# 🚀 Guía de Scripts Corregidos - EvaluaTE

## ✅ **Problemas Solucionados**

Los scripts han sido corregidos para usar el entorno virtual correcto (`.venv` en lugar de `backend/venv`) y ahora funcionan sin errores.

## 📋 **Scripts Disponibles**

### **1. `./activate_env.sh` - Activación Rápida del Entorno**
```bash
./activate_env.sh
```
**Función:** Activa el entorno virtual de forma rápida y segura.
**Uso:** Cuando solo necesitas activar el entorno para trabajar manualmente.

### **2. `./fix_dependencies.sh` - Verificación y Reparación de Dependencias**
```bash
./fix_dependencies.sh
```
**Función:** 
- ✅ Verifica que todas las dependencias estén instaladas
- ✅ Instala dependencias faltantes automáticamente
- ✅ Verifica la estructura de directorios
- ✅ Crea archivo `.env` si no existe
- ✅ Verifica el estado de los servicios

**Uso:** Ejecutar cuando:
- Instalas el proyecto por primera vez
- Agregas nuevas dependencias
- Tienes problemas con importaciones

### **3. `./start_simple.sh` - Inicio Completo de Servicios**
```bash
./start_simple.sh
```
**Función:**
- ✅ Activa el entorno virtual automáticamente
- ✅ Verifica dependencias críticas
- ✅ Inicia el backend (puerto 8000)
- ✅ Inicia el frontend (puerto 5173)
- ✅ Espera a que ambos servicios estén listos
- ✅ Muestra información de acceso

**Uso:** Para iniciar toda la aplicación de una vez.

### **4. `./start_services.sh` - Script Completo (Alternativo)**
```bash
./start_services.sh
```
**Función:** Similar a `start_simple.sh` pero con más verificaciones.
**Uso:** Cuando necesitas verificaciones adicionales.

## 🔧 **Flujo de Trabajo Recomendado**

### **Primera vez o después de cambios:**
```bash
# 1. Verificar y reparar dependencias
./fix_dependencies.sh

# 2. Iniciar servicios
./start_simple.sh
```

### **Uso diario:**
```bash
# Opción 1: Inicio directo
./start_simple.sh

# Opción 2: Activación manual
./activate_env.sh
cd backend && python main.py
```

## 📊 **Información de Acceso**

Una vez iniciados los servicios:
- 🌐 **Frontend:** http://localhost:5173
- 🔧 **Backend:** http://localhost:8000
- 📚 **API Docs:** http://localhost:8000/docs

## 🛑 **Comandos para Detener Servicios**

```bash
# Detener todos los servicios
pkill -f 'python main.py' && pkill -f 'vite'

# O usar Ctrl+C en la terminal donde ejecutaste start_simple.sh
```

## 🔍 **Solución de Problemas**

### **Error: "No se pudo activar el entorno virtual"**
```bash
# Verificar que el entorno virtual existe
ls -la .venv/

# Si no existe, crearlo
python3 -m venv .venv
```

### **Error: "Dependencias faltantes"**
```bash
# Ejecutar verificación completa
./fix_dependencies.sh
```

### **Error: "Puerto ocupado"**
```bash
# Detener procesos en puertos específicos
pkill -f "uvicorn"  # Para puerto 8000
pkill -f "vite"     # Para puerto 5173
```

## ✅ **Verificación de Funcionamiento**

Para verificar que todo funciona correctamente:

```bash
# 1. Verificar entorno virtual
source .venv/bin/activate
python --version

# 2. Verificar dependencias críticas
python -c "import fastapi, openai, dotenv; print('✅ Dependencias OK')"

# 3. Verificar backend
cd backend && python -c "from main import app; print('✅ Backend OK')"

# 4. Verificar frontend
cd ../nuevo-frontend && npm run build
```

## 🎉 **Estado Actual**

- ✅ **Entorno virtual:** `.venv` configurado correctamente
- ✅ **Dependencias:** Todas instaladas y verificadas
- ✅ **Scripts:** Corregidos y funcionando
- ✅ **Pyright:** Configurado para reconocer el entorno correcto
- ✅ **Aplicación:** Lista para usar

**¡Los scripts ahora funcionan sin errores y de manera profesional!** 