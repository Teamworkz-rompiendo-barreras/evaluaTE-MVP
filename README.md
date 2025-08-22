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

## Despliegue

El proyecto está configurado para desplegarse en Azure.
# Deploy trigger - Fri Aug  8 12:23:05 CEST 2025

gunicorn==22.0.0

# Verificando despliegue - Sat Aug 23 00:19:59 CEST 2025
