# EvaluaTE MVP

Aplicación de evaluación de currículums vitae utilizando inteligencia artificial.

## Estructura del Proyecto

- `backend/` - API REST en Python con FastAPI
- `nuevo-frontend/` - Frontend en React/TypeScript

## Instalación

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend
```bash
cd nuevo-frontend
npm install
```

## Desarrollo

### Backend
```bash
cd backend
python main.py
```

### Frontend
```bash
cd nuevo-frontend
npm run dev
```

## Pruebas

Algunas pruebas dependen de código TypeScript del frontend. Se incluye la versión compilada a JavaScript de `nuevo-frontend/src/config/reportConfig.ts` para que puedan ejecutarse directamente con Node.

Si se modifica el archivo TypeScript, recompílalo antes de correr los tests:

```bash
npx esbuild nuevo-frontend/src/config/reportConfig.ts --platform=node --format=cjs --target=es2019 --outfile=nuevo-frontend/src/config/reportConfig.cjs
```

Luego ejecuta las pruebas:

```bash
# Pruebas a nivel raíz
node test_new_report_format.js
node test_frontend_integration.js

# Pruebas del módulo de configuración del reporte (usa tsx internamente)
cd nuevo-frontend
npm test
```

## Despliegue

El proyecto está configurado para desplegarse en Azure.
# Deploy trigger - Fri Aug  8 12:23:05 CEST 2025

gunicorn==22.0.0

# Verificando despliegue - Sat Aug 23 00:19:59 CEST 2025
# Forzando despliegue - 00:34:48
# Forzando despliegue final - 00:49:14
