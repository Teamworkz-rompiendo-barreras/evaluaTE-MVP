from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from db import database  # <--- Importa tu base de datos aquí
import sqlalchemy

app = FastAPI()

# Habilita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# MODELO DE ENTRADA
class DatosInforme(BaseModel):
    nombre: str
    apellidos: str
    email: str
    whatsapp: str

# --- NUEVO: tabla informes ---
metadata = sqlalchemy.MetaData()

informes = sqlalchemy.Table(
    "informes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nombre", sqlalchemy.String(100)),
    sqlalchemy.Column("apellidos", sqlalchemy.String(100)),
    sqlalchemy.Column("email", sqlalchemy.String(150)),
    sqlalchemy.Column("whatsapp", sqlalchemy.String(20)),
    sqlalchemy.Column("resumen", sqlalchemy.Text),
    sqlalchemy.Column("fortalezas", sqlalchemy.Text),
    sqlalchemy.Column("areas_mejora", sqlalchemy.Text),
    sqlalchemy.Column("orientacion", sqlalchemy.Text),
    sqlalchemy.Column("conclusion", sqlalchemy.Text),
)

# --- NUEVO: conectar/desconectar ---
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/api/generar-informe")
async def generar_informe_endpoint(datos: DatosInforme):
    datos_dict = datos.dict()
    informe = generar_informe(datos_dict)

    # --- NUEVO: Guardar en la base de datos ---
    query = informes.insert().values(
        nombre=informe["nombre"],
        apellidos=informe["apellidos"],
        email=informe["email"],
        whatsapp=informe["whatsapp"],
        resumen=informe["resumen"],
        fortalezas=", ".join(informe["fortalezas"]),
        areas_mejora=", ".join(informe["areas_mejora"]),
        orientacion=informe["orientacion"],
        conclusion=informe["conclusion"],
    )
    await database.execute(query)

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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
