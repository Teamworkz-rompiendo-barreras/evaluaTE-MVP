from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import sqlalchemy

from db import database
from generate_report import generar_informe as generar_informe_ia

app = FastAPI()

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de entrada
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

# Tabla SQL
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

    # Construir el perfil completo
    perfil = f"""
Nombre: {datos_dict['nombre']} {datos_dict['apellidos']}
Email: {datos_dict['email']}
WhatsApp: {datos_dict['whatsapp']}
Discapacidad: {datos_dict['discapacidad']}
Modalidad: {datos_dict['tipo']}
Puesto deseado: {datos_dict['puesto']}
Jornada: {datos_dict['jornada']}
Disponibilidad: {datos_dict['disponibilidad']}
Traslado: {datos_dict['traslado']}
CV: {datos_dict['cv_filename']}
Resultados de habilidades blandas:
- Toma de decisiones: {datos_dict['minijuego_decisiones_score']}
- Resolución de problemas: {datos_dict['minijuego_resolucion_score']}
- Comunicación: {datos_dict['minijuego_comunicacion_score']}
- Adaptabilidad: {datos_dict['minijuego_adaptabilidad_score']}
- Gestión del tiempo: {datos_dict['minijuego_tiempo_score']}
- Trabajo en equipo: {datos_dict['minijuego_equipo_score']}
- Creatividad: {datos_dict['minijuego_creatividad_score']}
- Liderazgo: {datos_dict['minijuego_liderazgo_score']}
- Pensamiento crítico: {datos_dict['minijuego_pensamiento_score']}
- Inteligencia emocional: {datos_dict['minijuego_emocional_score']}
"""

    # Generar texto del informe
    texto_completo = generar_informe_ia(perfil)

    # Extraer partes del texto
    resumen = texto_completo.split("2.")[0].replace("1. RESUMEN PERSONAL", "").strip()
    fortalezas = []
    mejoras = []
    orientacion = ""
    conclusion = ""

    for linea in texto_completo.splitlines():
        linea = linea.strip()
        if linea.startswith("-") or linea.startswith("•"):
            if "fortaleza" in linea.lower() or "habilidad" in linea.lower():
                fortalezas.append(linea.lstrip("-• ").strip())
            elif "mejora" in linea.lower() or "oportunidad" in linea.lower():
                mejoras.append(linea.lstrip("-• ").strip())
        elif "orientación" in linea.lower():
            orientacion = linea
        elif "conclusión" in linea.lower():
            conclusion = linea

    informe = {
        "nombre": datos_dict["nombre"],
        "apellidos": datos_dict["apellidos"],
        "email": datos_dict["email"],
        "whatsapp": datos_dict["whatsapp"],
        "resumen": resumen,
        "fortalezas": fortalezas,
        "areas_mejora": mejoras,
        "orientacion": orientacion,
        "conclusion": conclusion,
    }

    # Guardar en la base de datos
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

# Ejecutar localmente
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

