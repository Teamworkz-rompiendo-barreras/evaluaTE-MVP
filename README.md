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

Una vez que el servidor de desarrollo de Vite esté en marcha podrás acceder a la aplicación en [http://localhost:5173](http://localhost:5173).

### ¿Dónde puedo ver el informe con los cambios?

El informe que muestra los datos personales actualizados está disponible en la ruta `/resultados` del frontend. Puedes abrirlo directamente en tu navegador cuando el servidor esté en ejecución:

```
http://localhost:5173/resultados
```

Si prefieres seguir el flujo completo de la aplicación, navega primero a `/register/contact` para rellenar los datos del candidato, continúa con `/register/preferences`, completa los minijuegos en `/games`, sube un CV en `/upload-cv` y, finalmente, accede a `/resultados` para revisar el informe final.

## Pruebas

Los tests del frontend están escritos en TypeScript y se ejecutan con [`tsx`](https://github.com/esbuild-kit/tsx), por lo que no es necesario compilar previamente los archivos.

```bash
cd nuevo-frontend
npm test
```

## Despliegue

Consulta la guía consolidada en `README_DEPLOY.md`.
# Test deployment
