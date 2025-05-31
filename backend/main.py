from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv

# Carga variables de entorno del archivo .env
load_dotenv()

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

# Crea el engine async
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

app = FastAPI()

# Habilita CORS para tu frontend (localhost, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto a tu dominio en producción
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/generar-informe")
async def generar_informe_endpoint(request: Request):
    datos = await request.json()  # Recibe JSON del frontend
    informe = generar_informe(datos)
    return {"informe": informe}

def generar_informe(datos):
    # Estructura compatible con el frontend
    return {
        "nombre": datos.get("nombre", ""),
        "apellidos": datos.get("apellidos", ""),
        "email": datos.get("email", ""),
        "whatsapp": datos.get("whatsapp", ""),
        "resumen": f"Este es un informe de ejemplo para {datos.get('nombre', '')}. Aquí irá el resumen real.",
        "fortalezas": ["Comunicación", "Resolución de problemas"],
        "areas_mejora": ["Gestión del tiempo"],
        "orientacion": "Se recomienda buscar trabajos en equipo de atención al público.",
        "conclusion": "¡Enhorabuena por tus avances!"
    }

# --- NUEVO ENDPOINT PARA PROBAR LA CONEXIÓN A LA BD ---
@app.get("/ping-db")
async def ping_db():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        return {"ok": True, "postgres_version": version}

# Para pruebas locales
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    