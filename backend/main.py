from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import sqlalchemy

from db import database
from generate_report import generar_informe as generar_informe_ia

app = FastAPI()

# Habilita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# MODELO DE DATOS
class DatosInforme(BaseModel):
    nombre: str
    apellidos: str
    email: str
    whatsapp: str
    discapacidad: str = ""
    tipo: str = ""
    puesto: str = ""
    jornada: str = ""
    disponibilidad: str = ""
    traslado: str = ""
    minijuego_decisiones_score: str = ""
    minijuego_resolucion_score: str = ""
    minijuego_comunicacion_score: str = ""
    minijuego_adaptabilidad_score: str = ""
    minijuego_tiempo_score: str = ""
    minijuego_equipo_score: str = ""
    minijuego_creatividad_score: str = ""
    minijuego_liderazgo_score: str = ""
    minijuego_pensamiento_score: str = ""
    minijuego_emocional_score: str = ""
    cv_filename: str

# Tabla informes
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

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/api/generar-informe")
async def generar_informe_endpoint(datos: DatosInforme):
    datos_dict = datos.dict()

    # Preparar datos para la generación del informe de IA
    datos_generar = datos_dict.copy()
    datos_generar["ruta_cv"] = (
        f"uploads/{datos_generar['cv_filename']}" if datos_generar.get("cv_filename") else ""
    )
    resultados = [
        f"Toma de decisiones: {datos_generar.get('minijuego_decisiones_score', '')}",
        f"Resolución de problemas: {datos_generar.get('minijuego_resolucion_score', '')}",
        f"Comunicación: {datos_generar.get('minijuego_comunicacion_score', '')}",
        f"Adaptabilidad: {datos_generar.get('minijuego_adaptabilidad_score', '')}",
        f"Gestión del tiempo: {datos_generar.get('minijuego_tiempo_score', '')}",
        f"Trabajo en equipo: {datos_generar.get('minijuego_equipo_score', '')}",
        f"Creatividad: {datos_generar.get('minijuego_creatividad_score', '')}",
        f"Liderazgo: {datos_generar.get('minijuego_liderazgo_score', '')}",
        f"Pensamiento crítico: {datos_generar.get('minijuego_pensamiento_score', '')}",
        f"Inteligencia emocional: {datos_generar.get('minijuego_emocional_score', '')}"
    ]
    datos_generar["resultados_minijuegos"] = ", ".join(resultados)

    texto_generado = generar_informe_ia(datos_generar)

    informe = {
        "nombre": datos_dict["nombre"],
        "apellidos": datos_dict["apellidos"],
        "email": datos_dict["email"],
        "whatsapp": datos_dict["whatsapp"],
        "resumen": texto_generado,
        "fortalezas": [],  # Se actualizarán cuando la IA los genere directamente
        "areas_mejora": [],
        "orientacion": "",
        "conclusion": ""
    }

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

    return JSONResponse(content={"informe": informe})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
