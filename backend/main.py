# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import sqlalchemy
import re

from db import database
from generate_report import generar_informe as generar_informe_ia

app = FastAPI()

# Habilitar CORS desde cualquier origen (solo para pruebas)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos que esperamos en POST /api/generar-informe
class DatosInforme(BaseModel):
    nombre: str
    apellidos: str
    email: str
    whatsapp: str
    discapacidad: str = ""
    tipo: str         = ""
    puesto: str       = ""
    jornada: str      = ""
    disponibilidad: str = ""
    traslado: str     = ""
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

# Definimos la tabla "informes" (debe coincidir con la que tienes en PostgreSQL)
metadata = sqlalchemy.MetaData()
informes = sqlalchemy.Table(
    "informes",
    metadata,
    sqlalchemy.Column("id",         sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nombre",     sqlalchemy.String(100)),
    sqlalchemy.Column("apellidos",  sqlalchemy.String(100)),
    sqlalchemy.Column("email",      sqlalchemy.String(150)),
    sqlalchemy.Column("whatsapp",   sqlalchemy.String(20)),
    sqlalchemy.Column("resumen",    sqlalchemy.Text),
    sqlalchemy.Column("fortalezas", sqlalchemy.Text),
    sqlalchemy.Column("areas_mejora",  sqlalchemy.Text),
    sqlalchemy.Column("orientacion",   sqlalchemy.Text),
    sqlalchemy.Column("conclusion",    sqlalchemy.Text),
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

    # Construir un texto que incluya TODOS los campos en un bloque “perfil”:
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

    # Llamamos a la IA (generate_report.py) para que devuelva un bloque de texto con delimitadores:
    texto_completo = generar_informe_ia(perfil)

    # Ahora parseamos “texto_completo” usando expresiones regulares para extraer cada sección
    # Buscamos los delimitadores: ---SECCIÓN-1---, ---SECCIÓN-2---, ..., ---SECCIÓN-5---
    partes = re.split(r"---SECCIÓN-\d+---", texto_completo)

    # re.split produce una lista donde:
    #   partes[0] es texto antes de “---SECCIÓN-1---” (normalmente estará vacío)
    #   partes[1] es TODO lo que vaya entre “---SECCIÓN-1---” y “---SECCIÓN-2---” → Resumen
    #   partes[2] → texto entre “---SECCIÓN-2---” y “---SECCIÓN-3---” → Fortalezas
    #   partes[3] → texto entre “---SECCIÓN-3---” y “---SECCIÓN-4---” → Oportunidades de mejora
    #   partes[4] → texto entre “---SECCIÓN-4---” y “---SECCIÓN-5---” → Orientación
    #   partes[5] → texto después de “---SECCIÓN-5---” → Conclusión

    resumen     = partes[1].strip() if len(partes) > 1 else ""
    fortalezas  = []
    areas_mejora= []
    orientacion = ""
    conclusion  = ""

    # “Fortalezas” suelen ir con asteriscos (*) en una línea cada una. 
    # Convertimos cada línea que empiece con “*” (o “-”) en un ítem de lista:
    if len(partes) > 2:
        for linea in partes[2].splitlines():
            linea = linea.strip()
            if linea.startswith("*") or linea.startswith("-"):
                fortalezas.append(linea.lstrip("*- ").strip())

    # “Oportunidades de mejora” están en partes[3]
    if len(partes) > 3:
        for linea in partes[3].splitlines():
            linea = linea.strip()
            if linea.startswith("*") or linea.startswith("-"):
                areas_mejora.append(linea.lstrip("*- ").strip())

    # “Orientación laboral” está en partes[4]
    if len(partes) > 4:
        orientacion = partes[4].strip()

    # “Conclusión” está en partes[5]
    if len(partes) > 5:
        conclusion = partes[5].strip()

    # Preparamos el objeto 'informe' para devolver a Frontend y para guardar en BD
    informe = {
        "nombre":     datos_dict["nombre"],
        "apellidos":  datos_dict["apellidos"],
        "email":      datos_dict["email"],
        "whatsapp":   datos_dict["whatsapp"],
        "resumen":    resumen,
        "fortalezas": fortalezas,
        "areas_mejora": areas_mejora,
        "orientacion": orientacion,
        "conclusion":  conclusion,
    }

    # Guardar en la base de datos (tabla “informes”)
    query = informes.insert().values(
        nombre     = informe["nombre"],
        apellidos  = informe["apellidos"],
        email      = informe["email"],
        whatsapp   = informe["whatsapp"],
        resumen    = informe["resumen"],
        fortalezas = ", ".join(informe["fortalezas"]),
        areas_mejora  = ", ".join(informe["areas_mejora"]),
        orientacion   = informe["orientacion"],
        conclusion    = informe["conclusion"],
    )
    await database.execute(query)

    return JSONResponse(content={"informe": informe})

# Para ejecutar localmente
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
