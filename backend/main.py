from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from db import database, informes  # Importa tu conexión y la tabla

app = FastAPI()

# Habilita CORS para tu frontend (localhost, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto a tu dominio en producción
    allow_methods=["*"],
    allow_headers=["*"],
)

# MODELO DE ENTRADA
class DatosInforme(BaseModel):
    nombre: str
    apellidos: str
    email: str
    whatsapp: str

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/api/generar-informe")
async def generar_informe_endpoint(datos: DatosInforme):
    datos_dict = datos.dict()  # Convierte el modelo en un diccionario
    informe = generar_informe(datos_dict)

    # Guardar en la base de datos
    query = informes.insert().values(
        nombre=informe["nombre"],
        apellidos=informe["apellidos"],
        email=informe["email"],
        whatsapp=informe["whatsapp"],
        resumen=informe["resumen"],
        fortalezas=", ".join(informe["fortalezas"]),  # Convierte lista a string
        areas_mejora=", ".join(informe["areas_mejora"]),
        orientacion=informe["orientacion"],
        conclusion=informe["conclusion"]
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

# Para pruebas locales
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
