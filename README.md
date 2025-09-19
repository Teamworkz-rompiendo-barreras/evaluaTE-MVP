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

Los tests del frontend están escritos en TypeScript y se ejecutan con [`tsx`](https://github.com/esbuild-kit/tsx), por lo que no es necesario compilar previamente los archivos.

```bash
cd nuevo-frontend
npm test
```

## Despliegue

Consulta la guía consolidada en `README_DEPLOY.md`.
