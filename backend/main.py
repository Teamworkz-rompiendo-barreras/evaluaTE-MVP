from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import sqlalchemy

from db import database
from generate_report import generar_informe as generar_informe_ia

app = FastAPI()

# Habilita CORS para permitir llamadas desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos que espera el endpoint
class DatosInforme(BaseModel):
    nombre: str
    apellidos: str
    email: str
    whatsapp: str

# Definición de la tabla "informes"
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

# Conectar a la base de datos al iniciar la app
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Endpoint principal que recibe los datos y genera el informe
@app.post("/api/generar-informe")
async def generar_informe_endpoint(datos: DatosInforme):
    datos_dict = datos.dict()

    # Construir perfil para enviar a Azure OpenAI
    perfil = f"""
    Nombre: {datos_dict.get('nombre', '')} {datos_dict.get('apellidos', '')}
    Email: {datos_dict.get('email', '')}
    WhatsApp: {datos_dict.get('whatsapp', '')}
    (Aquí podrás añadir resultados del CV y minijuegos)
    """

    texto_generado = generar_informe_ia(perfil)

    # Por ahora usamos todo el texto como resumen y el resto como plantilla vacía
    informe = {
        "nombre": datos_dict.get("nombre", ""),
        "apellidos": datos_dict.get("apellidos", ""),
        "email": datos_dict.get("email", ""),
        "whatsapp": datos_dict.get("whatsapp", ""),
        "resumen": texto_generado,
        "fortalezas": [],
        "areas_mejora": [],
        "orientacion": "",
        "conclusion": ""
    }

    # Guardar informe en base de datos
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

    # Enviar el informe al frontend
    return JSONResponse(content={"informe": informe})

# Ejecutar localmente
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
